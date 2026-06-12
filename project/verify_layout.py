#!/usr/bin/env python3
"""Verify GDS layout via KLayout DRC/LVS and Magic PEX.

Usage:
    python verify_layout.py strongarm.gds
    python verify_layout.py strongarm.gds --spice strongarm.sp
    python verify_layout.py *.gds --summary
    python verify_layout.py strongarm.gds --drc-only
    python verify_layout.py strongarm.gds --pex-only

Requires: klayout, magic on PATH (provided by nix develop)
          PDK_ROOT set to sky130A location
"""

import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path


def find_sky130a() -> Path | None:
    """Locate sky130A directory."""
    pdk_root = os.environ.get("PDK_ROOT", os.path.expanduser("~/.ciel"))
    # Try direct path
    direct = Path(pdk_root) / "sky130A"
    if direct.exists():
        return direct
    # Try ciel versioned layout
    versions = Path(pdk_root) / "ciel" / "sky130" / "versions"
    if versions.exists():
        for ver in sorted(versions.iterdir(), reverse=True):
            candidate = ver / "sky130A"
            if candidate.exists():
                return candidate
    return None


SKY130A = find_sky130a()


# ---------------------------------------------------------------------------
# KLayout DRC
# ---------------------------------------------------------------------------

def run_drc(gds_path: Path, work_dir: Path, verbose: bool = False) -> dict:
    """Run KLayout DRC using sky130A_mr.drc."""
    if SKY130A is None:
        return {"violations": -1, "details": ["sky130A not found"]}

    drc_script = SKY130A / "libs.tech" / "klayout" / "drc" / "sky130A_mr.drc"
    if not drc_script.exists():
        return {"violations": -1, "details": [f"DRC script missing: {drc_script}"]}

    report = work_dir / f"{gds_path.stem}_drc.xml"
    cmd = [
        "klayout", "-b",
        "-rd", f"input={gds_path}",
        "-rd", f"report={report}",
        "-rd", "feol=true",
        "-rd", "beol=true",
        "-rd", "offgrid=true",
        "-r", str(drc_script),
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, cwd=str(work_dir))
        if verbose and result.stderr:
            for line in result.stderr.strip().splitlines()[-5:]:
                print(f"  [drc] {line}")
    except subprocess.TimeoutExpired:
        return {"violations": -1, "details": ["DRC timed out (300s)"]}
    except FileNotFoundError:
        return {"violations": -1, "details": ["klayout not on PATH"]}

    if not report.exists():
        return {"violations": -1, "details": ["DRC report not generated"]}

    text = report.read_text()
    violations = text.count("<item>")
    details = []
    for m in re.finditer(r'<category>\s*<name>(.*?)</name>.*?</category>', text, re.DOTALL):
        cat_count = m.group(0).count("<item>")
        if cat_count > 0:
            details.append(f"{m.group(1)}: {cat_count}")

    return {"violations": violations, "details": details[:20]}


# ---------------------------------------------------------------------------
# KLayout LVS
# ---------------------------------------------------------------------------

