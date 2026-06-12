#!/usr/bin/env python3
"""Layout verification flow: GDS generation → DRC → LVS → PEX.

Usage:
    python -m project.layout.verify.run [--component NAME] [--step drc|lvs|pex|all]
    python project/layout/verify/run.py [--component NAME] [--step drc|lvs|pex|all]

Requires: nix develop (magic, netgen-vlsi, klayout, gdstk)
"""
import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]  # MVM/
VERIFY_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "output" / "layout"
PDK_ROOT = os.environ.get("PDK_ROOT", os.path.expanduser("~/.ciel"))
PDK = os.environ.get("PDK", "sky130A")
TECH_FILE = f"{PDK_ROOT}/{PDK}/libs.tech/magic/{PDK}.tech"
NETGEN_SETUP_PDK = f"{PDK_ROOT}/{PDK}/libs.tech/netgen/{PDK}_setup.tcl"
NETGEN_SETUP = str(VERIFY_DIR / "lvs_setup.tcl")

# Component registry: name → (layout_module, layout_func, schematic_generator)
COMPONENTS = {
    "strongarm": (
        "project.layout.cells.strongarm",
        "strongarm_layout",
        "project.components.strongarm.strongarm",
    ),
    "charge_dac": (
        "project.layout.cells.charge_dac",
        "charge_dac_layout",
        "project.components.charge_dac.charge_dac",
    ),
    "sample_hold_bank": (
        "project.layout.cells.sample_hold_bank",
        "sample_hold_bank_layout",
        "project.components.sample_hold_bank.sample_hold_bank",
    ),
    "imc_crossbar": (
        "project.layout.cells.imc_crossbar",
        "imc_crossbar_layout",
        "project.components.imc_crossbar.imc_crossbar",
    ),
    "interleaved_adc": (
        "project.layout.cells.interleaved_adc",
        "interleaved_adc_layout",
        "project.components.interleaved_adc.interleaved_adc",
    ),
    "async_ctrl": (
        "project.layout.cells.async_ctrl",
        "async_ctrl_layout",
        "project.components.async_ctrl.async_ctrl",
    ),
    "gemm_tapeout": (
        "project.layout.cells.gemm_tapeout",
        "gemm_tapeout_layout",
        "project.top.gemm_tapeout_lvs",
    ),
}


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def generate_gds(name: str) -> Path:
    """Generate GDS file from layout module. Returns path to .gds."""
    import importlib
    import gdstk

    mod_name, func_name, _ = COMPONENTS[name]
    mod = importlib.import_module(mod_name)
    layout_fn = getattr(mod, func_name)

    lib = gdstk.Library(f"MVM_{name}", unit=1e-6, precision=1e-9)
    cell, ports = layout_fn(lib)

    out_dir = OUTPUT_DIR / name
    ensure_dir(out_dir)
    gds_path = out_dir / f"{name}.gds"
    lib.write_gds(str(gds_path))
    print(f"[GDS] {name}: {gds_path} ({cell.name}, {len(ports)} ports)")

    bb = cell.bounding_box()
    if bb is not None:
        w = bb[1][0] - bb[0][0]
        h = bb[1][1] - bb[0][1]
        print(f"      Bounding box: {w:.1f} x {h:.1f} um = {w*h:.0f} um²")

    return gds_path


def _strip_ideal_elements(spice_text: str) -> str:
    """Remove ideal C and R elements from SPICE for LVS comparison.

    Layout extracts physical MIM caps and has no ideal resistors.
    Ideal C/R in the schematic cause device count mismatches.
    """
    out = []
    for line in spice_text.splitlines():
        stripped = line.lstrip()
        # Skip ideal C and R elements (but keep subcircuit instances Xname)
        if stripped and stripped[0] in ('C', 'c') and not stripped.startswith('.'):
            continue
        if stripped and stripped[0] in ('R', 'r') and not stripped.startswith('.'):
            continue
        out.append(line)
    return "\n".join(out)


