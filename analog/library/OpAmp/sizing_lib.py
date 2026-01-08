import numpy as np
from dataclasses import dataclass
from typing import Dict, Optional
from pathlib import Path

# Try to import mosplot for gm/Id method
try:
    from mosplot.plot import load_lookup_table, Mosfet, Expression

    MOSPLOT_AVAILABLE = True
except ImportError:
    MOSPLOT_AVAILABLE = False


# =============================================================================
# Sky130 Configuration
# =============================================================================

SKY130_NFET = "sky130_fd_pr__nfet_01v8"
SKY130_PFET = "sky130_fd_pr__pfet_01v8"

SKY130_MIN_L = 0.13  # μm (130 nm)
LOOKUP_DIR = "../scripts/GMID/sky130_lookup_tables"


# =============================================================================
# Input Parameters (all units in μm, pF, μA, MHz)
# =============================================================================


@dataclass
class Specifications:
    """Target op-amp specifications"""

    gbw: float = 10.0  # Unity gain bandwidth [MHz]
    phase_margin: float = 60  # Phase margin [degrees]
    slew_rate: float = 10.0  # Slew rate [V/μs]
    c_load: float = 1.0  # Load capacitance [pF]
    vdd: float = 1.8  # Supply voltage [V]
    vss: float = 0.0  # Ground [V]


@dataclass
class SquareLawParams:
    """Process parameters for square-law calculations (Sky130 typical)"""

    mu_n_cox: float = 270.0  # NMOS μCox [μA/V²]
    mu_p_cox: float = 70.0  # PMOS μCox [μA/V²]
    vth_n: float = 0.45  # NMOS Vth [V] (Sky130 typical)
    vth_p: float = 0.45  # PMOS |Vth| [V] (Sky130 typical)
    lambda_n: float = 0.1  # NMOS λ [1/V]
    lambda_p: float = 0.15  # PMOS λ [1/V]


@dataclass
class DesignChoices:
    """Designer's choices for operating points and lengths (all lengths in μm)"""

    # Channel lengths [μm] - Sky130 minimum is 0.13μm
    l_m1: float = 0.5  # Input pair (moderate length for matching)
    l_m3: float = 1.0  # Active load (longer for gain)
    l_m5: float = 1.0  # Tail source
    l_m6: float = 0.5  # Output driver
    l_m7: float = 1.0  # Output sink

    # For Square-Law: Overdrive voltages [V]
    vov_m1: float = 0.15
    vov_m3: float = 0.20
    vov_m5: float = 0.20
    vov_m6: float = 0.20
    vov_m7: float = 0.15

    # For gm/Id: Operating points [V^-1]
    gmid_m1: float = 15.0
    gmid_m3: float = 10.0
    gmid_m5: float = 10.0
    gmid_m6: float = 10.0
    gmid_m7: float = 10.0

    # Sizing constraints
    max_width: float = 100.0  # Maximum transistor width [μm]
    min_width: float = 0.42  # Minimum transistor width [μm] (Sky130)


# =============================================================================
# Square-Law Design (all internal calculations in μm, pF, μA, MHz)
# =============================================================================


