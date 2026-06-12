"""Build final TT-compatible GDS from gemm_tapeout layout + DEF pin geometry."""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import gdstk
from project.layout.cells.gemm_tapeout import gemm_tapeout_layout, TT_PINS, DIE_W, DIE_H
from project.layout.layers import L, ld

# ---------------------------------------------------------------------------
# TT project cell name — change this to match your TT project ID
# ---------------------------------------------------------------------------
CELL_NAME = "tt_um_mvm_gemm"

# ---------------------------------------------------------------------------
# DEF pin geometry (relative extents from DEF, in um)
# ---------------------------------------------------------------------------
# Signal pins: met4 (-0.15, -0.50) to (0.15, 0.50) → 0.30 x 1.00 um
SIG_HW, SIG_HH = 0.15, 0.50
# ua[] analog pins: met4 (-0.45, -0.50) to (0.45, 0.50) → 0.90 x 1.00 um
ANA_HW, ANA_HH = 0.45, 0.50

PIN_TOP_Y = 225.260
PIN_BOT_Y = 0.500

# ua[] bottom-edge pins (from DEF)
UA_PINS = {
    "ua[0]": 152.260, "ua[1]": 132.940, "ua[2]": 113.620, "ua[3]": 94.300,
    "ua[4]": 74.980,  "ua[5]": 55.660,  "ua[6]": 36.340,  "ua[7]": 17.020,
}


def build():
    lib = gdstk.Library(name=CELL_NAME, unit=1e-6, precision=1e-9)

    # Generate the design
    design_cell, design_ports = gemm_tapeout_layout(lib)

    # Create the top-level wrapper cell
    top = lib.new_cell(CELL_NAME)

    # Instance the design into the wrapper (origin-to-origin, no offset)
    top.add(gdstk.Reference(design_cell))

    # Add DEF-matching pin rectangles on met4 at top edge
    for pin_name, pin_x in TT_PINS.items():
        top.add(gdstk.rectangle(
            (pin_x - SIG_HW, PIN_TOP_Y - SIG_HH),
            (pin_x + SIG_HW, PIN_TOP_Y + SIG_HH),
            **ld(L.MET4),
        ))
        top.add(gdstk.Label(
            pin_name, (pin_x, PIN_TOP_Y), layer=L.MET4[0], texttype=L.MET4[1],
        ))

    # Add DEF-matching ua[] pin rectangles at bottom edge (unused but required)
    for pin_name, pin_x in UA_PINS.items():
        top.add(gdstk.rectangle(
            (pin_x - ANA_HW, PIN_BOT_Y - ANA_HH),
            (pin_x + ANA_HW, PIN_BOT_Y + ANA_HH),
            **ld(L.MET4),
        ))
        top.add(gdstk.Label(
            pin_name, (pin_x, PIN_BOT_Y), layer=L.MET4[0], texttype=L.MET4[1],
        ))

    # Die boundary on PR boundary layer (236/0) — helps tools find the outline
    top.add(gdstk.rectangle((0, 0), (DIE_W, DIE_H), layer=236, datatype=0))

    # Export
    out_dir = os.path.join(os.path.dirname(__file__), "output", "gds")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{CELL_NAME}.gds")
    lib.write_gds(out_path)

    bb = top.bounding_box()
    print(f"Top cell: {CELL_NAME}")
    print(f"Design:   {design_cell.name} ({len(lib.cells)} cells total)")
    if bb is not None:
        print(f"BBox:     ({bb[0][0]:.2f}, {bb[0][1]:.2f}) to ({bb[1][0]:.2f}, {bb[1][1]:.2f})")
    print(f"Output:   {out_path}")
    return out_path


if __name__ == "__main__":
    build()