def generate_schematic_spice(name: str) -> Path:
    """Generate schematic SPICE from component. Returns path to .spice."""
    import importlib

    _, _, schem_mod = COMPONENTS[name]
    mod = importlib.import_module(schem_mod)
    spice_text = mod.generate()
    spice_text = _strip_ideal_elements(spice_text)

    out_dir = OUTPUT_DIR / name
    ensure_dir(out_dir)
    spice_path = out_dir / f"{name}_schematic.spice"
    spice_path.write_text(spice_text)
    print(f"[SCH] {name}: {spice_path}")
    return spice_path


def run_magic(tcl_script: str, env: dict) -> subprocess.CompletedProcess:
    """Run a Magic TCL script in batch mode."""
    full_env = {**os.environ, **env}
    cmd = ["magic", "-dnull", "-noconsole", "-T", TECH_FILE]
    return subprocess.run(
        cmd,
        input=Path(tcl_script).read_text(),
        capture_output=True,
        text=True,
        env=full_env,
        cwd=str(OUTPUT_DIR),
    )


def run_drc(name: str, gds_path: Path) -> Path:
    """Run DRC via Magic. Returns path to report."""
    out_dir = OUTPUT_DIR / name
    report_path = out_dir / f"{name}_drc.rpt"

    # Get cell name from GDS
    import gdstk
    lib = gdstk.read_gds(str(gds_path))
    top_cells = lib.top_level()
    cell_name = top_cells[0].name if top_cells else name

    result = run_magic(
        str(VERIFY_DIR / "drc.tcl"),
        {
            "GDS_FILE": str(gds_path),
            "CELL_NAME": cell_name,
            "REPORT_FILE": str(report_path),
        },
    )

    if result.returncode != 0:
        print(f"[DRC] {name}: Magic failed")
        print(result.stderr[:500])
        return report_path

    if report_path.exists():
        text = report_path.read_text()
        # Extract violation count
        for line in text.splitlines():
            if "Total violations" in line:
                print(f"[DRC] {name}: {line.strip()}")
                break
        else:
            print(f"[DRC] {name}: report at {report_path}")
    else:
        print(f"[DRC] {name}: no report generated")
        if result.stdout:
            print(result.stdout[:500])

    return report_path


def run_lvs(name: str, gds_path: Path, schem_path: Path) -> bool:
    """Run LVS: extract layout netlist via Magic, compare via netgen."""
    out_dir = OUTPUT_DIR / name

    # Get cell name
    import gdstk
    lib = gdstk.read_gds(str(gds_path))
    top_cells = lib.top_level()
    cell_name = top_cells[0].name if top_cells else name

    # Step 1: Extract layout netlist
    layout_spice = out_dir / f"{name}_extracted.spice"
    result = run_magic(
        str(VERIFY_DIR / "extract_lvs.tcl"),
        {
            "GDS_FILE": str(gds_path),
            "CELL_NAME": cell_name,
            "OUT_SPICE": str(layout_spice),
        },
    )

    if result.returncode != 0 or not layout_spice.exists():
        print(f"[LVS] {name}: extraction failed")
        print(result.stderr[:500] if result.stderr else "no stderr")
        return False

    print(f"[LVS] {name}: extracted {layout_spice}")

    # Step 2: Run netgen LVS
    lvs_report = out_dir / f"{name}_lvs.rpt"
    flat_name = f"{cell_name}_flat"
    cmd = [
        "netgen", "-batch", "lvs",
        f"{layout_spice} {flat_name}",
        f"{schem_path} {name}",
        NETGEN_SETUP,
        str(lvs_report),
    ]

    lvs_env = {**os.environ, "NETGEN_SETUP_PDK": NETGEN_SETUP_PDK}
    result = subprocess.run(
        cmd, capture_output=True, text=True,
        cwd=str(out_dir), env=lvs_env,
    )

    if lvs_report.exists():
        text = lvs_report.read_text()
        # Check for match
        if "match" in text.lower():
            match_lines = [l for l in text.splitlines()
                           if "match" in l.lower() and "unique" not in l.lower()]
            for line in match_lines[-3:]:
                print(f"[LVS] {name}: {line.strip()}")
        passed = "circuits match" in text.lower() or "netlists match" in text.lower()
        status = "PASS" if passed else "FAIL"
        print(f"[LVS] {name}: {status} — report at {lvs_report}")
        return passed
    else:
        print(f"[LVS] {name}: netgen failed")
        print(result.stdout[:300] if result.stdout else "")
        print(result.stderr[:300] if result.stderr else "")
        return False


