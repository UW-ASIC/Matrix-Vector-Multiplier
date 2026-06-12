"""3x3 capacitive in-memory-computing crossbar layout.

Hierarchical gdstk layout:
  - crosspoint_cell(): single crosspoint with 4-bit binary-weighted cap array,
    CMOS switches, and inverters.
  - imc_crossbar_layout(): full 3x3 array with integration caps, reset circuitry,
    hierarchical routing, GND shields, and MET5 power straps.

Sky130 MIM caps on MET3/CAPM. Row inputs on MET3 horizontal, column outputs on
MET4 vertical, weight bits via MET4->MET3->MET2 hierarchical bus, power on MET5.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import gdstk

from project.layout.layers import L, ld
from project.layout.drc import DRC
from project.layout.ports import Port, add_port_label
from project.layout.compose import Instance
from project.layout.primitives.mosfet import nfet, pfet
from project.layout.primitives.contact import via_stack

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

N_ROWS = 3
N_COLS = 3
N_BITS = 4

# Target column pitch (um) -- shrunk to fit TT analog 2x2 die (334.88 um wide)
COL_PITCH = 80.0

# MIM cap construction: Sky130 MIM is CAPM between MET3 (bottom plate) and
# MET4 (top plate, on CAPM layer).  2 fF/um^2.
# Unit cap target ~50 fF => sqrt(50/2) ~ 5 um side
C_UNIT_SIDE = 4.8  # um -- default unit cap dimension

# Integration cap ~500 fF => sqrt(500/2) ~ 15.8 um
C_INT_SIDE = 15.8

# MOSFET dimensions for switches and inverters (um)
SW_N_W = 0.84    # switch NFET width
SW_N_L = 0.15
SW_P_W = 1.68    # switch PFET width
SW_P_L = 0.15
INV_N_W = 0.42   # inverter NFET width
INV_N_L = 0.15
INV_P_W = 0.84   # inverter PFET width
INV_P_L = 0.15

# Reset switch (wider for low on-resistance)
RST_N_W = 1.26
RST_N_L = 0.15
RST_P_W = 7.0
RST_P_L = 0.15


# ---------------------------------------------------------------------------
# MOSFET cell cache (avoid duplicate cell names in gdstk library)
# ---------------------------------------------------------------------------

_mosfet_cache: dict[str, tuple[gdstk.Cell, dict[str, Port]]] = {}


def _get_nfet(lib: gdstk.Library, w: float, l: float, nf: int = 1
              ) -> tuple[gdstk.Cell, dict[str, Port]]:
    """Get or create a shared NFET cell (cached by dimensions)."""
    key = f"nfet_{w}_{l}_{nf}"
    if key not in _mosfet_cache:
        _mosfet_cache[key] = nfet(lib, w, l, nf)
    return _mosfet_cache[key]


def _get_pfet(lib: gdstk.Library, w: float, l: float, nf: int = 1
              ) -> tuple[gdstk.Cell, dict[str, Port]]:
    """Get or create a shared PFET cell (cached by dimensions)."""
    key = f"pfet_{w}_{l}_{nf}"
    if key not in _mosfet_cache:
        _mosfet_cache[key] = pfet(lib, w, l, nf)
    return _mosfet_cache[key]


# ---------------------------------------------------------------------------
# Routing helpers (inline)
# ---------------------------------------------------------------------------

def _route_straight(cell: gdstk.Cell, layer: tuple[int, int],
                    p1: tuple[float, float], p2: tuple[float, float],
                    width: float) -> None:
    """Draw a straight metal wire (horizontal or vertical) between two points."""
    x1, y1 = p1
    x2, y2 = p2
    hw = width / 2

    if abs(y1 - y2) < 0.001:
        # Horizontal wire
        lo_x = min(x1, x2)
        hi_x = max(x1, x2)
        cell.add(gdstk.rectangle(
            (lo_x, y1 - hw), (hi_x, y1 + hw), **ld(layer)))
    elif abs(x1 - x2) < 0.001:
        # Vertical wire
        lo_y = min(y1, y2)
        hi_y = max(y1, y2)
        cell.add(gdstk.rectangle(
            (x1 - hw, lo_y), (x1 + hw, hi_y), **ld(layer)))
    else:
        # Diagonal -- draw as two-segment L (horizontal then vertical)
        _route_L(cell, layer, p1, p2, width)


def _route_L(cell: gdstk.Cell, layer: tuple[int, int],
             p1: tuple[float, float], p2: tuple[float, float],
             width: float) -> None:
    """Draw an L-shaped route: horizontal from p1 then vertical to p2."""
    x1, y1 = p1
    x2, y2 = p2
    hw = width / 2

    # Horizontal segment: (x1,y1) -> (x2,y1), extended +hw at corner to fill join
    lo_x = min(x1, x2)
    hi_x = max(x1, x2)
    if hi_x > lo_x:
        cell.add(gdstk.rectangle(
            (lo_x, y1 - hw), (hi_x + hw, y1 + hw), **ld(layer)))

    # Vertical segment: (x2,y1) -> (x2,y2)
    # Only extend hw toward the corner (y1), not past the far endpoint (y2).
    lo_y = min(y1, y2)
    hi_y = max(y1, y2)
    if hi_y > lo_y:
        if y2 > y1:
            # Corner at bottom of vertical segment
            cell.add(gdstk.rectangle(
                (x2 - hw, y1 - hw), (x2 + hw, y2), **ld(layer)))
        else:
            # Corner at top of vertical segment
            cell.add(gdstk.rectangle(
                (x2 - hw, y2), (x2 + hw, y1 + hw), **ld(layer)))


def _add_shield(cell: gdstk.Cell, layer: tuple[int, int],
                x: float, y_lo: float, y_hi: float,
                wire_w: float, shield_sp: float) -> None:
    """Add a pair of GND shield wires flanking a vertical track on the given layer."""
    hw = wire_w / 2
    # Left shield
    sx = x - shield_sp - wire_w
    cell.add(gdstk.rectangle(
        (sx - hw, y_lo), (sx + hw, y_hi), **ld(layer)))
    # Right shield
    sx = x + shield_sp + wire_w
    cell.add(gdstk.rectangle(
        (sx - hw, y_lo), (sx + hw, y_hi), **ld(layer)))


def _add_via3(cell: gdstk.Cell, cx: float, cy: float) -> None:
    """Add a VIA3 stack (MET3<->MET4) with proper enclosures at (cx, cy)."""
    # width=0.40: MET3 encl of VIA3 = (0.40-0.20)/2 = 0.10 >= 0.06 (via3.5)
    via_stack(cell, (cx, cy), L.MET3, L.MET4, width=0.40)


def _add_via2(cell: gdstk.Cell, cx: float, cy: float) -> None:
    """Add a VIA2 stack (MET2<->MET3) with proper enclosures at (cx, cy)."""
    # via_stack with default width gives MET3 pad = 0.33 (small, avoids capm.11)
    via_stack(cell, (cx, cy), L.MET2, L.MET3)
    # Add wider MET2 pad for via2.4a one-dir enclosure (>= 0.085)
    met2_w = DRC.VIA2_SZ + 2 * 0.09  # 0.20 + 0.18 = 0.38
    hw = met2_w / 2
    cell.add(gdstk.rectangle(
        (cx - hw, cy - hw), (cx + hw, cy + hw), **ld(L.MET2)))


def _add_via(cell: gdstk.Cell, cx: float, cy: float) -> None:
    """Add a VIA stack (MET1<->MET2) with proper enclosures at (cx, cy)."""
    # width=0.32: MET1/MET2 encl of VIA = (0.32-0.15)/2 = 0.085 (met2.5 one-dir)
    # MET1 area = 0.32^2 = 0.1024 >= 0.083 (met1.6)
    via_stack(cell, (cx, cy), L.MET1, L.MET2, width=0.32)


def _add_via4(cell: gdstk.Cell, cx: float, cy: float) -> None:
    """Add a VIA4 stack (MET4<->MET5) with proper enclosures at (cx, cy)."""
    via_stack(cell, (cx, cy), L.MET4, L.MET5)


# ---------------------------------------------------------------------------
# Crosspoint cell
# ---------------------------------------------------------------------------

def crosspoint_cell(lib: gdstk.Library, row: int, col: int,
                    n_bits: int = N_BITS,
                    c_unit_w: float = C_UNIT_SIDE,
                    c_unit_h: float = C_UNIT_SIDE
                    ) -> tuple[gdstk.Cell, dict[str, Port]]:
    """Generate a single crosspoint cell for position (row, col).

    Contains a 4-bit binary-weighted MIM cap array, per-bit CMOS switches, and
    per-bit inverters for complementary switch control.

    Vertical stacking (bottom to top):
        inverters -> switches -> caps (bit0 left, bit3 right)

    Ports (all in microns, relative to cell origin at lower-left):
        ROW_IN   MET3  -- horizontal row input (left edge, mid-height of switch region)
        COL_OUT  MET4  -- vertical column output (top of cap array, center)
        WB0..WB3 MET2  -- weight bit inputs (top edge, spaced per bit)
        VDD      MET1  -- power (top-right of inverter area)
        VSS      MET1  -- ground (bottom-left of inverter area)
    """
    cell_name = f"xpt_r{row}_c{col}"
    cell = lib.new_cell(cell_name)

    # --- Compute bit cap widths and cell dimensions ---
    bit_widths = [c_unit_w * (2 ** b) for b in range(n_bits)]  # 1,2,4,8 units
    bit_gap = DRC.CAPM_SP + 0.5  # inter-cap gap (CAPM spacing + LI margin)

    # Total cap array width
    cap_total_w = sum(bit_widths) + (n_bits - 1) * bit_gap

    # Vertical zone heights — sized for 0.50um poly pitch MOSFET cells
    # Switch NFET + PFET stacked height ~4.1um, need margin
    inv_zone_h = 3.5     # inverter pair (NFET + PFET stacked, ~2.9um + margin)
    sw_zone_h = 5.0      # switch pair (NFET + PFET stacked, ~4.1um + margin)
    # Gap between switches and caps: must fit VIA stack (MET1->MET2->MET3)
    # below CAPM with CAPM_SP_VIA2 (0.10um) clearance from CAPM edge
    cap_sw_gap = 2.5
    inv_sw_gap = 1.5     # gap between inverters and switches

    cell_h = inv_zone_h + inv_sw_gap + sw_zone_h + cap_sw_gap + c_unit_h
    cell_w = cap_total_w

    # Y coordinates for each zone
    inv_y0 = 0.0
    sw_y0 = inv_zone_h + inv_sw_gap
    cap_y0 = sw_y0 + sw_zone_h + cap_sw_gap

    # Minimum via pad sizes for DRC-clean connections
    via2_pad = DRC.VIA2_SZ + 2 * max(DRC.VIA2_ENCL_MET2, DRC.VIA2_ENCL_MET3)
    via_pad = DRC.VIA_SZ + 2 * max(DRC.VIA_ENCL_MET1, DRC.VIA_ENCL_MET2)
    drain_stub_hw = max(0.20, via2_pad / 2, via_pad / 2)  # half-width for drain stubs

    ports = {}

    # --- Per-bit: cap + switch pair + inverter ---
    bit_centers_x = []  # center x of each bit for port placement
    bx = 0.0
    for b in range(n_bits):
        bw = bit_widths[b]
        bcx = bx + bw / 2  # center of this bit column
        bit_centers_x.append(bcx)

        # --- MIM Cap ---
        encl = DRC.CAPM_ENCL_MET3
        # MET3 bottom plate (extends CAPM_ENCL_MET3 beyond CAPM in all directions)
        cell.add(gdstk.rectangle(
            (bx - encl, cap_y0 - encl),
            (bx + bw + encl, cap_y0 + c_unit_h + encl),
            **ld(L.MET3)))
        # CAPM marker
        cell.add(gdstk.rectangle(
            (bx, cap_y0), (bx + bw, cap_y0 + c_unit_h), **ld(L.CAPM)))
        # MET4 top plate
        cell.add(gdstk.rectangle(
            (bx, cap_y0), (bx + bw, cap_y0 + c_unit_h), **ld(L.MET4)))

        # --- VIA stack from switch drain to cap bottom plate ---
        # Place VIA2 (MET2->MET3) BELOW the MET3 plate, not overlapping CAPM.
        # CAPM starts at cap_y0; need CAPM_SP_VIA2 (0.10um) from CAPM edge.
        # VIA2 top edge must be at cap_y0 - CAPM_SP_VIA2 or lower.
        via2_y = cap_y0 - DRC.CAPM_SP_VIA2 - DRC.VIA2_SZ / 2 - 0.10
        # Extend MET3 bottom plate down to cover VIA2 landing pad
        met3_via2_bot = via2_y - max(DRC.VIA2_ENCL_MET3, via2_pad / 2)
        cell.add(gdstk.rectangle(
            (bcx - via2_pad / 2, met3_via2_bot),
            (bcx + via2_pad / 2, cap_y0 - encl),
            **ld(L.MET3)))

        # --- CMOS switch ---
        sw_mid_y = sw_y0 + sw_zone_h / 2

        # NFET (lower half of switch zone)
        sw_n_cell, sw_n_ports = _get_nfet(lib, SW_N_W, SW_N_L)
        sw_n_bb = sw_n_cell.bounding_box()
        sw_n_h = float(sw_n_bb[1][1] - sw_n_bb[0][1])
        nfet_y = sw_y0 + sw_zone_h * 0.25 - sw_n_h * 0.1
        sw_n_inst = Instance(sw_n_cell, sw_n_ports, name=f"sw_n_r{row}_c{col}_b{b}")
        sw_n_inst.place(bcx, nfet_y)
        sw_n_inst.add_to(cell)

        # PFET (upper half of switch zone)
        sw_p_cell, sw_p_ports = _get_pfet(lib, SW_P_W, SW_P_L)
        sw_p_bb = sw_p_cell.bounding_box()
        sw_p_h = float(sw_p_bb[1][1] - sw_p_bb[0][1])
        pfet_y = sw_y0 + sw_zone_h * 0.75 + sw_p_h * 0.1
        sw_p_inst = Instance(sw_p_cell, sw_p_ports, name=f"sw_p_r{row}_c{col}_b{b}")
        sw_p_inst.place(bcx, pfet_y)
        sw_p_inst.add_to(cell)

        # Switch drain connection up to cap bottom plate
        # MET1 from switch NFET D port up to VIA transition zone
        sw_n_drain_y = sw_n_inst.port("D").center[1]
        drain_x = bcx
        via_transition_y = via2_y - via2_pad / 2 - 0.1  # below VIA2 pad
        cell.add(gdstk.rectangle(
            (drain_x - drain_stub_hw, sw_n_drain_y),
            (drain_x + drain_stub_hw, via_transition_y + via_pad),
            **ld(L.MET1)))

        # VIA (MET1->MET2) using via_stack for proper enclosures
        via_y = sw_n_drain_y + via_pad / 2 + 0.1
        _add_via(cell, drain_x, via_y)

        # MET2 from VIA up to VIA2
        cell.add(gdstk.rectangle(
            (drain_x - drain_stub_hw, via_y - via_pad / 2),
            (drain_x + drain_stub_hw, via2_y + via2_pad / 2),
            **ld(L.MET2)))

        # VIA2 (MET2->MET3) using via_stack for proper enclosures
        _add_via2(cell, drain_x, via2_y)

        # --- Inverter ---
        inv_mid_y = inv_y0 + inv_zone_h / 2

        # Inverter NFET (lower half)
        inv_n_cell, inv_n_ports = _get_nfet(lib, INV_N_W, INV_N_L)
        inv_n_bb = inv_n_cell.bounding_box()
        inv_n_h = float(inv_n_bb[1][1] - inv_n_bb[0][1])
        inv_nfet_cy = inv_y0 + inv_zone_h * 0.25
        inv_n_inst = Instance(inv_n_cell, inv_n_ports, name=f"inv_n_r{row}_c{col}_b{b}")
        inv_n_inst.place(bcx, inv_nfet_cy)
        inv_n_inst.add_to(cell)

        # Inverter PFET (upper half)
        inv_p_cell, inv_p_ports = _get_pfet(lib, INV_P_W, INV_P_L)
        inv_p_bb = inv_p_cell.bounding_box()
        inv_p_h = float(inv_p_bb[1][1] - inv_p_bb[0][1])
        inv_pfet_cy = inv_y0 + inv_zone_h * 0.75
        inv_p_inst = Instance(inv_p_cell, inv_p_ports, name=f"inv_p_r{row}_c{col}_b{b}")
        inv_p_inst.place(bcx, inv_pfet_cy)
        inv_p_inst.add_to(cell)

        # MET1 inverter output -> switch PFET gate connection
        inv_p_top = inv_p_inst.port("D").center[1]
        met1_stub_hw = 0.17  # half-width: ensures area >= 0.083 um^2
        cell.add(gdstk.rectangle(
            (bcx - met1_stub_hw, inv_p_top),
            (bcx + met1_stub_hw, sw_y0),
            **ld(L.MET1)))

        # --- Weight-bit port (MET2, at top of cell for bus access) ---
        wb_port_y = cell_h + 0.5
        wb_w = DRC.MET2_W + 0.1
        # Place VIA (MET1->MET2) at the inverter NFET gate contact position.
        # The gate MET1 pad is above the S/D diffusion region, so there's no
        # met1.2 conflict with the nearby S/D MET1 pads (which are at y=0 in
        # MOSFET-local coords, well below the gate contact at gc_y).
        inv_gate_pos = inv_n_inst.port("G").center
        via_x = inv_gate_pos[0]
        via_y_wb = inv_gate_pos[1]
        # MET2 vertical drop from top to the gate VIA position
        cell.add(gdstk.rectangle(
            (bcx - wb_w / 2, via_y_wb),
            (bcx + wb_w / 2, wb_port_y),
            **ld(L.MET2)))
        # VIA from MET1 to MET2 at inverter gate contact (signal drops to gate)
        _add_via(cell, via_x, via_y_wb)

        ports[f"WB{b}"] = Port(
            f"WB{b}", (bcx, wb_port_y), wb_w, 90, L.MET2)

        bx += bw + bit_gap

    # --- ROW_IN port (MET3 horizontal, left edge, mid-height of switch zone) ---
    row_in_y = sw_y0 + sw_zone_h / 2
    row_in_w = DRC.MET3_W
    # MET3 stub from left edge across full cell width (connects to all switch sources)
    cell.add(gdstk.rectangle(
        (-1.0, row_in_y - row_in_w / 2),
        (cap_total_w + 1.0, row_in_y + row_in_w / 2),
        **ld(L.MET3)))

    ports["ROW_IN"] = Port(
        "ROW_IN", (-1.0, row_in_y), row_in_w, 180, L.MET3)

    # VIA2 drops from MET3 row wire to MET2->MET1 at each switch source
    for b in range(n_bits):
        bcx = bit_centers_x[b]
        _add_via2(cell, bcx, row_in_y)

    # --- COL_OUT port (MET4 vertical, top center of cap array) ---
    col_out_x = cap_total_w / 2
    col_out_y = cap_y0 + c_unit_h
    col_out_w = DRC.MET4_W

    # MET4 vertical stub extending above the cap tops for column bus connection
    cell.add(gdstk.rectangle(
        (col_out_x - col_out_w / 2, cap_y0),
        (col_out_x + col_out_w / 2, col_out_y + 1.5),
        **ld(L.MET4)))

    ports["COL_OUT"] = Port(
        "COL_OUT", (col_out_x, col_out_y + 1.5), col_out_w, 90, L.MET4)

    # --- VDD / VSS ports on MET1 ---
    # VSS at bottom-left
    vss_x = 0.3
    vss_y = 0.2
    vss_w = DRC.MET1_W * 3
    cell.add(gdstk.rectangle(
        (vss_x - vss_w / 2, vss_y - vss_w / 2),
        (vss_x + vss_w / 2, vss_y + vss_w / 2),
        **ld(L.MET1)))
    ports["VSS"] = Port("VSS", (vss_x, vss_y), vss_w, 270, L.MET1)

    # VDD at top of inverter PFET zone, right side
    vdd_x = cap_total_w - 0.3
    vdd_y = inv_zone_h - 0.2
    vdd_w = DRC.MET1_W * 3
    cell.add(gdstk.rectangle(
        (vdd_x - vdd_w / 2, vdd_y - vdd_w / 2),
        (vdd_x + vdd_w / 2, vdd_y + vdd_w / 2),
        **ld(L.MET1)))
    ports["VDD"] = Port("VDD", (vdd_x, vdd_y), vdd_w, 90, L.MET1)

    return cell, ports


# ---------------------------------------------------------------------------
# Full 4x4 crossbar
# ---------------------------------------------------------------------------

def imc_crossbar_layout(lib: gdstk.Library) -> tuple[gdstk.Cell, dict[str, Port]]:
    """Generate the complete 4x4 IMC crossbar layout.

    Architecture:
      - 16 crosspoint cells in a 4(row) x 4(col) grid
      - MET3 horizontal row input buses (in inter-row channels)
      - MET4 vertical column output buses
      - Weight-bit bus: MET4 vertical at left -> MET3 horizontal per row ->
        MET2 drops into each cell
      - Integration caps at bottom of each column
      - Reset switches + shared inverter below integration caps
      - GND shields on MET4 between columns
      - MET5 horizontal power straps (VDD and VSS)

    Returns:
        (top_cell, ports) with all external ports labeled.
    """
    top = lib.new_cell("imc_crossbar")
    ports = {}

    # --- Generate crosspoint sub-cells ---
    xpt_cells = {}   # (row, col) -> (cell, ports)
    xpt_insts = {}   # (row, col) -> Instance

    for i in range(N_ROWS):
        for j in range(N_COLS):
            xpt_cells[(i, j)] = crosspoint_cell(lib, i, j)

    # --- Compute crosspoint cell dimensions ---
    sample_cell, sample_ports = xpt_cells[(0, 0)]
    sample_bb = sample_cell.bounding_box()
    xpt_w = float(sample_bb[1][0] - sample_bb[0][0])
    xpt_h = float(sample_bb[1][1] - sample_bb[0][1])

    # Row channel height: must fit MET3 row bus + weight-bit MET3 horizontal
    # tracks (4 bits per row-col pair) without MET3 spacing violations.
    # 4 MET3 tracks need ~4*(MET3_W+MET3_SP) = 4*0.6 = 2.4um, plus row bus
    # and margins.  8.0um provides clean separation.
    row_channel = 12.0
    # Column group pitch (center-to-center)
    col_group_pitch = COL_PITCH

    # --- Placement grid ---
    col_origins = [j * col_group_pitch for j in range(N_COLS)]

    # Y origins for each row (row 0 at bottom, row 3 at top)
    row_origins = [i * (xpt_h + row_channel) for i in range(N_ROWS)]

    # Offset everything up to leave room for reset section at bottom
    reset_section_h = 30.0  # space for integration caps + reset switches
    row_y_offset = reset_section_h

    # --- Place crosspoint instances ---
    for i in range(N_ROWS):
        for j in range(N_COLS):
            xpt_cell, xpt_ports = xpt_cells[(i, j)]
            inst = Instance(xpt_cell, xpt_ports, name=f"Xxpt_{i}_{j}")

            px = col_origins[j]
            py = row_y_offset + row_origins[i]
            inst.place(px, py)
            inst.add_to(top)
            xpt_insts[(i, j)] = inst

    # --- Compute overall array bounds ---
    array_y_top = row_y_offset + row_origins[N_ROWS - 1] + xpt_h
    array_x_right = col_origins[N_COLS - 1] + xpt_w

    # =======================================================================
    # 1. Route row inputs (MET3 horizontal)
    # =======================================================================
    met3_w = DRC.MET3_W + 0.3  # wider for row bus

    for i in range(N_ROWS):
        # Row bus Y: in the channel below row i's crosspoints
        if i == 0:
            bus_y = row_y_offset - row_channel / 2
        else:
            bus_y = row_y_offset + row_origins[i] - row_channel / 2

        # Draw horizontal MET3 bus across full width + margin
        bus_x0 = col_origins[0] - 5.0
        bus_x1 = col_origins[N_COLS - 1] + xpt_w + 3.0
        _route_straight(top, L.MET3, (bus_x0, bus_y), (bus_x1, bus_y), met3_w)

        # Connect bus to each crosspoint's ROW_IN port via short MET3 stub
        for j in range(N_COLS):
            inst = xpt_insts[(i, j)]
            row_port = inst.port("ROW_IN")
            rp_x, rp_y = row_port.center
            _route_straight(top, L.MET3, (rp_x, bus_y), (rp_x, rp_y), met3_w)

        # Row input port at left edge
        port_name = f"x{i}"
        port_x = bus_x0
        ports[port_name] = Port(port_name, (port_x, bus_y), met3_w, 180, L.MET3)
        add_port_label(top, ports[port_name])

    # =======================================================================
    # 2. Route column outputs (MET4 vertical)
    # =======================================================================
    met4_w = DRC.MET4_W + 0.3  # wider for column bus

    col_bus_x = []  # X position of each column's vertical bus
    for j in range(N_COLS):
        bus_x = col_origins[j] + xpt_w / 2
        col_bus_x.append(bus_x)

        bus_y0 = 0.0
        bus_y1 = array_y_top + 3.0
        _route_straight(top, L.MET4, (bus_x, bus_y0), (bus_x, bus_y1), met4_w)

        # Connect bus to each crosspoint's COL_OUT port
        for i in range(N_ROWS):
            inst = xpt_insts[(i, j)]
            col_port = inst.port("COL_OUT")
            cp_x, cp_y = col_port.center
            if abs(cp_x - bus_x) > 0.01:
                _route_straight(top, L.MET4, (cp_x, cp_y), (bus_x, cp_y), met4_w)

        # Column output port at top
        port_name = f"y{j}"
        ports[port_name] = Port(port_name, (bus_x, bus_y1), met4_w, 90, L.MET4)
        add_port_label(top, ports[port_name])

    # =======================================================================
    # 3. Route weight-bit bus (MET4 vertical -> MET3 horizontal -> MET2 drop)
    # =======================================================================
    # Weight-bit vertical bus on MET4 at the left edge of the array.
    # 64 signals: wb_ijb for i=0..3, j=0..3, b=0..3
    # Safe pitch: MET4_W + 2*MET4_SP to avoid spacing violations between
    # adjacent wire edges AND via landing pads.
    wb_met4_w = DRC.MET4_W
    wb_met4_pitch = DRC.MET4_W + 2 * DRC.MET4_SP + 0.40  # 1.30um: extra margin for VIA3 pads at L-route corners

    # Weight bus starts to the left of the array
    wb_bus_x0 = col_origins[0] - 8.0

    wb_idx = 0
    for i in range(N_ROWS):
        for j in range(N_COLS):
            for b in range(N_BITS):
                # Vertical MET4 track position
                wb_x = wb_bus_x0 - wb_idx * wb_met4_pitch
                wb_name = f"wb_{i}{j}{b}"

                # MET4 vertical from bottom to row i's channel
                if i == 0:
                    target_y = row_y_offset - row_channel / 2 + 1.5
                else:
                    target_y = row_y_offset + row_origins[i] - row_channel / 2 + 1.5

                _route_straight(top, L.MET4,
                                (wb_x, -2.0), (wb_x, target_y + 1.0),
                                wb_met4_w)

                # VIA3 at the turn point (MET4 -> MET3)
                _add_via3(top, wb_x, target_y)

                # MET3 horizontal from wb_x to target cell's WB port X
                inst = xpt_insts[(i, j)]
                wb_port = inst.port(f"WB{b}")
                wp_x, wp_y = wb_port.center

                met3_bus_w = DRC.VIA3_SZ + 2 * DRC.VIA3_ENCL_MET3 + 0.10  # >= 0.42 for via3.5
                # Offset each bit's MET3 horizontal to avoid shorts
                h_y = target_y + b * (met3_bus_w + DRC.MET3_SP)
                _route_straight(top, L.MET3, (wb_x, h_y), (wp_x, h_y), met3_bus_w)

                # MET3 jog from VIA3 to offset horizontal
                if b > 0:
                    _route_straight(top, L.MET3,
                                    (wb_x, target_y), (wb_x, h_y), met3_bus_w)

                # VIA2 at the cell entry point (MET3 -> MET2)
                _add_via2(top, wp_x, h_y)

                # MET2 vertical drop from h_y to the cell's WB port
                _route_straight(top, L.MET2,
                                (wp_x, h_y), (wp_x, wp_y), DRC.MET2_W)

                # External port at bottom of MET4 vertical bus
                ports[wb_name] = Port(
                    wb_name, (wb_x, -2.0), wb_met4_w, 270, L.MET4)
                add_port_label(top, ports[wb_name])

                wb_idx += 1

    # =======================================================================
    # 4. Integration caps at bottom of each column
    # =======================================================================
    cint_w = C_INT_SIDE
    cint_h = C_INT_SIDE
    cint_encl = DRC.CAPM_ENCL_MET3
    cint_y0 = 2.0  # base Y for integration caps

    for j in range(N_COLS):
        # Center integration cap under the column bus
        cint_cx = col_bus_x[j]
        cint_x0 = cint_cx - cint_w / 2
        cint_x1 = cint_cx + cint_w / 2

        # MET3 bottom plate
        top.add(gdstk.rectangle(
            (cint_x0 - cint_encl, cint_y0 - cint_encl),
            (cint_x1 + cint_encl, cint_y0 + cint_h + cint_encl),
            **ld(L.MET3)))
        # CAPM
        top.add(gdstk.rectangle(
            (cint_x0, cint_y0), (cint_x1, cint_y0 + cint_h),
            **ld(L.CAPM)))
        # MET4 top plate (connects to column output bus)
        top.add(gdstk.rectangle(
            (cint_x0, cint_y0), (cint_x1, cint_y0 + cint_h),
            **ld(L.MET4)))

        # VIA3 array connecting MET3 bottom plate to column bus.
        # Place VIA3s along right edge of the MET3 plate, but offset
        # inward from CAPM edge by CAPM_SP_VIA3 to avoid capm.8 violations.
        v3_margin = DRC.CAPM_SP_VIA3 + DRC.VIA3_SZ / 2 + 0.12
        v3_x = cint_x1 - v3_margin
        v3_y_start = cint_y0 + v3_margin
        v3_y_end = cint_y0 + cint_h - v3_margin
        v3_y = v3_y_start
        while v3_y <= v3_y_end:
            _add_via3(top, v3_x, v3_y)
            v3_y += DRC.VIA3_SZ + DRC.VIA3_SP

    # =======================================================================
    # 5. Reset switches + shared inverter (below integration caps)
    # =======================================================================
    rst_y0 = cint_y0 - 6.0  # below integration caps

    # Shared reset inverter (leftmost position)
    rst_inv_x = col_origins[0] - 3.0
    rst_inv_y = rst_y0

    # Reset inverter NFET
    rst_inv_n_cell, rst_inv_n_ports = _get_nfet(lib, INV_N_W, INV_N_L)
    rst_inv_n = Instance(rst_inv_n_cell, rst_inv_n_ports, name="rst_inv_n")
    rst_inv_n.place(rst_inv_x, rst_inv_y + INV_N_W / 2)
    rst_inv_n.add_to(top)

    # Reset inverter PFET (above NFET)
    rst_inv_p_cell, rst_inv_p_ports = _get_pfet(lib, INV_P_W, INV_P_L)
    rst_inv_p = Instance(rst_inv_p_cell, rst_inv_p_ports, name="rst_inv_p")
    rst_inv_p.place(rst_inv_x, rst_inv_y + INV_N_W + 0.5 + INV_P_W / 2)
    rst_inv_p.add_to(top)

    # Per-column reset switches (CMOS TG between column output and VSS)
    rst_n_cell, rst_n_ports = _get_nfet(lib, RST_N_W, RST_N_L)
    rst_p_cell, rst_p_ports = _get_pfet(lib, RST_P_W, RST_P_L)
    rst_n_bb = rst_n_cell.bounding_box()
    rst_n_h = float(rst_n_bb[1][1] - rst_n_bb[0][1])
    rst_p_bb = rst_p_cell.bounding_box()
    rst_p_h = float(rst_p_bb[1][1] - rst_p_bb[0][1])

    for j in range(N_COLS):
        sw_x = col_bus_x[j] - 1.0
        sw_y = rst_y0

        # Reset NFET
        rst_n_inst = Instance(rst_n_cell, rst_n_ports, name=f"rst_n_{j}")
        rst_n_inst.place(sw_x, sw_y + rst_n_h / 2)
        rst_n_inst.add_to(top)

        # Reset PFET (above NFET with gap)
        rst_p_y = sw_y + rst_n_h + 0.5 + rst_p_h / 2
        rst_p_inst = Instance(rst_p_cell, rst_p_ports, name=f"rst_p_{j}")
        rst_p_inst.place(sw_x, rst_p_y)
        rst_p_inst.add_to(top)

        # MET1 connection from reset switch drain to column bus via MET2/VIA
        rst_drain_x = col_bus_x[j]
        rst_drain_y = rst_n_inst.port("D").center[1]
        top.add(gdstk.rectangle(
            (rst_drain_x - 0.15, rst_drain_y),
            (rst_drain_x + 0.15, cint_y0 - cint_encl),
            **ld(L.MET1)))

    # =======================================================================
    # 6. GND shields between columns (MET4 vertical)
    # =======================================================================
    shield_w = DRC.MET4_W
    shield_y_lo = -5.0
    shield_y_hi = array_y_top + 5.0

    for j in range(N_COLS - 1):
        shield_x = (col_bus_x[j] + col_bus_x[j + 1]) / 2
        _route_straight(top, L.MET4,
                        (shield_x, shield_y_lo),
                        (shield_x, shield_y_hi),
                        shield_w)

    # Outer shields at left and right edges
    _route_straight(top, L.MET4,
                    (col_bus_x[0] - col_group_pitch * 0.4, shield_y_lo),
                    (col_bus_x[0] - col_group_pitch * 0.4, shield_y_hi),
                    shield_w)
    _route_straight(top, L.MET4,
                    (col_bus_x[N_COLS - 1] + col_group_pitch * 0.4, shield_y_lo),
                    (col_bus_x[N_COLS - 1] + col_group_pitch * 0.4, shield_y_hi),
                    shield_w)

    # =======================================================================
    # 7. MET5 horizontal power straps
    # =======================================================================
    met5_w = DRC.MET5_W
    met5_sp = DRC.MET5_SP
    met5_pitch = met5_w + met5_sp

    pwr_x0 = col_origins[0] - 10.0
    pwr_x1 = col_origins[N_COLS - 1] + xpt_w + 10.0

    strap_y = rst_y0 - 3.0
    strap_idx = 0
    while strap_y < array_y_top + 5.0:
        is_vdd = (strap_idx % 2 == 0)
        _route_straight(top, L.MET5, (pwr_x0, strap_y), (pwr_x1, strap_y), met5_w)

        for j in range(N_COLS):
            via4_x = col_bus_x[j] + (3.0 if is_vdd else -3.0)
            _add_via4(top, via4_x, strap_y)

        strap_y += met5_pitch
        strap_idx += 1

    # VDD and VSS top-level ports
    first_vdd_y = rst_y0 - 3.0
    first_vss_y = first_vdd_y + met5_pitch
    ports["vdd"] = Port("vdd", (pwr_x0, first_vdd_y), met5_w, 180, L.MET5)
    ports["vss"] = Port("vss", (pwr_x0, first_vss_y), met5_w, 180, L.MET5)
    add_port_label(top, ports["vdd"])
    add_port_label(top, ports["vss"])

    # =======================================================================
    # 8. RST port
    # =======================================================================
    rst_port_x = rst_inv_x - 1.0
    rst_port_y = rst_y0 + INV_N_W / 2
    _route_straight(top, L.MET2,
                    (rst_port_x, rst_port_y),
                    (rst_inv_x, rst_port_y),
                    DRC.MET2_W)
    ports["rst"] = Port("rst", (rst_port_x, rst_port_y), DRC.MET2_W, 180, L.MET2)
    add_port_label(top, ports["rst"])

    return top, ports


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    lib = gdstk.Library("imc_crossbar")

    top, ports = imc_crossbar_layout(lib)

    # Summary
    bb = top.bounding_box()
    if bb is not None:
        w_um = bb[1][0] - bb[0][0]
        h_um = bb[1][1] - bb[0][1]
        print(f"IMC crossbar: {w_um:.1f} x {h_um:.1f} um")
    else:
        print("IMC crossbar: no geometry (empty bounding box)")

    print(f"Ports ({len(ports)}):")
    for name, port in sorted(ports.items()):
        print(f"  {name:12s}  layer={port.layer}  center=({port.center[0]:.1f}, "
              f"{port.center[1]:.1f})  width={port.width:.2f}")

    # Count cells
    print(f"Sub-cells: {len(lib.cells) - 1}")  # exclude top

    out_path = os.path.join(os.path.dirname(__file__), "..", "..", "..",
                            "imc_crossbar_layout.gds")
    out_path = os.path.normpath(out_path)
    lib.write_gds(out_path)
    print(f"Exported {out_path}")