def run_lvs(gds_path: Path, spice_path: Path, work_dir: Path, verbose: bool = False) -> dict:
    """Run KLayout LVS comparing GDS against SPICE netlist."""
    if SKY130A is None:
        return {"matches": False, "details": ["sky130A not found"]}

    lvs_script = SKY130A / "libs.tech" / "klayout" / "lvs" / "sky130.lvs"
    if not lvs_script.exists():
        return {"matches": False, "details": [f"LVS script missing: {lvs_script}"]}

    report = work_dir / f"{gds_path.stem}_lvs.lvsdb"
    netlist = work_dir / f"{gds_path.stem}_extracted.cir"

    cmd = [
        "klayout", "-b",
        "-rd", f"input={gds_path}",
        "-rd", f"schematic={spice_path}",
        "-rd", f"report={report}",
        "-rd", f"target_netlist={netlist}",
        "-rd", "run_mode=flat",
        "-rd", "spice_net_names=true",
        "-rd", "spice_comments=false",
        "-rd", "scale=false",
        "-rd", "verbose=false",
        "-rd", "schematic_simplify=false",
        "-rd", "net_only=false",
        "-rd", "top_lvl_pins=false",
        "-rd", "combine=false",
        "-rd", "purge=false",
        "-rd", "purge_nets=false",
        "-r", str(lvs_script),
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, cwd=str(work_dir))
        output = result.stdout + result.stderr
        if verbose:
            for line in output.strip().splitlines()[-10:]:
                print(f"  [lvs] {line}")
    except subprocess.TimeoutExpired:
        return {"matches": False, "details": ["LVS timed out (300s)"]}
    except FileNotFoundError:
        return {"matches": False, "details": ["klayout not on PATH"]}

    matches = "congratulations" in output.lower() or "netlists match" in output.lower()
    details = []
    if report.exists():
        rtext = report.read_text(errors="replace")
        mc = rtext.lower().count("mismatch")
        if mc > 0:
            details.append(f"{mc} mismatch references")

    return {"matches": matches, "details": details}


# ---------------------------------------------------------------------------
# Magic PEX
# ---------------------------------------------------------------------------

def _detect_top_cell(gds_path: Path) -> str:
    """Detect top cell name from GDS using klayout."""
    try:
        script = f'layout = RBA::Layout.new; layout.read("{gds_path}"); layout.each_cell {{ |c| puts c.name }}'
        tmp = Path("/tmp/_mvm_list_cells.rb")
        tmp.write_text(script)
        result = subprocess.run(["klayout", "-b", "-r", str(tmp)],
                                capture_output=True, text=True, timeout=30)
        cells = [l.strip() for l in result.stdout.splitlines() if l.strip()]
        return cells[-1] if cells else gds_path.stem
    except Exception:
        return gds_path.stem


def run_pex(gds_path: Path, work_dir: Path, verbose: bool = False) -> dict:
    """Run Magic parasitic extraction."""
    if SKY130A is None:
        return {"resistors": -1, "capacitors": -1, "details": ["sky130A not found"]}

    magicrc = SKY130A / "libs.tech" / "magic" / "sky130A.magicrc"
    tech = SKY130A / "libs.tech" / "magic" / "sky130A.tech"

    cell = _detect_top_cell(gds_path)
    flat_cell = f"{cell}_flat"
    pex_spice = work_dir / f"{gds_path.stem}_pex.spice"

    gds_abs = gds_path.resolve()
    spice_name = f"{flat_cell}.spice"

    tcl = f"""\
gds read {gds_abs}
load {cell}
flatten {flat_cell}
load {flat_cell}
select top cell
extract all
ext2spice lvs
ext2spice cthresh 0
ext2spice rthresh 0
ext2spice -o {spice_name} {flat_cell}
quit -noprompt
"""

    cmd = ["magic", "-dnull", "-noconsole"]
    if magicrc.exists():
        cmd += ["-rcfile", str(magicrc)]
    else:
        cmd += ["-T", str(tech)]

    try:
        result = subprocess.run(
            cmd, input=tcl, capture_output=True, text=True, timeout=300, cwd=str(work_dir)
        )
        if verbose and result.stderr:
            for line in result.stderr.strip().splitlines()[-5:]:
                print(f"  [pex] {line}")
    except subprocess.TimeoutExpired:
        return {"resistors": -1, "capacitors": -1, "details": ["PEX timed out (300s)"]}
    except FileNotFoundError:
        return {"resistors": -1, "capacitors": -1, "details": ["magic not on PATH"]}

    # Magic writes <spice_name> in cwd (work_dir)
    default_out = work_dir / spice_name
    if default_out.exists():
        default_out.rename(pex_spice)
    elif not pex_spice.exists():
        return {"resistors": -1, "capacitors": -1, "details": ["PEX SPICE not generated"]}

    text = pex_spice.read_text()
    resistors = sum(1 for l in text.splitlines() if l.strip().startswith("R"))
    capacitors = sum(1 for l in text.splitlines() if l.strip().startswith("C"))

    return {"resistors": resistors, "capacitors": capacitors, "spice": str(pex_spice), "details": []}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def verify_one(gds_path: Path, spice_path: Path | None, args) -> dict:
    """Run all checks on one GDS file."""
    work_dir = Path(args.work_dir) / gds_path.stem
    # Clean stale extraction artifacts
    if work_dir.exists():
        for f in work_dir.glob("*.ext"):
            f.unlink()
        for f in work_dir.glob("*.res.ext"):
            f.unlink()
        for f in work_dir.glob("*.spice"):
            f.unlink()
    work_dir.mkdir(parents=True, exist_ok=True)

    result = {"name": gds_path.stem}

    if not args.pex_only:
        drc = run_drc(gds_path, work_dir, verbose=args.verbose)
        result["drc_violations"] = drc["violations"]
        result["drc_details"] = drc["details"]

    if not args.drc_only and not args.pex_only and spice_path and spice_path.exists():
        lvs = run_lvs(gds_path, spice_path, work_dir, verbose=args.verbose)
        result["lvs_matches"] = lvs["matches"]
        result["lvs_details"] = lvs["details"]

    if not args.drc_only:
        if args.extract:
            # Full extraction → parasitic netlist for post-layout simulation
            pex = run_pex_full(gds_path, work_dir, verbose=args.verbose)
            if pex["ok"]:
                result["pex_r"] = pex["resistors"]
                result["pex_c"] = pex["capacitors"]
                result["pex_netlist"] = pex["netlist"]
            else:
                result["pex_r"] = -1
                result["pex_c"] = -1
                result["pex_details"] = pex["details"]
        else:
            pex = run_pex(gds_path, work_dir, verbose=args.verbose)
            result["pex_r"] = pex["resistors"]
            result["pex_c"] = pex["capacitors"]
            if "spice" in pex:
                result["pex_spice"] = pex["spice"]

    return result