def run_pex(name: str, gds_path: Path) -> Path:
    """Run parasitic extraction via Magic. Returns path to PEX SPICE."""
    out_dir = OUTPUT_DIR / name

    import gdstk
    lib = gdstk.read_gds(str(gds_path))
    top_cells = lib.top_level()
    cell_name = top_cells[0].name if top_cells else name

    pex_spice = out_dir / f"{name}_pex.spice"
    result = run_magic(
        str(VERIFY_DIR / "extract_pex.tcl"),
        {
            "GDS_FILE": str(gds_path),
            "CELL_NAME": cell_name,
            "OUT_SPICE": str(pex_spice),
        },
    )

    if result.returncode != 0 or not pex_spice.exists():
        print(f"[PEX] {name}: extraction failed")
        print(result.stderr[:500] if result.stderr else "no stderr")
        return pex_spice

    # Count parasitics
    text = pex_spice.read_text()
    n_r = text.count(" R ")
    n_c = text.count(" C ")
    n_lines = len(text.splitlines())
    print(f"[PEX] {name}: {pex_spice} ({n_lines} lines, {n_r} R, {n_c} C)")
    return pex_spice


def verify_component(name: str, steps: set[str]):
    """Run verification steps for a single component."""
    print(f"\n{'='*60}")
    print(f"  Verifying: {name}")
    print(f"{'='*60}")

    # Always generate GDS first
    try:
        gds_path = generate_gds(name)
    except Exception as e:
        print(f"[ERR] {name}: GDS generation failed: {e}")
        return

    if "drc" in steps:
        run_drc(name, gds_path)

    if "lvs" in steps:
        try:
            schem_path = generate_schematic_spice(name)
            run_lvs(name, gds_path, schem_path)
        except Exception as e:
            print(f"[ERR] {name}: LVS failed: {e}")

    if "pex" in steps:
        pex_path = run_pex(name, gds_path)
        if pex_path.exists():
            print(f"[PEX] {name}: parasitic netlist ready for simulation")
            print(f"      Use: .include {pex_path}")


def main():
    parser = argparse.ArgumentParser(description="Layout verification flow")
    parser.add_argument(
        "--component", "-c",
        choices=list(COMPONENTS.keys()) + ["all"],
        default="all",
        help="Component to verify (default: all)",
    )
    parser.add_argument(
        "--step", "-s",
        choices=["drc", "lvs", "pex", "all"],
        default="all",
        help="Verification step (default: all)",
    )
    args = parser.parse_args()

    # Check tools
    for tool in ["magic", "netgen"]:
        if subprocess.run(["which", tool], capture_output=True).returncode != 0:
            print(f"ERROR: {tool} not found. Run inside 'nix develop'.")
            sys.exit(1)

    if not Path(TECH_FILE).exists():
        print(f"ERROR: Sky130 tech file not found at {TECH_FILE}")
        print(f"       Set PDK_ROOT or run 'ciel enable --pdk-family sky130'")
        sys.exit(1)

    steps = {"drc", "lvs", "pex"} if args.step == "all" else {args.step}
    components = list(COMPONENTS.keys()) if args.component == "all" else [args.component]

    ensure_dir(OUTPUT_DIR)

    results = {}
    for name in components:
        verify_component(name, steps)

    print(f"\n{'='*60}")
    print(f"  Output directory: {OUTPUT_DIR}")
    print(f"{'='*60}")


if __name__ == "__main__":
    # Ensure project root is on path
    sys.path.insert(0, str(ROOT))
    main()