def design_square_law(
    specs: Specifications, process: SquareLawParams, choices: DesignChoices
) -> Dict:
    """
    Design op-amp using square-law equations.

    All units: μm, pF, μA, MHz, V

    Key equations:
        Id = (1/2) * μCox * (W/L) * Vov²   [μA, with μCox in μA/V²]
        gm = 2*Id / Vov                     [μA/V = μS]
        gm/Id = 2/Vov                       [1/V]
        ro = 1/(λ*Id)                       [MΩ, with Id in μA]
    """
    print("\n" + "=" * 70)
    print("SQUARE-LAW DESIGN (Sky130)")
    print("=" * 70)

    # Compensation capacitor [pF]
    cc = 0.25 * specs.c_load

    # --- Input Pair M1, M2 ---
    vov1 = choices.vov_m1
    gmid_m1 = 2 / vov1  # [1/V]

    # gm1 = 2π * GBW * Cc  [μS], with GBW in MHz and Cc in pF
    # gm [μS] = 2π * f[MHz] * C[pF] = 2π * f * C  (since MHz*pF = 1)
    gm1 = 2 * np.pi * specs.gbw * cc  # [μS]
    id1 = gm1 / gmid_m1  # [μA]
    i_tail = 2 * id1  # [μA]

    # Check slew rate: SR = I_tail / Cc  [V/μs]
    # With I_tail in μA and Cc in pF: SR = I_tail[μA] / Cc[pF] = V/μs
    sr_achieved = i_tail / cc
    if sr_achieved < specs.slew_rate:
        i_tail = specs.slew_rate * cc
        id1 = i_tail / 2
        gm1 = gmid_m1 * id1

    # W/L = 2*Id / (μCox * Vov²)  [unitless]
    # With Id in μA and μCox in μA/V²
    wl_m1 = 2 * id1 / (process.mu_n_cox * vov1**2)
    w_m1 = wl_m1 * choices.l_m1  # [μm]

    # ro = 1/(λ*Id)  [MΩ], with Id in μA and λ in 1/V
    # Actually ro[Ω] = 1/(λ * Id[A]) = 1/(λ * Id[μA] * 1e-6) = 1e6/(λ * Id[μA])
    # So ro[MΩ] = 1/(λ * Id[μA])
    ro1 = 1 / (process.lambda_n * id1)  # [MΩ]

    # --- Active Load M3, M4 ---
    vov3 = choices.vov_m3
    id3 = id1  # [μA]
    wl_m3 = 2 * id3 / (process.mu_p_cox * vov3**2)
    w_m3 = wl_m3 * choices.l_m3  # [μm]
    gm3 = 2 * id3 / vov3  # [μS]
    ro3 = 1 / (process.lambda_p * id3)  # [MΩ]

    # --- Tail Source M5 ---
    vov5 = choices.vov_m5
    id5 = i_tail  # [μA]
    wl_m5 = 2 * id5 / (process.mu_n_cox * vov5**2)
    w_m5 = wl_m5 * choices.l_m5  # [μm]

    # --- First Stage Gain ---
    rout1 = ro1 * ro3 / (ro1 + ro3)  # [MΩ]
    # Av1 = gm1 * rout1, with gm1 in μS and rout1 in MΩ
    # gm[μS] * R[MΩ] = gm[μA/V] * R[MΩ] = (gm * R) [dimensionless]
    av1 = gm1 * rout1

    # --- Output Stage M6, M7 ---
    # gm6 for phase margin: gm6 >= k * gm1 * CL / Cc
    k_pm = 2.2
    gm6_min = k_pm * gm1 * specs.c_load / cc  # [μS]

    # gm6 for RHP zero cancellation: gm6 >= 2 * 2π * GBW * Cc
    gm6_zero = 2 * 2 * np.pi * specs.gbw * cc  # [μS]
    gm6 = max(gm6_min, gm6_zero)

    vov6 = choices.vov_m6
    id6 = gm6 * vov6 / 2  # [μA]
    wl_m6 = 2 * id6 / (process.mu_p_cox * vov6**2)
    w_m6 = wl_m6 * choices.l_m6  # [μm]
    ro6 = 1 / (process.lambda_p * id6)  # [MΩ]

    vov7 = choices.vov_m7
    id7 = id6  # [μA]
    wl_m7 = 2 * id7 / (process.mu_n_cox * vov7**2)
    w_m7 = wl_m7 * choices.l_m7  # [μm]
    ro7 = 1 / (process.lambda_n * id7)  # [MΩ]

    # --- Second Stage Gain ---
    rout2 = ro6 * ro7 / (ro6 + ro7)  # [MΩ]
    av2 = gm6 * rout2

    # --- Apply sizing constraints ---
    def clamp_width(w):
        return max(choices.min_width, min(choices.max_width, w))

    w_m1 = clamp_width(w_m1)
    w_m3 = clamp_width(w_m3)
    w_m5 = clamp_width(w_m5)
    w_m6 = clamp_width(w_m6)
    w_m7 = clamp_width(w_m7)

    # Enforce minimum length
    def clamp_length(l):
        return max(SKY130_MIN_L, l)

    l_m1 = clamp_length(choices.l_m1)
    l_m3 = clamp_length(choices.l_m3)
    l_m5 = clamp_length(choices.l_m5)
    l_m6 = clamp_length(choices.l_m6)
    l_m7 = clamp_length(choices.l_m7)

    # Recalculate W/L after clamping
    wl_m1 = w_m1 / l_m1
    wl_m3 = w_m3 / l_m3
    wl_m5 = w_m5 / l_m5
    wl_m6 = w_m6 / l_m6
    wl_m7 = w_m7 / l_m7

    # --- Performance Estimates ---
    av_total = av1 * av2
    gbw_achieved = gm1 / (2 * np.pi * cc)  # [MHz]
    sr = i_tail / cc  # [V/μs]

    # Second pole: fp2 = gm6 / (2π * CL)  [MHz]
    fp2 = gm6 / (2 * np.pi * specs.c_load)

    # RHP zero: fz = gm6 / (2π * Cc)  [MHz]
    fz = gm6 / (2 * np.pi * cc)

    # Phase margin estimate
    pm = (
        90
        - np.arctan(gbw_achieved / fp2) * 180 / np.pi
        - np.arctan(gbw_achieved / fz) * 180 / np.pi
    )

    # Power consumption [μW]
    power = (i_tail + id6) * specs.vdd

    # --- Results ---
    results = {
        "M1": {
            "W": w_m1,
            "L": l_m1,
            "W/L": wl_m1,
            "Id": id1,
            "gm/Id": gmid_m1,
            "Vov": vov1,
        },
        "M2": {
            "W": w_m1,
            "L": l_m1,
            "W/L": wl_m1,
            "Id": id1,
            "gm/Id": gmid_m1,
            "Vov": vov1,
        },
        "M3": {
            "W": w_m3,
            "L": l_m3,
            "W/L": wl_m3,
            "Id": id3,
            "gm/Id": 2 / vov3,
            "Vov": vov3,
        },
        "M4": {
            "W": w_m3,
            "L": l_m3,
            "W/L": wl_m3,
            "Id": id3,
            "gm/Id": 2 / vov3,
            "Vov": vov3,
        },
        "M5": {
            "W": w_m5,
            "L": l_m5,
            "W/L": wl_m5,
            "Id": id5,
            "gm/Id": 2 / vov5,
            "Vov": vov5,
        },
        "M6": {
            "W": w_m6,
            "L": l_m6,
            "W/L": wl_m6,
            "Id": id6,
            "gm/Id": 2 / vov6,
            "Vov": vov6,
        },
        "M7": {
            "W": w_m7,
            "L": l_m7,
            "W/L": wl_m7,
            "Id": id7,
            "gm/Id": 2 / vov7,
            "Vov": vov7,
        },
        "Cc": cc,  # [pF]
        "Performance": {
            "DC Gain (dB)": 20 * np.log10(av_total),
            "Av1 (dB)": 20 * np.log10(av1),
            "Av2 (dB)": 20 * np.log10(av2),
            "GBW (MHz)": gbw_achieved,
            "Phase Margin (°)": pm,
            "Slew Rate (V/μs)": sr,
            "fp2 (MHz)": fp2,
            "fz (MHz)": fz,
            "I_tail (μA)": i_tail,
            "I_out (μA)": id6,
            "Power (μW)": power,
        },
    }

    _print_results(results)
    return results


