"""
Sky130 MOSFET Characterization Tool
Combines lookup table generation and analysis with easy configuration
"""

import numpy as np
import matplotlib.pyplot as plt
from mosplot.plot import load_lookup_table, Mosfet, Expression
from mosplot.lookup_table_generator.simulators import NgspiceSimulator
from mosplot.lookup_table_generator import TransistorSweep, LookupTableGenerator
import os
from enum import Enum
from pathlib import Path

# ============================================================================
# USER CONFIGURATION - EDIT THIS SECTION
# ============================================================================

# --- Device Selection ---
DEVICE_TO_ANALYZE = "sky130_fd_pr__nfet_01v8"  # Options below

VBS = 0.0  # Body-source voltage
VDS = 0.6  # Drain-source voltage (use negative for PMOS, e.g., -0.6)
VGS_RANGE = (
    0.01,
    1.8,
)  # Gate-source voltage range (use negative for PMOS, e.g., (-1.8, -0.01))
LENGTH_FILTER = None  # Specific length in meters (e.g., 0.15e-6) or None for all

# --- Plot Configuration ---
PLOT_CONFIG = {
    # Plot 1: X vs Y
    "plot1": {
        "enabled": True,
        "x_axis": "gmid",  # Options: "gmid", "vgs", "vds", "id", "gm", "gds", "current_density"
        "y_axis": "current_density",  # Same options as x_axis
        "y_scale": "log",  # "log" or "linear"
        "title": "gm/ID vs Current Density",
        "filename": "plot1.svg",
    },
    # Plot 2: Another X vs Y
    "plot2": {
        "enabled": True,
        "x_axis": "vgs",
        "y_axis": "gm",
        "y_scale": "linear",
        "title": "VGS vs Transconductance",
        "filename": "plot2.svg",
    },
    # Plot 3: Custom expression example
    "plot3": {
        "enabled": False,
        "x_axis": "gmid",
        "y_axis": "ft",  # Transit frequency (gm / (2*pi*Cgg))
        "y_scale": "log",
        "title": "gm/ID vs Transit Frequency",
        "filename": "plot3.svg",
    },
}

# --- Lookup Value Configuration ---
# Extract specific values from the lookup table
LOOKUP_QUERIES = [
    {
        "enabled": True,
        "description": "Find ID/W at gm/ID = 10",
        "x_param": "gmid",
        "x_value": 10.0,
        "y_param": "current_density",
        "length": 0.15e-6,  # Specific length or None
    },
    {
        "enabled": True,
        "description": "Find gm at VGS = 0.6V",
        "x_param": "vgs",
        "x_value": 0.6,
        "y_param": "gm",
        "length": 0.5e-6,
    },
    {
        "enabled": False,
        "description": "Find VGS at gm/ID = 15",
        "x_param": "gmid",
        "x_value": 15.0,
        "y_param": "vgs",
        "length": None,  # Will show all lengths
    },
]

# --- Comparison Plot Configuration ---
COMPARE_DEVICES = {
    "enabled": False,
    "devices": [
        "sky130_fd_pr__nfet_01v8",
        "sky130_fd_pr__nfet_01v8_lvt",
    ],
    "x_axis": "gmid",
    "y_axis": "current_density",
    "length": 0.15e-6,
    "title": "Device Comparison",
    "filename": "comparison.svg",
}

# --- Generation Settings ---
LOOKUP_DIR = "./sky130_lookup_tables"
FIGURE_DIR = "./figures"
AUTO_GENERATE = True  # Automatically generate lookup tables if missing
REGENERATE = False  # Force regeneration even if tables exist

# ============================================================================
# END USER CONFIGURATION
# ============================================================================


class Sky130Device(Enum):
    """Available Sky130 1.8V devices for gm/ID characterization"""

    # NMOS devices
    NFET_01V8 = "sky130_fd_pr__nfet_01v8"
    NFET_01V8_LVT = "sky130_fd_pr__nfet_01v8_lvt"

    # PMOS devices
    PFET_01V8 = "sky130_fd_pr__pfet_01v8"
    PFET_01V8_HVT = "sky130_fd_pr__pfet_01v8_hvt"
    PFET_01V8_LVT = "sky130_fd_pr__pfet_01v8_lvt"

    def is_nmos(self):
        return "nfet" in self.value

    def is_pmos(self):
        return "pfet" in self.value

    def __str__(self):
        return self.value


