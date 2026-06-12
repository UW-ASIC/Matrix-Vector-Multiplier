"""Layout for 4-bit charge-redistribution DAC.

Architecture:
  - 6x6 MIM cap array (4x4 common-centroid core + 1-ring dummy border)
  - Switch row (4x CMOS TG pairs: sw_hi to vref, sw_lo to vss) below cap array
  - Inverter row below switches
  - MET4 top-plate bus, MET2/MET5 shield planes
  - Ports: vref, b0-b3, out, vdd, vss

All dimensions in microns.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import gdstk

from project.layout.layers import L, ld
from project.layout.drc import DRC
from project.layout.ports import Port, add_port_label
from project.layout.primitives.mosfet import nfet, pfet
from project.layout.primitives.contact import via_stack

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

N_BITS = 4
C_UNIT_FF = 50.0           # fF per unit cap
MIM_AREA_CAP = DRC.MIM_AREA_CAP   # 2.0 fF/um^2
MIM_PERI_CAP = 0.19        # fF/um (fringe)

# Solve for unit cap side length:
#   C_UNIT = MIM_AREA_CAP * s^2 + MIM_PERI_CAP * 4 * s
#   2*s^2 + 0.76*s - 50 = 0  =>  s ~ 4.82 um
# Round to 4.85 for a clean number and slight margin.
CAP_SIDE = 4.85            # active CAPM side (um)

# MET3 bottom plate oversizes CAPM by enclosure rule
MET3_ENCL = DRC.CAPM_ENCL_MET3   # 0.14 um
BOT_SIDE = CAP_SIDE + 2 * MET3_ENCL  # MET3 bottom plate side

# MET4 top plate is the connection from top; CAPM sits between MET3 and MET4.
# For the top-plate connection we place a MET4 rectangle on top of CAPM.
# VIA3 connects MET3 (bot) to MET4 (top) — but for MIM, top plate IS MET4 natively.
# So we just need VIA3 for bottom-plate escapes.

# Array pitch: BOT_SIDE + spacing between MET3 bottom plates
# capm.11: 1.34 um spacing from CAPM to *unrelated* MET3
# But within our array, adjacent caps share the same top plate (MET4),
# so the CAPM-to-CAPM spacing rule (capm.1b = 0.84 um) applies.
CAPM_SP = DRC.CAPM_SP      # 0.84 um min CAPM spacing
CAP_PITCH = BOT_SIDE + CAPM_SP  # pitch between cap cell origins

# Grid: 6x6 (4x4 core + 1-ring dummy)
GRID = 6

# ---------------------------------------------------------------------------
# Common-centroid assignment for 4x4 core (indices 1..4 in 6x6)
# Each cell is (bit_index) or -1 for dummy.
# Bit 3 = 8C (8 units), Bit 2 = 4C (4 units), Bit 1 = 2C (2 units),
# Bit 0 = 1C (1 unit), D = dummy.
# ---------------------------------------------------------------------------

# 4x4 core assignment (row 0 = bottom):
#   row3: 8a  4a  2a  8b     =>  3, 2, 1, 3
#   row2: 4b  8c  0   8d     =>  2, 3, 0, 3
#   row1: 8e  D0  8f  4c     =>  3,-1, 3, 2
#   row0: 8g  2b  4d  8h     =>  3, 1, 2, 3

CORE_MAP = [
    [3, 1, 2, 3],   # row 0 (bottom)
    [3, -1, 3, 2],  # row 1
    [2, 3, 0, 3],   # row 2
    [3, 2, 1, 3],   # row 3 (top)
]
# -1 = dummy in core

# ---------------------------------------------------------------------------
# MOSFET dimensions (from PDK sizing, in microns)
# ---------------------------------------------------------------------------

# DAC switch: W_N=1.68, W_P=3.36, L=0.15
SW_WN = 1.68
SW_WP = 3.36
SW_L = 0.15

# Inverter: W_N=0.42, W_P=0.84, L=0.15
INV_WN = 0.42
INV_WP = 0.84
INV_L = 0.15


# ---------------------------------------------------------------------------
# Primitive cell builders
# ---------------------------------------------------------------------------

def _mim_cap_cell(lib: gdstk.Library, name: str,
                  side: float = CAP_SIDE) -> tuple[gdstk.Cell, dict[str, Port]]:
    """Create a single MIM capacitor cell.

    Structure (bottom to top):
      MET3  — bottom plate (full cell)
      CAPM  — capacitor dielectric marker
      MET4  — top plate (full cell, extends to array bus)

    Ports:
      BOT — MET3 center, faces south (for escape routing)
      TOP — MET4 center, faces north
    """
    cell = lib.new_cell(name)
    met3_half = (side + 2 * MET3_ENCL) / 2
    capm_half = side / 2

    # MET3 bottom plate
    cell.add(gdstk.rectangle(
        (-met3_half, -met3_half), (met3_half, met3_half), **ld(L.MET3)))

    # CAPM dielectric layer
    cell.add(gdstk.rectangle(
        (-capm_half, -capm_half), (capm_half, capm_half), **ld(L.CAPM)))

    # MET4 top plate (same size as MET3 for now; bus will be a separate overlay)
    cell.add(gdstk.rectangle(
        (-met3_half, -met3_half), (met3_half, met3_half), **ld(L.MET4)))

    ports = {
        "BOT": Port("BOT", (0.0, 0.0), met3_half, 270.0, L.MET3),
        "TOP": Port("TOP", (0.0, 0.0), met3_half, 90.0, L.MET4),
    }
    return cell, ports


# ---------------------------------------------------------------------------
# Main layout function
# ---------------------------------------------------------------------------

def charge_dac_layout(lib: gdstk.Library) -> tuple[gdstk.Cell, dict[str, Port]]:
    """Build the 4-bit charge-redistribution DAC layout.

    Returns:
        (cell, ports) where ports is a dict mapping port names to Port objects.
    """
    top = lib.new_cell("charge_dac")

    # ------------------------------------------------------------------
    # 1. Create primitive cells
    # ------------------------------------------------------------------
    cap_cell, cap_ports = _mim_cap_cell(lib, "dac_mim_unit")
    dummy_cell, _ = _mim_cap_cell(lib, "dac_mim_dummy")
    # For dummy caps, short both plates to VSS via VIA3 (added during placement)

    # MOSFET cells for switches
    sw_n_cell, sw_n_ports = nfet(lib, SW_WN, SW_L, name="dac_sw_nfet")
    sw_p_cell, sw_p_ports = pfet(lib, SW_WP, SW_L, name="dac_sw_pfet")

    # MOSFET cells for inverters
    inv_n_cell, inv_n_ports = nfet(lib, INV_WN, INV_L, name="dac_inv_nfet")
    inv_p_cell, inv_p_ports = pfet(lib, INV_WP, INV_L, name="dac_inv_pfet")

    # ------------------------------------------------------------------
    # 2. Place 6x6 capacitor array
    # ------------------------------------------------------------------
    # Array origin: bottom-left cap center
    # Total array dimensions: GRID * CAP_PITCH
    array_w = GRID * CAP_PITCH
    array_h = GRID * CAP_PITCH

    # Center the array horizontally in the cell; place it in upper portion
    # Leave room below for switches + inverters (~20 um)
    routing_channel_h = 7.0  # MET1/MET2 routing between caps and switches
    switch_row_h = 8.0        # height for switch transistors (increased for diff/tap.9)
    inv_row_h = 6.0           # height for inverters (increased for diff/tap.9)
    vss_rail_h = 1.0          # bottom VSS rail
    vdd_rail_h = 1.0          # VDD rail between inv and switches

    bottom_margin = vss_rail_h + inv_row_h + vdd_rail_h + switch_row_h + routing_channel_h
    array_y0 = bottom_margin + CAP_PITCH / 2  # y of row 0 cap centers

    # x origin: center array at x = array_w/2 (so leftmost cap center at CAP_PITCH/2)
    array_x0 = CAP_PITCH / 2

    # Track which caps belong to which bit for bottom-plate routing
    # bit_caps[bit] = list of (grid_col, grid_row) in 6x6 coordinates
    bit_caps = {i: [] for i in range(N_BITS)}
    dummy_positions = []

    for row in range(GRID):
        for col in range(GRID):
            cx = array_x0 + col * CAP_PITCH
            cy = array_y0 + row * CAP_PITCH

            # Determine if this is core or border
            is_border = (row == 0 or row == GRID - 1 or
                         col == 0 or col == GRID - 1)

            if is_border:
                # Dummy cap
                ref = gdstk.Reference(dummy_cell, origin=(cx, cy))
                top.add(ref)
                dummy_positions.append((cx, cy))
            else:
                # Core cell: map to 4x4 core indices
                core_r = row - 1  # 0..3
                core_c = col - 1  # 0..3
                bit_idx = CORE_MAP[core_r][core_c]

                if bit_idx < 0:
                    # Dummy in core
                    ref = gdstk.Reference(dummy_cell, origin=(cx, cy))
                    top.add(ref)
                    dummy_positions.append((cx, cy))
                else:
                    ref = gdstk.Reference(cap_cell, origin=(cx, cy))
                    top.add(ref)
                    bit_caps[bit_idx].append((cx, cy))

    # ------------------------------------------------------------------
    # 3. MET4 top-plate bus (solid plane over entire array)
    # ------------------------------------------------------------------
    # All cap top plates connect to output via this bus.
    tp_margin = 0.5  # extend beyond outermost cap edges
    tp_left = array_x0 - BOT_SIDE / 2 - tp_margin
    tp_right = array_x0 + (GRID - 1) * CAP_PITCH + BOT_SIDE / 2 + tp_margin
    tp_bot = array_y0 - BOT_SIDE / 2 - tp_margin
    tp_top = array_y0 + (GRID - 1) * CAP_PITCH + BOT_SIDE / 2 + tp_margin

    top.add(gdstk.rectangle(
        (tp_left, tp_bot), (tp_right, tp_top), **ld(L.MET4)))

    # ------------------------------------------------------------------
    # 4. Route bottom plates per bit down to routing channel
    # ------------------------------------------------------------------
    # Strategy: for each bit, run MET2 vertical straps from each cap's
    # bottom plate (via VIA2 from MET3 down to MET2), merge into a
    # horizontal MET1 bus in the routing channel, then down to switch.

    # Routing channel sits between cap array bottom edge and switch row
    rc_top = array_y0 - CAP_PITCH / 2 - 0.5  # top of routing channel
    rc_bot = rc_top - routing_channel_h        # bottom of routing channel

    # Assign each bit a horizontal track in the routing channel
    track_pitch = routing_channel_h / (N_BITS + 1)
    bit_track_y = {}
    for i in range(N_BITS):
        bit_track_y[i] = rc_bot + (i + 1) * track_pitch

    # MET1 bus width — at least 0.28 um to satisfy met1.2 with adjacent wires
    bus_w = max(0.28, DRC.MET1_W * 2)  # 0.28 um

    # Offset for via_stack away from CAPM edge to satisfy capm.8 (CAPM-to-VIA2 >= 0.10 um)
    # Place the VIA2 escape near the bottom edge of the MET3 plate, outside CAPM.
    # Add 0.05 um safety margin beyond minimum to avoid marginal violations.
    capm_half = CAP_SIDE / 2
    via2_offset_y = -(capm_half + DRC.CAPM_SP_VIA2 + DRC.VIA2_SZ / 2 + 0.05)  # below CAPM

    # MET2 strap width: must enclose VIA2 by at least 0.045 um in both directions (via2.4a)
    # and also enclose VIA by VIA_ENCL_MET2 for the lower via stack
    strap_w = max(DRC.VIA2_SZ + 2 * DRC.VIA2_ENCL_MET2 + 0.10,
                  DRC.VIA_SZ + 2 * DRC.VIA_ENCL_MET2 + 0.10)

    for bit in range(N_BITS):
        track_y = bit_track_y[bit]
        positions = bit_caps[bit]

        # Horizontal MET1 bus for this bit across the array
        xs = [p[0] for p in positions]
        bus_left = min(xs) - BOT_SIDE / 4
        bus_right = max(xs) + BOT_SIDE / 4
        top.add(gdstk.rectangle(
            (bus_left, track_y - bus_w / 2),
            (bus_right, track_y + bus_w / 2),
            **ld(L.MET1)))

        for (cx, cy) in positions:
            # VIA2: MET3 (bottom plate) -> MET2 escape strap
            # Offset below CAPM edge to satisfy capm.8 spacing rule
            via_y = cy + via2_offset_y
            via_stack(top, (cx, via_y), L.MET2, L.MET3,
                      width=DRC.VIA2_SZ + 2 * 0.065)

            # MET2 vertical strap from via down to routing channel
            top.add(gdstk.rectangle(
                (cx - strap_w / 2, track_y - bus_w / 2),
                (cx + strap_w / 2, via_y + DRC.VIA2_SZ / 2 + DRC.VIA2_ENCL_MET2),
                **ld(L.MET2)))

            # VIA at bottom of strap: MET2 -> MET1
            # Use explicit width to ensure MET2 landing pad meets met2.5
            via_stack(top, (cx, track_y), L.MET1, L.MET2,
                      width=DRC.VIA_SZ + 2 * DRC.VIA_ENCL_MET2 + 0.04)

    # ------------------------------------------------------------------
    # 5. Dummy cap bottom-plate grounding
    # ------------------------------------------------------------------
    # Short dummy bottom plates (MET3) to VSS via VIA2->MET2 to ground plane.
    # Offset VIA2 below CAPM edge (capm.8) like the core caps.
    for (dx, dy) in dummy_positions:
        via_stack(top, (dx, dy + via2_offset_y), L.MET2, L.MET3,
                  width=DRC.VIA2_SZ + 2 * 0.065)

    # ------------------------------------------------------------------
    # 6. Place switch rows below routing channel
    # ------------------------------------------------------------------
    # For each bit: sw_hi (CMOS TG to vref) and sw_lo (CMOS TG to vss)
    # Each TG = NFET + PFET pair
    # Layout: N on bottom, P on top for each TG; two TGs side by side per bit

    sw_row_y = rc_bot - 1.0  # center y of switch NFET row
    sw_p_offset_y = 4.0      # PFET row offset above NFET row (increased for diff/tap.9 + poly.7)

    # Horizontal spacing: spread 4 bits across array width
    sw_pitch = array_w / N_BITS  # one bit's horizontal allocation
    sw_tg_sep = 4.0              # separation between hi and lo TGs (increased for LI1 spacing)

    switch_positions = {}  # bit -> {"hi_n": (x,y), "hi_p": (x,y), "lo_n": (x,y), ...}

    for bit in range(N_BITS):
        bx = array_x0 + bit * sw_pitch + sw_pitch / 2  # bit center x

        # sw_hi (connects to vref)
        hi_n_x = bx - sw_tg_sep / 2
        hi_n_y = sw_row_y
        hi_p_y = sw_row_y + sw_p_offset_y

        top.add(gdstk.Reference(sw_n_cell, origin=(hi_n_x, hi_n_y)))
        top.add(gdstk.Reference(sw_p_cell, origin=(hi_n_x, hi_p_y)))

        # sw_lo (connects to vss)
        lo_n_x = bx + sw_tg_sep / 2
        lo_n_y = sw_row_y
        lo_p_y = sw_row_y + sw_p_offset_y

        top.add(gdstk.Reference(sw_n_cell, origin=(lo_n_x, lo_n_y)))
        top.add(gdstk.Reference(sw_p_cell, origin=(lo_n_x, lo_p_y)))

        switch_positions[bit] = {
            "hi_n": (hi_n_x, hi_n_y), "hi_p": (hi_n_x, hi_p_y),
            "lo_n": (lo_n_x, lo_n_y), "lo_p": (lo_n_x, lo_p_y),
        }

    # ------------------------------------------------------------------
    # Connect switch drains to bottom-plate bus in routing channel
    # ------------------------------------------------------------------
    # Wire width for switch-to-channel routing
    sw_wire_w = max(0.28, DRC.MET1_W * 2)  # 0.28 um

    for bit in range(N_BITS):
        track_y = bit_track_y[bit]
        sp = switch_positions[bit]

        # Both sw_hi and sw_lo drain connect to cap_bot (same node)
        for key in ("hi_n", "lo_n"):
            sx, sy = sp[key]
            drn_x = sx + sw_n_ports["D"].center[0]
            drn_y = sy + sw_n_ports["D"].center[1]

            # MET1 vertical from switch drain up to track
            top.add(gdstk.rectangle(
                (drn_x - sw_wire_w / 2, drn_y),
                (drn_x + sw_wire_w / 2, track_y + bus_w / 2),
                **ld(L.MET1)))

    # ------------------------------------------------------------------
    # 7. Place inverter row below switches
    # ------------------------------------------------------------------
    inv_row_y = sw_row_y - switch_row_h  # NFET center
    inv_p_offset = 3.0                    # PFET above NFET (increased for diff/tap.9 + poly.7)

    inverter_positions = {}  # bit -> {"n": (x,y), "p": (x,y)}

    for bit in range(N_BITS):
        bx = array_x0 + bit * sw_pitch + sw_pitch / 2
        inv_nx = bx
        inv_ny = inv_row_y
        inv_py = inv_row_y + inv_p_offset

        top.add(gdstk.Reference(inv_n_cell, origin=(inv_nx, inv_ny)))
        top.add(gdstk.Reference(inv_p_cell, origin=(inv_nx, inv_py)))

        inverter_positions[bit] = {"n": (inv_nx, inv_ny), "p": (inv_nx, inv_py)}

    # ------------------------------------------------------------------
    # Connect inverter outputs to switch gates
    # ------------------------------------------------------------------
    # The inverter output must reach the switch gate, but the vertical
    # path crosses the VDD MET1 rail.  Use MET2 to bridge over it.
    inv_wire_w = max(0.28, DRC.MET1_W * 2)  # 0.28 um minimum
    # Clearance margin from VDD rail edges for the MET2 bridge
    vdd_clear = DRC.MET1_SP + 0.10  # spacing + margin

    for bit in range(N_BITS):
        inv_pos = inverter_positions[bit]
        sp = switch_positions[bit]

        # Inverter output = drain of both inv_n and inv_p (connected at inv center)
        inv_out_x = inv_pos["n"][0] + inv_n_ports["D"].center[0]
        inv_drn_n_y = inv_pos["n"][1] + inv_n_ports["D"].center[1]
        sw_gate_y = sp["hi_n"][1] + sw_n_ports["G"].center[1]

        # MET1 segment below VDD rail: inverter drain up to just below VDD rail
        m1_below_top = vdd_y - vss_rail_w / 2 - vdd_clear
        top.add(gdstk.rectangle(
            (inv_out_x - inv_wire_w / 2, inv_drn_n_y),
            (inv_out_x + inv_wire_w / 2, m1_below_top),
            **ld(L.MET1)))

        # MET1 segment above VDD rail: just above VDD rail up to switch gate
        m1_above_bot = vdd_y + vss_rail_w / 2 + vdd_clear
        top.add(gdstk.rectangle(
            (inv_out_x - inv_wire_w / 2, m1_above_bot),
            (inv_out_x + inv_wire_w / 2, sw_gate_y),
            **ld(L.MET1)))

        # MET2 bridge over VDD rail: connect the two MET1 segments
        top.add(gdstk.rectangle(
            (inv_out_x - inv_wire_w / 2, m1_below_top - inv_wire_w / 2),
            (inv_out_x + inv_wire_w / 2, m1_above_bot + inv_wire_w / 2),
            **ld(L.MET2)))

        # Vias at bottom and top of MET2 bridge
        via_stack(top, (inv_out_x, m1_below_top), L.MET1, L.MET2)
        via_stack(top, (inv_out_x, m1_above_bot), L.MET1, L.MET2)

    # ------------------------------------------------------------------
    # Connect switch sources: sw_hi to VREF, sw_lo to VSS
    # ------------------------------------------------------------------
    # Standard wire width for power connections
    wire_w = max(0.28, DRC.MET1_W * 2)  # 0.28 um minimum

    # VREF bus: horizontal MET2 bus running across all sw_hi sources
    vref_y = sw_row_y - 1.5
    vref_w = 0.50
    vref_left = array_x0 - 1.0
    vref_right = array_x0 + (GRID - 1) * CAP_PITCH + 1.0

    top.add(gdstk.rectangle(
        (vref_left, vref_y - vref_w / 2),
        (vref_right, vref_y + vref_w / 2),
        **ld(L.MET2)))

    for bit in range(N_BITS):
        sp = switch_positions[bit]
        # sw_hi source -> VREF via MET1 down to MET2 bus
        src_x = sp["hi_n"][0] + sw_n_ports["S"].center[0]
        src_y = sp["hi_n"][1] + sw_n_ports["S"].center[1]
        top.add(gdstk.rectangle(
            (src_x - wire_w / 2, vref_y),
            (src_x + wire_w / 2, src_y),
            **ld(L.MET1)))
        via_stack(top, (src_x, vref_y), L.MET1, L.MET2)

        # sw_lo source -> VSS (bridge over VDD rail using MET2)
        lo_src_x = sp["lo_n"][0] + sw_n_ports["S"].center[0]
        lo_src_y = sp["lo_n"][1] + sw_n_ports["S"].center[1]

        # MET1 from switch source down to just above VDD rail
        lo_m1_above_bot = vdd_y + vss_rail_w / 2 + vdd_clear
        top.add(gdstk.rectangle(
            (lo_src_x - wire_w / 2, lo_m1_above_bot),
            (lo_src_x + wire_w / 2, lo_src_y),
            **ld(L.MET1)))

        # MET1 from just below VDD rail down to VSS rail
        lo_m1_below_top = vdd_y - vss_rail_w / 2 - vdd_clear
        top.add(gdstk.rectangle(
            (lo_src_x - wire_w / 2, vss_y),
            (lo_src_x + wire_w / 2, lo_m1_below_top),
            **ld(L.MET1)))

        # MET2 bridge over VDD rail
        top.add(gdstk.rectangle(
            (lo_src_x - wire_w / 2, lo_m1_below_top - wire_w / 2),
            (lo_src_x + wire_w / 2, lo_m1_above_bot + wire_w / 2),
            **ld(L.MET2)))

        # Vias at bottom and top of MET2 bridge
        via_stack(top, (lo_src_x, lo_m1_below_top), L.MET1, L.MET2)
        via_stack(top, (lo_src_x, lo_m1_above_bot), L.MET1, L.MET2)

    # ------------------------------------------------------------------
    # 8. VDD and VSS power rails
    # ------------------------------------------------------------------
    cell_left = -1.0
    cell_right = array_w + 1.0
    cell_bottom = inv_row_y - inv_row_h
    cell_top = tp_top + 1.0

    # VSS rail at bottom (MET1, wide)
    vss_rail_w = 0.80
    vss_y = cell_bottom
    top.add(gdstk.rectangle(
        (cell_left, vss_y - vss_rail_w / 2),
        (cell_right, vss_y + vss_rail_w / 2),
        **ld(L.MET1)))

    # VDD rail between inverters and switches (MET1, wide)
    vdd_y = inv_row_y + inv_p_offset + 1.2
    top.add(gdstk.rectangle(
        (cell_left, vdd_y - vss_rail_w / 2),
        (cell_right, vdd_y + vss_rail_w / 2),
        **ld(L.MET1)))

    # Connect inverter NFET sources/bulks to VSS, PFET sources/bulks to VDD
    for bit in range(N_BITS):
        inv_pos = inverter_positions[bit]
        nx, ny = inv_pos["n"]
        px, py = inv_pos["p"]

        # NFET source to VSS
        ns_x = nx + inv_n_ports["S"].center[0]
        top.add(gdstk.rectangle(
            (ns_x - wire_w / 2, vss_y),
            (ns_x + wire_w / 2, ny + inv_n_ports["S"].center[1]),
            **ld(L.MET1)))

        # PFET source to VDD
        ps_x = px + inv_p_ports["S"].center[0]
        top.add(gdstk.rectangle(
            (ps_x - wire_w / 2, py + inv_p_ports["S"].center[1]),
            (ps_x + wire_w / 2, vdd_y),
            **ld(L.MET1)))

    # Connect switch NFET S-side to VSS, PFET S-side to VDD
    # (shared primitive has no B port; bulk ties through source region)
    for bit in range(N_BITS):
        sp = switch_positions[bit]
        for key in ("hi_n", "lo_n"):
            sx, sy = sp[key]
            bx = sx + sw_n_ports["S"].center[0]
            by = sy + sw_n_ports["S"].center[1]
            top.add(gdstk.rectangle(
                (bx - wire_w / 2, vss_y),
                (bx + wire_w / 2, by),
                **ld(L.MET1)))
        for key in ("hi_p", "lo_p"):
            sx, sy = sp[key]
            bx = sx + sw_p_ports["S"].center[0]
            by = sy + sw_p_ports["S"].center[1]
            top.add(gdstk.rectangle(
                (bx - wire_w / 2, by),
                (bx + wire_w / 2, vdd_y),
                **ld(L.MET1)))

    # ------------------------------------------------------------------
    # 9. Shield planes
    # ------------------------------------------------------------------
    shield_margin = 1.0

    # MET2 ground shield below cap array
    m2_shield_bot = tp_bot - shield_margin
    m2_shield_top = tp_bot + 0.5  # just below the array
    m2_shield_y = array_y0 - CAP_PITCH / 2 - 0.3
    top.add(gdstk.rectangle(
        (tp_left - shield_margin, m2_shield_y - 0.5),
        (tp_right + shield_margin, m2_shield_y + 0.5),
        **ld(L.MET2)))

    # Full MET2 ground plane under cap array (slotted for DRC: array of strips)
    m2_plane_bot = array_y0 - BOT_SIDE / 2 - 1.0
    m2_plane_top = array_y0 + (GRID - 1) * CAP_PITCH + BOT_SIDE / 2 + 1.0
    m2_strip_w = 2.0
    m2_strip_sp = DRC.MET2_SP + 0.50
    n_strips = max(1, int((tp_right - tp_left) / (m2_strip_w + m2_strip_sp)))
    strip_x0 = tp_left
    for i in range(n_strips):
        sx = strip_x0 + i * (m2_strip_w + m2_strip_sp)
        top.add(gdstk.rectangle(
            (sx, m2_plane_bot), (sx + m2_strip_w, m2_plane_top),
            **ld(L.MET2)))

    # MET5 ground shield above cap array
    # MET5 min width = 1.60 um, min space = 1.60 um
    m5_strip_w = DRC.MET5_W
    m5_strip_sp = DRC.MET5_SP
    n_m5 = max(1, int((tp_right - tp_left) / (m5_strip_w + m5_strip_sp)))
    for i in range(n_m5):
        sx = tp_left + i * (m5_strip_w + m5_strip_sp)
        top.add(gdstk.rectangle(
            (sx, tp_bot - 0.5), (sx + m5_strip_w, tp_top + 0.5),
            **ld(L.MET5)))

    # ------------------------------------------------------------------
    # 10. Export ports
    # ------------------------------------------------------------------
    # OUT port: center of MET4 top-plate bus (east edge for escape)
    out_x = tp_right
    out_y = (tp_bot + tp_top) / 2
    ports = {}
    ports["OUT"] = Port("OUT", (out_x, out_y), 1.0, 0.0, L.MET4)

    # VREF port: left edge of VREF MET2 bus
    ports["VREF"] = Port("VREF", (vref_left, vref_y), vref_w, 180.0, L.MET2)

    # Bit ports: at inverter gate inputs (MET1), facing south
    for bit in range(N_BITS):
        inv_pos = inverter_positions[bit]
        gx = inv_pos["n"][0] + inv_n_ports["G"].center[0]
        gy = inv_pos["n"][1] + inv_n_ports["G"].center[1]
        ports[f"B{bit}"] = Port(
            f"B{bit}", (gx, gy),
            inv_n_ports["G"].width, 270.0, L.MET1)

    # VDD port: left edge of VDD rail
    ports["VDD"] = Port("VDD", (cell_left, vdd_y), vss_rail_w, 180.0, L.MET1)

    # VSS port: left edge of VSS rail
    ports["VSS"] = Port("VSS", (cell_left, vss_y), vss_rail_w, 180.0, L.MET1)

    # Add pin labels for all ports
    for p in ports.values():
        add_port_label(top, p)

    return top, ports


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    lib = gdstk.Library("charge_dac")
    cell, ports = charge_dac_layout(lib)

    out_path = os.path.join(os.path.dirname(__file__), "charge_dac.gds")
    lib.write_gds(out_path)

    print(f"Exported {out_path}")
    print(f"  Cell: {cell.name}")
    print(f"  Ports ({len(ports)}):")
    for name, port in sorted(ports.items()):
        print(f"    {name:6s}  center=({port.center[0]:.2f}, {port.center[1]:.2f})  "
              f"layer={port.layer}  orient={port.orientation:.0f}")

    # Summary
    bb = cell.bounding_box()
    if bb is not None:
        w = bb[1][0] - bb[0][0]
        h = bb[1][1] - bb[0][1]
        print(f"  Bounding box: {w:.1f} x {h:.1f} um")