# =============================================================================
# gm/Id Design (using mosplot with Sky130)
# =============================================================================


def design_gmid(
    specs: Specifications,
    process: SquareLawParams,
    choices: DesignChoices,
    lookup_dir: str = LOOKUP_DIR,
    vds_nmos: float = 0.9,
    vds_pmos: float = -0.9,
) -> Dict:
    """
    Design op-amp using gm/Id methodology with Sky130 lookup tables.

    All units: μm, pF, μA, MHz

    Args:
        specs: Target specifications
        process: Process parameters (for Vth in swing calc)
        choices: Design choices (lengths in μm, gm/Id values)
        lookup_dir: Path to lookup tables directory
        vds_nmos: VDS for NMOS lookup [V]
        vds_pmos: VDS for PMOS lookup [V]
    """
    if not MOSPLOT_AVAILABLE:
        raise ImportError("mosplot is required. Install with: pip install mosplot")

    print("\n" + "=" * 70)
    print("gm/Id DESIGN (Sky130 PDK)")
    print("=" * 70)

    # Load lookup tables
    nmos_path = Path(lookup_dir) / f"{SKY130_NFET}.npz"
    pmos_path = Path(lookup_dir) / f"{SKY130_PFET}.npz"

    if not nmos_path.exists() or not pmos_path.exists():
        raise FileNotFoundError(
            f"Lookup tables not found in {lookup_dir}\n"
            f"Run your lookup.py script first to generate them."
        )

    print(f"Loading: {nmos_path.name}")
    nmos_lut = load_lookup_table(str(nmos_path))
    print(f"Loading: {pmos_path.name}")
    pmos_lut = load_lookup_table(str(pmos_path))

    # Create Mosfet objects
    nmos = Mosfet(
        lookup_table=nmos_lut, mos=SKY130_NFET, vbs=0.0, vds=vds_nmos, vgs=(0.01, 1.8)
    )
    pmos = Mosfet(
        lookup_table=pmos_lut, mos=SKY130_PFET, vbs=0.0, vds=vds_pmos, vgs=(-1.8, -0.01)
    )

    # Note: Sky130 lookup tables use lengths in MICRONS (already our unit)
    def lookup(mos, length_um, gmid):
        """Get Id/W and gm/gds from lookup table"""
        id_w = mos.interpolate(
            x_expression=mos.length_expression,
            x_value=length_um,
            y_expression=mos.gmid_expression,
            y_value=gmid,
            z_expression=mos.current_density_expression,
        )
        gm_gds = mos.interpolate(
            x_expression=mos.length_expression,
            x_value=length_um,
            y_expression=mos.gmid_expression,
            y_value=gmid,
            z_expression=mos.gain_expression,
        )
        vdsat = mos.interpolate(
            x_expression=mos.length_expression,
            x_value=length_um,
            y_expression=mos.gmid_expression,
            y_value=gmid,
            z_expression=mos.vdsat_expression,
        )
        # id_w from LUT is in A/μm, convert to μA/μm
        return abs(id_w) * 1e6, abs(gm_gds), abs(vdsat)

    # Compensation capacitor [pF]
    cc = 0.25 * specs.c_load

    # --- Input Pair M1, M2 ---
    l_m1 = max(SKY130_MIN_L, choices.l_m1)
    print(f"\nM1,M2: L={l_m1:.2f}μm, gm/Id={choices.gmid_m1:.1f}")
    id_w_1, gm_gds_1, vdsat_1 = lookup(nmos, l_m1, choices.gmid_m1)
    print(
        f"  From LUT: Id/W={id_w_1:.3f}μA/μm, gm/gds={gm_gds_1:.1f}, Vdsat={vdsat_1*1e3:.1f}mV"
    )

    # gm1 = 2π * GBW * Cc  [μS]
    gm1 = 2 * np.pi * specs.gbw * cc
    id1 = gm1 / choices.gmid_m1  # [μA]
    i_tail = 2 * id1

    # Check slew rate
    if i_tail / cc < specs.slew_rate:
        i_tail = specs.slew_rate * cc
        id1 = i_tail / 2
        gm1 = choices.gmid_m1 * id1

    w_m1 = id1 / id_w_1  # [μm]
    wl_m1 = w_m1 / l_m1

    # --- Active Load M3, M4 ---
    l_m3 = max(SKY130_MIN_L, choices.l_m3)
    print(f"\nM3,M4: L={l_m3:.2f}μm, gm/Id={choices.gmid_m3:.1f}")
    id_w_3, gm_gds_3, vdsat_3 = lookup(pmos, l_m3, choices.gmid_m3)
    print(
        f"  From LUT: Id/W={id_w_3:.3f}μA/μm, gm/gds={gm_gds_3:.1f}, Vdsat={vdsat_3*1e3:.1f}mV"
    )

    id3 = id1
    w_m3 = id3 / id_w_3  # [μm]
    wl_m3 = w_m3 / l_m3
    gm3 = choices.gmid_m3 * id3  # [μS]

    # --- Tail Source M5 ---
    l_m5 = max(SKY130_MIN_L, choices.l_m5)
    print(f"\nM5: L={l_m5:.2f}μm, gm/Id={choices.gmid_m5:.1f}")
    id_w_5, gm_gds_5, vdsat_5 = lookup(nmos, l_m5, choices.gmid_m5)
    print(
        f"  From LUT: Id/W={id_w_5:.3f}μA/μm, gm/gds={gm_gds_5:.1f}, Vdsat={vdsat_5*1e3:.1f}mV"
    )

    id5 = i_tail
    w_m5 = id5 / id_w_5  # [μm]
    wl_m5 = w_m5 / l_m5

    # --- First Stage Gain ---
    # ro = (gm/gds) / gm  [MΩ], with gm in μS
    ro1 = gm_gds_1 / gm1  # [MΩ]
    ro3 = gm_gds_3 / gm3  # [MΩ]
    rout1 = ro1 * ro3 / (ro1 + ro3)
    av1 = gm1 * rout1

    # --- Output Stage M6, M7 ---
    k_pm = 2.2
    gm6_min = k_pm * gm1 * specs.c_load / cc
    gm6_zero = 2 * 2 * np.pi * specs.gbw * cc
    gm6 = max(gm6_min, gm6_zero)  # [μS]

    l_m6 = max(SKY130_MIN_L, choices.l_m6)
    print(f"\nM6: L={l_m6:.2f}μm, gm/Id={choices.gmid_m6:.1f}")
    id_w_6, gm_gds_6, vdsat_6 = lookup(pmos, l_m6, choices.gmid_m6)
    print(
        f"  From LUT: Id/W={id_w_6:.3f}μA/μm, gm/gds={gm_gds_6:.1f}, Vdsat={vdsat_6*1e3:.1f}mV"
    )

    id6 = gm6 / choices.gmid_m6  # [μA]
    w_m6 = id6 / id_w_6  # [μm]
    wl_m6 = w_m6 / l_m6

    l_m7 = max(SKY130_MIN_L, choices.l_m7)
    print(f"\nM7: L={l_m7:.2f}μm, gm/Id={choices.gmid_m7:.1f}")
    id_w_7, gm_gds_7, vdsat_7 = lookup(nmos, l_m7, choices.gmid_m7)
    print(
        f"  From LUT: Id/W={id_w_7:.3f}μA/μm, gm/gds={gm_gds_7:.1f}, Vdsat={vdsat_7*1e3:.1f}mV"
    )

    id7 = id6
    w_m7 = id7 / id_w_7  # [μm]
    wl_m7 = w_m7 / l_m7
    gm7 = choices.gmid_m7 * id7  # [μS]

    # --- Apply sizing constraints ---
    def clamp_width(w):
        return max(choices.min_width, min(choices.max_width, w))

    w_m1 = clamp_width(w_m1)
    w_m3 = clamp_width(w_m3)
    w_m5 = clamp_width(w_m5)
    w_m6 = clamp_width(w_m6)
    w_m7 = clamp_width(w_m7)

    # Recalculate W/L after clamping
    wl_m1 = w_m1 / l_m1
    wl_m3 = w_m3 / l_m3
    wl_m5 = w_m5 / l_m5
    wl_m6 = w_m6 / l_m6
    wl_m7 = w_m7 / l_m7

    # --- Second Stage Gain ---
    ro6 = gm_gds_6 / gm6  # [MΩ]
    ro7 = gm_gds_7 / gm7  # [MΩ]
    rout2 = ro6 * ro7 / (ro6 + ro7)
    av2 = gm6 * rout2

    # --- Performance Estimates ---
    av_total = av1 * av2
    gbw_achieved = gm1 / (2 * np.pi * cc)  # [MHz]
    sr = i_tail / cc  # [V/μs]
    fp2 = gm6 / (2 * np.pi * specs.c_load)  # [MHz]
    fz = gm6 / (2 * np.pi * cc)  # [MHz]
    pm = (
        90
        - np.arctan(gbw_achieved / fp2) * 180 / np.pi
        - np.arctan(gbw_achieved / fz) * 180 / np.pi
    )
    power = (i_tail + id6) * specs.vdd  # [μW]

    # --- Results ---
    results = {
        "M1": {
            "W": w_m1,
            "L": l_m1,
            "W/L": wl_m1,
            "Id": id1,
            "gm/Id": choices.gmid_m1,
            "gm/gds": gm_gds_1,
        },
        "M2": {
            "W": w_m1,
            "L": l_m1,
            "W/L": wl_m1,
            "Id": id1,
            "gm/Id": choices.gmid_m1,
            "gm/gds": gm_gds_1,
        },
        "M3": {
            "W": w_m3,
            "L": l_m3,
            "W/L": wl_m3,
            "Id": id3,
            "gm/Id": choices.gmid_m3,
            "gm/gds": gm_gds_3,
        },
        "M4": {
            "W": w_m3,
            "L": l_m3,
            "W/L": wl_m3,
            "Id": id3,
            "gm/Id": choices.gmid_m3,
            "gm/gds": gm_gds_3,
        },
        "M5": {
            "W": w_m5,
            "L": l_m5,
            "W/L": wl_m5,
            "Id": id5,
            "gm/Id": choices.gmid_m5,
            "gm/gds": gm_gds_5,
        },
        "M6": {
            "W": w_m6,
            "L": l_m6,
            "W/L": wl_m6,
            "Id": id6,
            "gm/Id": choices.gmid_m6,
            "gm/gds": gm_gds_6,
        },
        "M7": {
            "W": w_m7,
            "L": l_m7,
            "W/L": wl_m7,
            "Id": id7,
            "gm/Id": choices.gmid_m7,
            "gm/gds": gm_gds_7,
        },
        "Cc": cc,  # [pF]
        "Performance": {
            "DC Gain (dB)": 20 * np.log10(av_total),
            "Av1 (dB)": 20 * np.log10(av1),
            "Av2 (dB)": 20 * np.log10(av2),
            "GBW (MHz)": gbw_achieved,
            "Phase Margin (°)": pm,
            "Slew Rate (V/μs)": sr,
            "fp2 (MHz)": fp2,
            "fz (MHz)": fz,
            "I_tail (μA)": i_tail,
            "I_out (μA)": id6,
            "Power (μW)": power,
        },
    }

    _print_results(results)
    return results