# ============================================================================
# Lookup Table Generator
# ============================================================================


def setup_lookup_generator():
    """Setup lookup table generator for Sky130"""

    # Get PDK paths
    PDK_ROOT = os.environ.get("PDK_ROOT", os.path.expanduser("~/.volare"))
    PDK = os.environ.get("PDK", "sky130A")
    PDK_PATH = os.path.join(PDK_ROOT, PDK)
    SKY130_LIB = os.path.join(PDK_PATH, "libs.tech/ngspice/sky130.lib.spice")

    # Common simulator parameters
    common_params = {
        "simulator_path": "ngspice",
        "temperature": 27,
        "parameters_to_save": ["id", "vth", "vdsat", "gm", "gds", "gmbs"],
        "lib_mappings": [(SKY130_LIB, "tt")],
        "device_parameters": {"w": 1e-6, "l": 0.15e-6, "nf": 1, "mult": 1},
        "raw_spice": [".option TEMP=27", ".option TNOM=27"],
    }

    # Create simulators for each device
    simulators = {
        "sky130_fd_pr__nfet_01v8": NgspiceSimulator(
            **common_params,
            mos_spice_symbols=("x1", "x1.msky130_fd_pr__nfet_01v8"),
        ),
        "sky130_fd_pr__nfet_01v8_lvt": NgspiceSimulator(
            **common_params,
            mos_spice_symbols=("x1", "x1.msky130_fd_pr__nfet_01v8_lvt"),
        ),
        "sky130_fd_pr__pfet_01v8": NgspiceSimulator(
            **common_params,
            mos_spice_symbols=("x1", "x1.msky130_fd_pr__pfet_01v8"),
        ),
        "sky130_fd_pr__pfet_01v8_hvt": NgspiceSimulator(
            **common_params,
            mos_spice_symbols=("x1", "x1.msky130_fd_pr__pfet_01v8_hvt"),
        ),
        "sky130_fd_pr__pfet_01v8_lvt": NgspiceSimulator(
            **common_params,
            mos_spice_symbols=("x1", "x1.msky130_fd_pr__pfet_01v8_lvt"),
        ),
    }

    # Sweep configurations
    nmos_sweep = TransistorSweep(
        mos_type="nmos",
        vgs=(0, 1.8, 0.02),
        vds=(0, 1.8, 0.02),
        vbs=(0, -1.8, -0.2),
        length=[0.15e-6, 0.5e-6, 1.0e-6, 2.0e-6],
    )

    pmos_sweep = TransistorSweep(
        mos_type="pmos",
        vgs=(0, -1.8, -0.02),
        vds=(0, -1.8, -0.02),
        vbs=(0, 1.8, 0.2),
        length=[0.15e-6, 0.5e-6, 1.0e-6, 2.0e-6],
    )

    model_sweeps = {
        "sky130_fd_pr__nfet_01v8": nmos_sweep,
        "sky130_fd_pr__nfet_01v8_lvt": nmos_sweep,
        "sky130_fd_pr__pfet_01v8": pmos_sweep,
        "sky130_fd_pr__pfet_01v8_hvt": pmos_sweep,
        "sky130_fd_pr__pfet_01v8_lvt": pmos_sweep,
    }

    # Create generator
    generator = LookupTableGenerator(
        description="Sky130 PDK - All 1.8V device variants",
        simulator=simulators,
        model_sweeps=model_sweeps,
        n_process=1,
    )

    return generator


# ============================================================================
# Expression Helper
# ============================================================================