def run_pex_full(gds_path: Path, work_dir: Path, verbose: bool = False) -> dict:
    """Run Magic PEX with full RC extraction → parasitic SPICE netlist for post-layout sim.

    Output netlist includes all parasitic R/C and can be .included in testbenches
    for corner/MC analysis with real layout parasitics.
    """
    if SKY130A is None:
        return {"ok": False, "details": ["sky130A not found"]}

    magicrc = SKY130A / "libs.tech" / "magic" / "sky130A.magicrc"
    tech = SKY130A / "libs.tech" / "magic" / "sky130A.tech"

    cell = _detect_top_cell(gds_path)
    flat_cell = f"{cell}_flat"
    pex_spice = work_dir / f"{gds_path.stem}_pex.spice"
    pex_sim = work_dir / f"{gds_path.stem}_parasitic.spice"

    gds_abs = gds_path.resolve()
    spice_name = f"{flat_cell}.spice"

    tcl = f"""\
gds read {gds_abs}
load {cell}
flatten {flat_cell}
load {flat_cell}
select top cell
extract all
ext2spice lvs
ext2spice cthresh 0
ext2spice rthresh 0
ext2spice -o {spice_name} {flat_cell}
quit -noprompt
"""

    cmd = ["magic", "-dnull", "-noconsole"]
    if magicrc.exists():
        cmd += ["-rcfile", str(magicrc)]
    else:
        cmd += ["-T", str(tech)]

    try:
        result = subprocess.run(
            cmd, input=tcl, capture_output=True, text=True, timeout=600, cwd=str(work_dir)
        )
        if verbose:
            for line in (result.stdout + result.stderr).strip().splitlines()[-10:]:
                print(f"  [pex-full] {line}")
    except subprocess.TimeoutExpired:
        return {"ok": False, "details": ["PEX timed out (600s)"]}
    except FileNotFoundError:
        return {"ok": False, "details": ["magic not on PATH"]}

    # Magic writes <spice_name> in cwd (work_dir)
    default_out = work_dir / spice_name
    if default_out.exists():
        default_out.rename(pex_spice)
    elif not pex_spice.exists():
        return {"ok": False, "details": ["PEX netlist not generated"]}

    # Post-process: wrap in .subckt for easy .include in testbenches
    raw = pex_spice.read_text()
    lines = raw.splitlines()

    # Count parasitics
    n_r = sum(1 for l in lines if l.strip().startswith("R"))
    n_c = sum(1 for l in lines if l.strip().startswith("C"))

    # Write sim-ready version with header
    with open(pex_sim, "w") as f:
        f.write(f"* Parasitic netlist for {cell} (extracted from GDS via Magic)\n")
        f.write(f"* R={n_r}, C={n_c}\n")
        f.write(f"* Use: .include {pex_sim.name}\n")
        f.write(f"*      Then instantiate X... {cell}_flat <ports>\n")
        f.write("*\n")
        f.write(raw)

    return {
        "ok": True,
        "netlist": str(pex_sim),
        "resistors": n_r,
        "capacitors": n_c,
        "details": [],
    }