# =============================================================================
# Print Helper
# =============================================================================


def _print_results(results: Dict):
    """Print sizing results in a nice table"""
    print("\n" + "-" * 70)
    print("TRANSISTOR SIZING")
    print("-" * 70)
    print(
        f"{'Name':<6} {'W (μm)':>10} {'L (μm)':>10} {'W/L':>10} {'Id (μA)':>10} {'gm/Id':>8}"
    )
    print("-" * 70)

    for name in ["M1", "M2", "M3", "M4", "M5", "M6", "M7"]:
        m = results[name]
        print(
            f"{name:<6} {m['W']:>10.3f} {m['L']:>10.3f} {m['W/L']:>10.2f} {m['Id']:>10.2f} {m['gm/Id']:>8.1f}"
        )

    print("-" * 70)
    print(f"Cc = {results['Cc']:.3f} pF")

    print("\n" + "-" * 70)
    print("PERFORMANCE ESTIMATES")
    print("-" * 70)
    perf = results["Performance"]
    for key, val in perf.items():
        print(f"  {key:<20} = {val:>10.2f}")
    print("-" * 70)


# =============================================================================
# Get Sizing Function (for external use)
# =============================================================================


def get_sizing(
    method: str = "square_law",
    specs: Specifications = None,
    process: SquareLawParams = None,
    choices: DesignChoices = None,
    lookup_dir: str = LOOKUP_DIR,
) -> Dict:
    """
    Get transistor sizing for use in other scripts.

    All returned values are in μm (widths, lengths) and pF (capacitors).

    Args:
        method: "square_law" or "gmid"
        specs: Target specifications (uses defaults if None)
        process: Process parameters (uses defaults if None)
        choices: Design choices (uses defaults if None)
        lookup_dir: Path to lookup tables (for gm/Id method)

    Returns:
        Dictionary with sizing in μm and pF units, ready for optimizer:
        {
            "XM1_W": float,  # μm
            "XM1_L": float,  # μm
            ...
            "C1_value": float,  # pF
            "_performance": dict  # Performance predictions
        }
    """
    if specs is None:
        specs = Specifications()
    if process is None:
        process = SquareLawParams()
    if choices is None:
        choices = DesignChoices()

    if method == "square_law":
        results = design_square_law(specs, process, choices)
    elif method == "gmid":
        results = design_gmid(specs, process, choices, lookup_dir=lookup_dir)
    else:
        raise ValueError(f"Unknown method: {method}. Use 'square_law' or 'gmid'")

    # Already in μm and pF - no conversion needed!
    sizing = {
        "XM1_W": results["M1"]["W"],
        "XM1_L": results["M1"]["L"],
        "XM2_W": results["M2"]["W"],
        "XM2_L": results["M2"]["L"],
        "XM3_W": results["M3"]["W"],
        "XM3_L": results["M3"]["L"],
        "XM4_W": results["M4"]["W"],
        "XM4_L": results["M4"]["L"],
        "XM5_W": results["M5"]["W"],
        "XM5_L": results["M5"]["L"],
        "XM6_W": results["M6"]["W"],
        "XM6_L": results["M6"]["L"],
        "XM7_W": results["M7"]["W"],
        "XM7_L": results["M7"]["L"],
        "C1_value": results["Cc"],
    }

    # Also include performance predictions
    sizing["_performance"] = results["Performance"]

    return sizing


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":

    # === Define your specifications (all in convenient units) ===
    specs = Specifications(
        gbw=10.0,  # 10 MHz
        phase_margin=60,  # 60°
        slew_rate=10.0,  # 10 V/μs
        c_load=1.0,  # 1 pF
        vdd=1.8,
        vss=0.0,
    )

    # === Process parameters (for square-law) - Sky130 typical ===
    process = SquareLawParams(
        mu_n_cox=270.0,  # μA/V²
        mu_p_cox=70.0,  # μA/V²
        vth_n=0.45,
        vth_p=0.45,
        lambda_n=0.1,
        lambda_p=0.15,
    )

    # === Design choices (all lengths in μm) ===
    choices = DesignChoices(
        # Channel lengths [μm] - Sky130 min is 0.13μm
        l_m1=0.5,  # Input pair
        l_m3=1.0,  # Active load
        l_m5=1.0,  # Tail source
        l_m6=0.5,  # Output driver
        l_m7=1.0,  # Output sink
        # Square-law: Vov [V]
        vov_m1=0.15,
        vov_m3=0.20,
        vov_m5=0.20,
        vov_m6=0.20,
        vov_m7=0.15,
        # gm/Id: operating points [1/V]
        gmid_m1=15.0,
        gmid_m3=10.0,
        gmid_m5=10.0,
        gmid_m6=10.0,
        gmid_m7=10.0,
        # Constraints
        max_width=100.0,  # μm
        min_width=0.42,  # μm (Sky130 minimum)
    )

    # === Run Square-Law Design ===
    sq_results = design_square_law(specs, process, choices)

    # === Get sizing for optimizer ===
    print("\n" + "=" * 70)
    print("SIZING FOR OPTIMIZER")
    print("=" * 70)
    sizing = get_sizing("square_law", specs, process, choices)
    for key, val in sizing.items():
        if key != "_performance":
            print(f"  {key}: {val:.3f}")

    # === Run gm/Id Design (requires lookup tables) ===
    # Uncomment below after running lookup.py to generate tables
    #
    # gmid_results = design_gmid(
    #     specs, process, choices,
    #     lookup_dir="./sky130_lookup_tables",
    #     vds_nmos=0.9,
    #     vds_pmos=-0.9
    # )