def get_expression(name, mosfet):
    """Get expression by name"""
    expressions = {
        "gmid": mosfet.gmid_expression,
        "vgs": mosfet.vgs_expression,
        "vds": mosfet.vds_expression,
        "id": Expression(variables=["id"], function=lambda id: id, label="$I_D$ (A)"),
        "gm": Expression(variables=["gm"], function=lambda gm: gm, label="$g_m$ (S)"),
        "gds": Expression(
            variables=["gds"], function=lambda gds: gds, label="$g_{ds}$ (S)"
        ),
        "current_density": mosfet.current_density_expression,
        "ft": Expression(
            variables=["gm", "id"],
            function=lambda gm, id: gm / (2 * np.pi * 1e-15),  # Simplified
            label="$f_T$ (Hz)",
        ),
        "av": Expression(
            variables=["gm", "gds"],
            function=lambda gm, gds: gm / gds,
            label="$A_v$ (V/V)",
        ),
    }
    return expressions.get(name.lower())


# ============================================================================
# Main Analysis Functions
# ============================================================================


def generate_lookup_tables(lookup_dir, force=False):
    """Generate lookup tables if needed"""
    lookup_path = Path(lookup_dir)
    lookup_path.mkdir(exist_ok=True)

    # Check if tables already exist
    all_devices = [d.value for d in Sky130Device]
    existing = [d for d in all_devices if (lookup_path / f"{d}.npz").exists()]

    if len(existing) == len(all_devices) and not force:
        print(f"✓ All lookup tables exist in {lookup_dir}")
        return

    if force:
        print("Regenerating all lookup tables (forced)...")
    else:
        print(f"Generating missing lookup tables in {lookup_dir}...")

    generator = setup_lookup_generator()

    try:
        print("\nRunning OP simulation to verify setup...")
        generator.op_simulation()
        print("✓ OP simulation successful!")

        print("\nBuilding lookup tables...")
        print("This may take several minutes...")
        generator.build(lookup_dir)
        print(f"\n✓ Lookup tables saved to: {lookup_dir}")

    except Exception as e:
        print(f"✗ Generation failed: {e}")
        raise


def create_mosfet(device_name, vbs, vds, vgs, length, lookup_dir):
    """Create Mosfet object from lookup table"""
    table_path = Path(lookup_dir) / f"{device_name}.npz"

    if not table_path.exists():
        raise FileNotFoundError(f"Lookup table not found: {table_path}")

    lookup_table = load_lookup_table(str(table_path))

    mosfet = Mosfet(
        lookup_table=lookup_table,
        mos=device_name,
        vbs=vbs,
        vds=vds,
        vgs=vgs,
    )

    if length is not None:
        mosfet.length = length

    return mosfet


def plot_analysis(mosfet, config, output_dir):
    """Create a plot based on configuration"""
    if not config["enabled"]:
        return

    x_expr = get_expression(config["x_axis"], mosfet)
    y_expr = get_expression(config["y_axis"], mosfet)

    if x_expr is None or y_expr is None:
        print(f"✗ Invalid expression in plot config: {config}")
        return

    output_path = Path(output_dir) / config["filename"]
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"  Plotting: {config['title']}")

    mosfet.plot_by_expression(
        x_expression=x_expr,
        y_expression=y_expr,
        filtered_values=(
            mosfet.length[0:-1:4] if LENGTH_FILTER is None else [LENGTH_FILTER]
        ),
        y_scale=config["y_scale"],
        save_fig=str(output_path),
    )

    print(f"    Saved: {output_path}")


def lookup_value(mosfet, query):
    """Look up a specific value from the lookup table"""
    if not query["enabled"]:
        return

    print(f"\n  {query['description']}")

    # Filter by length if specified
    data = mosfet.data
    if query["length"] is not None:
        length_mask = np.isclose(data["length"], query["length"])
        data = {k: v[length_mask] for k, v in data.items()}
        print(f"    Length: {query['length']*1e6:.2f}μm")

    # Get x and y expressions
    x_expr = get_expression(query["x_param"], mosfet)
    y_expr = get_expression(query["y_param"], mosfet)

    if x_expr is None or y_expr is None:
        print(f"    ✗ Invalid parameter names")
        return

    # Evaluate expressions
    x_data = x_expr.evaluate(data)
    y_data = y_expr.evaluate(data)

    # Find closest x value
    idx = np.argmin(np.abs(x_data - query["x_value"]))
    actual_x = x_data[idx]
    result_y = y_data[idx]

    print(f"    At {query['x_param']} = {actual_x:.4g} (requested: {query['x_value']})")
    print(f"    → {query['y_param']} = {result_y:.4g}")