def main():
    parser = argparse.ArgumentParser(description="Verify GDS layout (DRC/LVS/PEX)")
    parser.add_argument("gds", nargs="+", help="GDS file(s) to verify")
    parser.add_argument("--spice", help="SPICE netlist for LVS (auto-detected if <name>.sp exists)")
    parser.add_argument("--work-dir", default="verify_output", help="Working directory for reports")
    parser.add_argument("--drc-only", action="store_true")
    parser.add_argument("--pex-only", action="store_true")
    parser.add_argument("--extract", action="store_true",
                        help="Full parasitic extraction → .spice netlist for post-layout sim")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--summary", action="store_true", help="Print summary table only")
    args = parser.parse_args()

    if SKY130A is None:
        print("ERROR: sky130A PDK not found. Set PDK_ROOT or install via ciel.", file=sys.stderr)
        return 1

    print(f"PDK: {SKY130A}")
    print(f"Output: {args.work_dir}/")
    print()

    results = []
    for gds_str in args.gds:
        gds_path = Path(gds_str).resolve()
        if not gds_path.exists():
            print(f"  SKIP {gds_path.name} — file not found")
            continue

        # Auto-detect SPICE
        spice = Path(args.spice) if args.spice else gds_path.with_suffix(".sp")

        if not args.summary:
            print(f"--- {gds_path.name} ---")

        r = verify_one(gds_path, spice, args)
        results.append(r)

        if not args.summary:
            if "drc_violations" in r:
                status = "CLEAN" if r["drc_violations"] == 0 else f"{r['drc_violations']} violations"
                print(f"  DRC: {status}")
                if r["drc_violations"] > 0 and r["drc_details"]:
                    for d in r["drc_details"][:5]:
                        print(f"       {d}")
            if "lvs_matches" in r:
                print(f"  LVS: {'MATCH' if r['lvs_matches'] else 'MISMATCH'}")
            if "pex_r" in r:
                print(f"  PEX: R={r['pex_r']}, C={r['pex_c']}")
                if "pex_netlist" in r:
                    print(f"  Parasitic netlist: {r['pex_netlist']}")
            print()

    # Summary
    if len(results) > 1 or args.summary:
        print("=" * 65)
        print(f"{'Name':<25} {'DRC':<12} {'LVS':<10} {'PEX R':<8} {'PEX C':<8}")
        print("-" * 65)
        for r in results:
            drc = str(r.get("drc_violations", "—"))
            lvs = "OK" if r.get("lvs_matches") else ("FAIL" if "lvs_matches" in r else "—")
            pex_r = str(r.get("pex_r", "—"))
            pex_c = str(r.get("pex_c", "—"))
            print(f"{r['name']:<25} {drc:<12} {lvs:<10} {pex_r:<8} {pex_c:<8}")

    # Exit code
    any_fail = any(
        r.get("drc_violations", 0) > 0 or r.get("lvs_matches") is False
        for r in results
    )
    return 1 if any_fail else 0


if __name__ == "__main__":
    sys.exit(main())
