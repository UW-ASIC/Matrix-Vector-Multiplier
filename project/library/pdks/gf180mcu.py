"""GlobalFoundries GF180MCU PDK configuration and sizing.

GF 180nm MCU process — available via volare/ciel.
Similar node to sky130 but different characteristics:
- VDD = 3.3V (3V3 devices) or 1.8V (1V8 devices)
- Thicker oxide, higher VTH
- Better analog matching than sky130
"""

import os
from pathlib import Path
from .base import PDKConfig


def _get_pdk_root() -> Path:
    env = os.environ.get("PDK_ROOT")
    if env:
        p = Path(env)
        if p.is_dir():
            return p
    fallback = Path.home() / ".ciel"
    if fallback.is_dir():
        return fallback
    raise FileNotFoundError(
        "PDK_ROOT not found. Set PDK_ROOT env var or install via Ciel (~/.ciel)."
    )


def _lib_path() -> Path:
    return (_get_pdk_root() / "gf180mcuD" / "libs.tech" / "ngspice" /
            "sm141064.ngspice")


class GF180MCU(PDKConfig):
    """GF180MCU 180nm process (3.3V nominal, using 3V3 devices).

    Using 3V3 devices gives more headroom for analog. VDD=3.3V.
    If you want 1.8V operation, switch to the 1V8 device variants.
    """

    def __init__(self):
        super().__init__(
            name="gf180mcu",
            vdd=3.3,
            min_l=0.28,
            nfet="nfet_03v3",
            pfet="pfet_03v3",
            nfet_lvt="nfet_03v3",   # GF180 doesn't have separate LVT
            pfet_hvt="pfet_03v3",
            un_cox=200.0,   # uA/V^2 (thicker oxide → lower Cox)
            up_cox=65.0,    # P/N ratio ~3 (similar to sky130)
            vth_n=0.53,
            vth_p=0.55,
            corners=("tt", "ss", "ff", "sf", "fs"),

            # ── Sizing (W, L) in microns ──
            # GF180: higher VDD compensates for thicker oxide.
            # Vov = VDD - VTH ~ 2.77V (huge) → very strong inversion for switches.
            # Larger min L (0.28um) → bigger devices but better matching.
            sizing={
                # Inverter (min-size: 2:1 P:N for equal drive)
                "inv_n": ("0.56", "0.28"),
                "inv_p": ("1.12", "0.28"),

                # StrongARM comparator
                # Higher VDD → more signal swing, relaxed offset requirement.
                # But thicker oxide → lower gm/W. Size up for speed.
                "comp_input": ("10.0", "0.28"),     # gm/ID~13, large for offset
                "comp_latch_n": ("1.4", "0.28"),
                "comp_latch_p": ("4.2", "0.28"),    # 3x for mobility
                "comp_tail": ("0.56", "0.28"),      # min, VGS=VDD=3.3V
                "comp_reset": ("1.4", "0.28"),

                # Charge DAC switch
                # Higher VDD → much larger Vov → lower Ron for same W.
                # Ron = 1/(un_cox * W/L * Vov) with Vov~2.77V → very low Ron.
                "dac_sw_n": ("1.4", "0.28"),
                "dac_sw_p": ("2.8", "0.28"),

                # Sample-hold switch
                "sh_sw_n": ("0.84", "0.28"),
                "sh_sw_p": ("1.68", "0.28"),

                # IMC crossbar reset
                "xbar_rst_n": ("1.4", "0.28"),
                "xbar_rst_p": ("7.0", "0.28"),

                # IMC crosspoint switch
                "xbar_xpt_n": ("1.4", "0.28"),
                "xbar_xpt_p": ("2.8", "0.28"),

                # ADC mux switch
                "adc_mux_n": ("0.56", "0.28"),
                "adc_mux_p": ("1.68", "0.28"),

                # Muller C-element
                "muller_p_series": ("1.4", "0.28"),
                "muller_n_series": ("0.7", "0.28"),
                "muller_keeper_p": ("0.56", "0.28"),
                "muller_keeper_n": ("0.28", "0.28"),
                "muller_fb_p": ("0.28", "0.56"),
                "muller_fb_n": ("0.28", "0.56"),
            },

            # ── Capacitors ──
            # VDD=3.3V → great SNR. kT/C floor easy to beat.
            # Can use same cap values as sky130 (or slightly smaller).
            caps={
                "c_unit": 50e-15,
                "c_int": 500e-15,
                "c_hold": 200e-15,
                "c_load_delay": 220e-15,
            },

            # ── Delay chain ──
            # Similar fT to sky130 but higher VDD → faster switching.
            delay={
                "n_rst_stages": 8,
                "n_settle_stages": 16,
                "cload": "220f",
            },
        )

    def include_models(self, circuit, corner: str = "tt", temp: int = 27):
        if corner not in self.corners:
            raise ValueError(f"Invalid corner '{corner}', must be one of {self.corners}")
        pdk = _get_pdk_root()
        lib_path = pdk / "gf180mcuD" / "libs.tech" / "ngspice" / "sm141064.ngspice"
        circuit.lib(str(lib_path), corner)
        circuit.temp(temp)

    def include_models_mc(self, circuit, corner: str = "tt", temp: int = 27,
                          seed: int = 0):
        if corner not in self.corners:
            raise ValueError(f"Invalid corner '{corner}', must be one of {self.corners}")
        pdk = _get_pdk_root()
        lib_path = pdk / "gf180mcuD" / "libs.tech" / "ngspice" / "sm141064.ngspice"
        # GF180 MC uses statistical section
        circuit.lib(str(lib_path), f"{corner}_stat")
        circuit.temp(temp)