def compare_devices(config, lookup_dir, output_dir):
    """Compare multiple devices on same plot"""
    if not config["enabled"]:
        return

    print(f"\nGenerating comparison plot: {config['title']}")

    fig, ax = plt.subplots(figsize=(10, 6))

    for device_name in config["devices"]:
        print(f"  Loading {device_name}...")

        mosfet = create_mosfet(
            device_name,
            vbs=VBS,
            vds=VDS,
            vgs=VGS_RANGE,
            length=config["length"],
            lookup_dir=lookup_dir,
        )

        x_expr = get_expression(config["x_axis"], mosfet)
        y_expr = get_expression(config["y_axis"], mosfet)

        x_data = x_expr.evaluate(mosfet.data)
        y_data = y_expr.evaluate(mosfet.data)

        ax.plot(x_data, y_data, label=device_name, linewidth=2)

    ax.set_xlabel(x_expr.label)
    ax.set_ylabel(y_expr.label)
    ax.set_title(config["title"])
    ax.legend()
    ax.grid(True, alpha=0.3)

    if config.get("y_scale") == "log":
        ax.set_yscale("log")

    output_path = Path(output_dir) / config["filename"]
    fig.savefig(str(output_path), bbox_inches="tight")
    print(f"  Saved: {output_path}")
    plt.close(fig)


# ============================================================================
# Main Execution
# ============================================================================


def main():
    print("=" * 70)
    print("Sky130 MOSFET Characterization Tool")
    print("=" * 70)

    # Step 1: Generate lookup tables if needed
    print("\n[1] Checking lookup tables...")
    try:
        if AUTO_GENERATE:
            generate_lookup_tables(LOOKUP_DIR, force=REGENERATE)
        else:
            print(f"Auto-generation disabled. Using tables in {LOOKUP_DIR}")
    except Exception as e:
        print(f"✗ Failed to generate lookup tables: {e}")
        return

    # Step 2: Load device and create Mosfet object
    print(f"\n[2] Loading device: {DEVICE_TO_ANALYZE}")
    try:
        mosfet = create_mosfet(
            DEVICE_TO_ANALYZE,
            vbs=VBS,
            vds=VDS,
            vgs=VGS_RANGE,
            length=LENGTH_FILTER,
            lookup_dir=LOOKUP_DIR,
        )
        print(f"✓ Device loaded successfully")
        print(f"  VBS = {VBS}V, VDS = {VDS}V, VGS = {VGS_RANGE}")
        if LENGTH_FILTER:
            print(f"  Length filter: {LENGTH_FILTER*1e6:.2f}μm")
    except Exception as e:
        print(f"✗ Failed to load device: {e}")
        return

    # Step 3: Generate plots
    enabled_plots = [k for k, v in PLOT_CONFIG.items() if v["enabled"]]
    if enabled_plots:
        print(f"\n[3] Generating {len(enabled_plots)} plot(s)...")
        for plot_name, config in PLOT_CONFIG.items():
            try:
                plot_analysis(mosfet, config, FIGURE_DIR)
            except Exception as e:
                print(f"  ✗ Failed to generate {plot_name}: {e}")
    else:
        print("\n[3] No plots enabled")

    # Step 4: Lookup specific values
    enabled_queries = [q for q in LOOKUP_QUERIES if q["enabled"]]
    if enabled_queries:
        print(f"\n[4] Looking up {len(enabled_queries)} value(s)...")
        for query in LOOKUP_QUERIES:
            try:
                lookup_value(mosfet, query)
            except Exception as e:
                print(f"  ✗ Query failed: {e}")
    else:
        print("\n[4] No lookup queries enabled")

    # Step 5: Device comparison
    print("\n[5] Device comparison...")
    try:
        compare_devices(COMPARE_DEVICES, LOOKUP_DIR, FIGURE_DIR)
    except Exception as e:
        print(f"  ✗ Comparison failed: {e}")

    print("\n" + "=" * 70)
    print("Analysis complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
