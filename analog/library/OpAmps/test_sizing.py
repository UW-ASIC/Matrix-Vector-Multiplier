from uwasic_optimizer import (
    Optimizer,
    Parameter,
    Target,
    TargetMode,
    Test,
    Environment,
)
from typing import List, Dict
from sizing import get_sizing, Specifications, SquareLawParams, DesignChoices

# =============================================================================
# CONFIGURATION
# =============================================================================

# Template/Default sizing (before optimization)
TEMPLATE_SIZING = {
    "XM1_W": 5.0,  # μm
    "XM1_L": 1.0,  # μm
    "XM2_W": 5.0,  # μm
    "XM2_L": 1.0,  # μm
    "XM3_W": 8.0,  # μm
    "XM3_L": 1.5,  # μm
    "XM4_W": 8.0,  # μm
    "XM4_L": 1.5,  # μm
    "XM5_W": 4.0,  # μm
    "XM5_L": 2.0,  # μm
    "XM6_W": 20.0,  # μm
    "XM6_L": 1.0,  # μm
    "XM7_W": 10.0,  # μm
    "XM7_L": 2.0,  # μm
    "C1_value": 3.0,  # pF
}

# Optimizer settings
CIRCUIT_FILE = "OpAmp_tb.sch"
TEMPLATE_DIR = "template"

# Lookup table directory (for gm/Id method)
LOOKUP_DIR = "../scripts/GMID/sky130_lookup_tables"


# =============================================================================
# TESTS DEFINITION
# =============================================================================

tests: List[Test] = [
    Test(
        name="dc_gain",
        environment=[
            Environment(name="temp", value="27"),
            Environment(name="V1", value="DC 0.9V"),
            Environment(name="V2", value="DC 1.8V"),
            Environment(name="V3", value="DC 0V AC 1mV"),
            Environment(name="V4", value="DC 0.7V"),
            Environment(name="V5", value="DC 0V AC 1mV"),
        ],
        spice_code="""
.ac dec 100 1 1G
meas ac dc_gain_val FIND vdb(vout) AT=10
print dc_gain_val
""",
        description="DC Gain measurement",
    ),
    Test(
        name="gbw",
        environment=[
            Environment(name="temp", value="27"),
            Environment(name="V1", value="DC 0.9V"),
            Environment(name="V2", value="DC 1.8V"),
            Environment(name="V3", value="DC 0V AC 1mV"),
            Environment(name="V4", value="DC 0.7V"),
            Environment(name="V5", value="DC 0V AC 1mV"),
        ],
        spice_code="""
.ac dec 100 1 1G
meas ac dc_gain_for_gbw FIND vdb(vout) AT=10
let gbw_val = 10 * 10^((dc_gain_for_gbw - 0) / 20)
print gbw_val
""",
        description="GBW estimation",
    ),
    Test(
        name="phase_margin",
        environment=[
            Environment(name="temp", value="27"),
            Environment(name="V1", value="DC 0.9V"),
            Environment(name="V2", value="DC 1.8V"),
            Environment(name="V3", value="DC 0V AC 1mV"),
            Environment(name="V4", value="DC 0.7V"),
            Environment(name="V5", value="DC 0V AC 1mV"),
        ],
        spice_code="""
.ac dec 100 1 1G
meas ac phase_rad FIND vp(vout) AT=1e6
let phase_margin_val = (180 + phase_rad * 180 / pi)
print phase_margin_val
""",
        description="Phase margin measurement",
    ),
    Test(
        name="power",
        environment=[
            Environment(name="temp", value="27"),
            Environment(name="V1", value="DC 0.9V"),
            Environment(name="V2", value="DC 1.8V"),
            Environment(name="V3", value="DC 0V AC 1mV"),
            Environment(name="V4", value="DC 0.7V"),
            Environment(name="V5", value="DC 0V AC 1mV"),
        ],
        spice_code="""
.op
let power_val = v(vdd) * (-i(V2))
print power_val
""",
        description="Power consumption",
    ),
    Test(
        name="area",
        environment=[
            Environment(name="temp", value="27"),
            Environment(name="V1", value="DC 0.9V"),
            Environment(name="V2", value="DC 1.8V"),
            Environment(name="V3", value="DC 0V AC 1mV"),
            Environment(name="V4", value="DC 0.7V"),
            Environment(name="V5", value="DC 0V AC 1mV"),
        ],
        spice_code="""
.op
let area_m1 = @m.x1.xm1.msky130_fd_pr__nfet_01v8[w] * @m.x1.xm1.msky130_fd_pr__nfet_01v8[l]
let area_m2 = @m.x1.xm2.msky130_fd_pr__nfet_01v8[w] * @m.x1.xm2.msky130_fd_pr__nfet_01v8[l]
let area_m3 = @m.x1.xm3.msky130_fd_pr__pfet_01v8[w] * @m.x1.xm3.msky130_fd_pr__pfet_01v8[l]
let area_m4 = @m.x1.xm4.msky130_fd_pr__pfet_01v8[w] * @m.x1.xm4.msky130_fd_pr__pfet_01v8[l]
let area_m5 = @m.x1.xm5.msky130_fd_pr__nfet_01v8[w] * @m.x1.xm5.msky130_fd_pr__nfet_01v8[l]
let area_m6 = @m.x1.xm6.msky130_fd_pr__pfet_01v8[w] * @m.x1.xm6.msky130_fd_pr__pfet_01v8[l]
let area_m7 = @m.x1.xm7.msky130_fd_pr__nfet_01v8[w] * @m.x1.xm7.msky130_fd_pr__nfet_01v8[l]
let area_val = area_m1 + area_m2 + area_m3 + area_m4 + area_m5 + area_m6 + area_m7
print area_val
""",
        description="Total transistor area",
    ),
]

targets: List[Target] = [
    Target(metric="DC_GAIN", value=40.0, weight=3.0, mode=TargetMode.Min, unit="dB"),
    Target(metric="GBW", value=5e6, weight=2.0, mode=TargetMode.Min, unit="Hz"),
    Target(
        metric="PHASE_MARGIN",
        value=45.0,
        weight=2.0,
        mode=TargetMode.Min,
        unit="degrees",
    ),
    Target(metric="POWER", value=2e-3, weight=1.0, mode=TargetMode.Max, unit="W"),
    Target(metric="AREA", value=50e-12, weight=1.5, mode=TargetMode.Max, unit="m^2"),
]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def create_parameters(sizing: Dict[str, float]) -> List[Parameter]:
    """Create fixed parameters from sizing dictionary"""
    params = []
    for name in [
        "XM1_W",
        "XM1_L",
        "XM2_W",
        "XM2_L",
        "XM3_W",
        "XM3_L",
        "XM4_W",
        "XM4_L",
        "XM5_W",
        "XM5_L",
        "XM6_W",
        "XM6_L",
        "XM7_W",
        "XM7_L",
        "C1_value",
    ]:
        val = sizing[name]
        params.append(Parameter(name=name, value=val, min_val=val, max_val=val))
    return params


def print_sizing(name: str, sizing: Dict[str, float]):
    """Print sizing in a nice format"""
    print(f"\n{name}:")
    print(
        f"  M1,M2 (input):  W={sizing['XM1_W']:>8.3f}μm  L={sizing['XM1_L']:>6.3f}μm  W/L={sizing['XM1_W']/sizing['XM1_L']:>8.2f}"
    )
    print(
        f"  M3,M4 (load):   W={sizing['XM3_W']:>8.3f}μm  L={sizing['XM3_L']:>6.3f}μm  W/L={sizing['XM3_W']/sizing['XM3_L']:>8.2f}"
    )
    print(
        f"  M5 (tail):      W={sizing['XM5_W']:>8.3f}μm  L={sizing['XM5_L']:>6.3f}μm  W/L={sizing['XM5_W']/sizing['XM5_L']:>8.2f}"
    )
    print(
        f"  M6 (out drv):   W={sizing['XM6_W']:>8.3f}μm  L={sizing['XM6_L']:>6.3f}μm  W/L={sizing['XM6_W']/sizing['XM6_L']:>8.2f}"
    )
    print(
        f"  M7 (out sink):  W={sizing['XM7_W']:>8.3f}μm  L={sizing['XM7_L']:>6.3f}μm  W/L={sizing['XM7_W']/sizing['XM7_L']:>8.2f}"
    )
    print(f"  Cc:             {sizing['C1_value']:>8.3f}pF")


def run_simulation(name: str, sizing: Dict[str, float]) -> Dict:
    """Run SPICE simulation for a sizing configuration"""
    print(f"\n{'='*60}")
    print(f"Simulating: {name}")
    print(f"{'='*60}")

    parameters = create_parameters(sizing)

    optimizer = Optimizer(
        circuit="OpAmp_tb.sch",
        template="template",
        solver="pso",
        max_iterations=1,
        precision=1e-6,
        verbose=False,
    )

    result = optimizer.optimize(
        parameters=parameters,
        tests=tests,
        targets=targets,
        constraints=[],
    )

    return {
        "name": name,
        "sizing": sizing,
        "success": result.success,
        "cost": result.cost,
        "result": result,
        "metrics": result.metrics,
    }


def print_comparison(results: List[Dict]):
    """Print comparison table"""
    print("\n" + "=" * 80)
    print("SIMULATION RESULTS COMPARISON")
    print("=" * 80)

    # Sizing comparison table
    print("\n" + "-" * 80)
    print("TRANSISTOR SIZING")
    print("-" * 80)
    print(f"{'Param':<10}", end="")
    for r in results:
        print(f"{r['name']:>20}", end="")
    print()
    print("-" * 80)

    params = [
        "XM1_W",
        "XM1_L",
        "XM3_W",
        "XM3_L",
        "XM5_W",
        "XM5_L",
        "XM6_W",
        "XM6_L",
        "XM7_W",
        "XM7_L",
        "C1_value",
    ]
    units = ["μm", "μm", "μm", "μm", "μm", "μm", "μm", "μm", "μm", "μm", "pF"]

    for param, unit in zip(params, units):
        print(f"{param:<10}", end="")
        for r in results:
            val = r["sizing"].get(param, 0)
            print(f"{val:>17.3f} {unit}", end="")
        print()

    # Performance comparison table
    print("\n" + "-" * 80)
    print("PERFORMANCE: PREDICTED vs SIMULATED")
    print("-" * 80)
    print(f"{'Metric':<20} {'Target':<12} {'Sq-Law Pred':<14} {'Sq-Law Sim':<14}")
    print("-" * 80)

    # Get Square-Law result
    sq_result = next((r for r in results if r["name"] == "Square-Law"), None)

    if sq_result and sq_result.get("metrics"):
        metrics = sq_result["metrics"]
        print(
            f"{'DC Gain (dB)':<20} {'≥ 40':<12} {'66.58':<14} {metrics.get('DC_GAIN', 'N/A'):<14.2f}"
        )
        print(
            f"{'GBW (MHz)':<20} {'≥ 5':<12} {'10.61':<14} {metrics.get('GBW', 0)/1e6:<14.2f}"
        )
        print(
            f"{'Phase Margin (°)':<20} {'≥ 45':<12} {'59.07':<14} {metrics.get('PHASE_MARGIN', 'N/A'):<14.2f}"
        )
        print(
            f"{'Power (μW)':<20} {'≤ 2000':<12} {'30.90':<14} {metrics.get('POWER', 0)*1e6:<14.2f}"
        )
        print(
            f"{'Area (μm²)':<20} {'≤ 50':<12} {'N/A':<14} {metrics.get('AREA', 0)*1e12:<14.2f}"
        )


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("TWO-STAGE OPAMP SIZING COMPARISON TEST")
    print("=" * 80)

    # =========================================================================
    # Step 1: Get sizing from different methods
    # =========================================================================

    print("\n[1] Calculating sizing using different methods...")

    # Define specs (customize as needed)
    specs = Specifications(
        gbw=10.0,  # 10 MHz
        phase_margin=60,  # 60°
        slew_rate=10.0,  # 10 V/μs
        c_load=1.0,  # 1 pF
        vdd=1.8,
        vss=0.0,
    )

    choices = DesignChoices(
        # Channel lengths [μm] - Sky130 min is 0.13 μm
        l_m1=0.5,  # Input pair
        l_m3=1.0,  # Active load
        l_m5=0.3,  # Tail source
        l_m6=0.5,  # Output driver
        l_m7=0.3,  # Output sink
        # Square-law: Overdrive voltages [V]
        vov_m1=0.15,
        vov_m3=0.20,
        vov_m5=0.20,
        vov_m6=0.20,
        vov_m7=0.15,
        # gm/Id: Operating points [1/V]
        gmid_m1=15.0,
        gmid_m3=10.0,
        gmid_m5=10.0,
        gmid_m6=10.0,
        gmid_m7=10.0,
        # Sizing constraints [μm]
        max_width=100.0,  # Maximum transistor width
        min_width=0.42,  # Minimum transistor width (Sky130)
    )

    # Get Square-Law sizing
    print("\n--- Square-Law Method ---")
    sq_sizing = get_sizing("square_law", specs=specs, choices=choices)
    print_sizing("Square-Law", sq_sizing)

    # Get gm/Id sizing (uncomment when lookup tables are ready)
    print("\n--- gm/Id Method ---")
    gmid_sizing = get_sizing(
        "gmid", specs=specs, choices=choices, lookup_dir=LOOKUP_DIR
    )
    print_sizing("gm/Id", gmid_sizing)

    # Template sizing
    print_sizing("Template", TEMPLATE_SIZING)

    # =========================================================================
    # Step 2: Run simulations
    # =========================================================================

    print("\n" + "=" * 80)
    print("[2] Running SPICE simulations...")
    print("=" * 80)

    results = []

    # Test Template (before)
    results.append(run_simulation("Template", TEMPLATE_SIZING))

    print("Square-Law keys:", sq_sizing.keys())
    print("Template keys:", TEMPLATE_SIZING.keys())
    print("Missing keys:", set(TEMPLATE_SIZING.keys()) - set(sq_sizing.keys()))

    # Test Square-Law
    results.append(run_simulation("Square-Law", sq_sizing))

    results.append(run_simulation("gm/Id", gmid_sizing))

    # =========================================================================
    # Step 3: Print comparison
    # =========================================================================

    print_comparison(results)

    # =========================================================================
    # Step 4: Summary
    # =========================================================================

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    best = min(results, key=lambda x: x["cost"])
    print(f"\nBest configuration: {best['name']} (cost={best['cost']:.4f})")

    print("\nPredicted vs Simulated (Square-Law):")
    if "_performance" in sq_sizing:
        perf = sq_sizing["_performance"]
        print(f"  Predicted DC Gain:  {perf.get('DC Gain (dB)', 'N/A'):.1f} dB")
        print(f"  Predicted GBW:      {perf.get('GBW (MHz)', 'N/A'):.2f} MHz")
        print(f"  Predicted PM:       {perf.get('Phase Margin (°)', 'N/A'):.1f}°")
        print(f"  Predicted Power:    {perf.get('Power (μW)', 'N/A'):.2f} μW")

    print("\n" + "=" * 80)
    print("DONE")
    print("=" * 80)
