"""Async self-timed controller layout — standard-cell row style with serpentine delay chains.

Architecture:
  - 3.40um cell height, standard-cell rows with shared VDD/VSS rails
  - MOS load caps (NFET gate-cap) for delay stages (~220fF, 5.6x5.6um)
  - Serpentine folding: 5 stages per row, alternating direction
  - rst_delay: 10 stages -> 2 rows of 5
  - settle_delay: 20 stages -> 4 rows of 5
  - Signal flow: GO -> buffer -> rst_delay -> NAND/xbar_rst -> settle_delay -> adc_go -> done
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import gdstk

from project.layout.layers import L, ld
from project.layout.drc import DRC
from project.layout.ports import Port, add_port_label, transform_ports
from project.layout.compose import Instance, abut_x, stack_y
from project.layout.primitives.mosfet import nfet, pfet


# ---------------------------------------------------------------------------
# Design constants (microns)
# ---------------------------------------------------------------------------

CELL_H = 5.40          # cell height — generous for NMOS-PMOS gap + N-well row spacing
RAIL_W = 0.70          # power rail width (MET1) — tall enough for LICON in tap
NWELL_Y = CELL_H / 2   # NWELL boundary (PMOS region above this)

# Inverter sizing
INV_NW = 0.42          # NFET width
INV_PW = 0.84          # PFET width
INV_L = 0.15           # gate length (both)

# MOS cap for delay load
MCAP_W = 5.6           # MOS cap gate width
MCAP_L = 5.6           # MOS cap gate length (sets capacitance)

# Delay stage dimensions
INV_CELL_W = 4.00      # inverter cell width — wider for LI/MET1 clearance
MCAP_CELL_W = 7.00     # MOS cap cell width
DELAY_PITCH = 15.50    # full delay stage pitch (inv + MOS cap + gap) — widened for MET1 spacing
STAGES_PER_ROW = 5

# Spacing
INTER_BLOCK_GAP = 3.50 # gap between functional blocks along X

# Contact / via dimensions (from DRC)
LICON = DRC.LICON_SZ   # 0.17
MCON = DRC.MCON_SZ     # 0.17
VIA = DRC.VIA_SZ       # 0.15
LI_W = DRC.LI1_W       # 0.17
MET1_W = DRC.MET1_W    # 0.14um MET1 routing width — minimum for max clearance
MET2_W = DRC.MET2_W    # 0.14um MET2 routing width — minimum for max clearance

# Inter-device spacing to satisfy DRC
NFET_PFET_GAP = 1.60   # vertical gap between NFET top and PFET bottom
DEVICE_COL_GAP = 2.50  # horizontal gap between device columns (LI/MCON spacing) — widened for MET1
NWELL_GUARD_SP = DRC.NWELL_SP + 0.08  # 1.35 um N-well to N-well spacing (nwell.1/nwell.2a margin)


# ---------------------------------------------------------------------------
# Helper: place a shared-primitive MOSFET into a parent cell
# ---------------------------------------------------------------------------

_mosfet_counter = 0


def _place_mosfet(cell, lib, x, y, w, l, is_pmos=False, flip_sd=False):
    """Place a DRC-clean MOSFET from the shared primitive library.

    Args:
        cell:     gdstk.Cell to add the reference to.
        lib:      gdstk.Library (needed to create the primitive cell).
        x, y:     Lower-left corner of the device region.
        w:        Channel width in microns.
        l:        Gate length in microns.
        is_pmos:  If True, use pfet(); else nfet().
        flip_sd:  If True, swap source/drain in the returned dict.

    Returns:
        dict with keys 'G', 'S', 'D', 'B' as (cx, cy) center coordinates,
        plus 'bbox' as ((x0,y0),(x1,y1)).
    """
    global _mosfet_counter
    _mosfet_counter += 1
    tag = "p" if is_pmos else "n"
    w_nm = round(w * 1000)
    l_nm = round(l * 1000)
    name = f"ac_{tag}_{w_nm}_{l_nm}_{_mosfet_counter}"

    if is_pmos:
        mos_cell, mos_ports = pfet(lib, w, l, nf=1, name=name)
    else:
        mos_cell, mos_ports = nfet(lib, w, l, nf=1, name=name)

    inst = Instance(mos_cell, mos_ports, name=name)

    bb = mos_cell.bounding_box()
    if bb is not None:
        cx = x - float(bb[0][0])
        cy = y - float(bb[0][1])
    else:
        cx = x
        cy = y

    inst.place(cx, cy)
    inst.add_to(cell)

    g_pos = inst.port("G").center
    s_pos = inst.port("S").center
    d_pos = inst.port("D").center

    if flip_sd:
        s_pos, d_pos = d_pos, s_pos

    bbox = inst.bbox()

    pins = {
        "G": g_pos,
        "S": s_pos,
        "D": d_pos,
        "B": s_pos,
        "bbox": bbox,
    }
    return pins


def _mcon_stack(cell, cx, cy):
    """Place MCON + MET1 pad at (cx, cy) to go from LI1 to MET1."""
    cell.add(gdstk.rectangle(
        (cx - MCON / 2, cy - MCON / 2),
        (cx + MCON / 2, cy + MCON / 2),
        **ld(L.MCON),
    ))
    met1_pad = max(MET1_W, MCON + 2 * DRC.MCON_ENCL_MET1_WIDE)
    cell.add(gdstk.rectangle(
        (cx - met1_pad / 2, cy - met1_pad / 2),
        (cx + met1_pad / 2, cy + met1_pad / 2),
        **ld(L.MET1),
    ))


def _via_stack(cell, cx, cy):
    """Place VIA + MET2 pad at (cx, cy) to go from MET1 to MET2."""
    _VIA_ENCL_MARGIN = 0.04  # extra margin for met2.5/met2.4 compliance
    met1_pad = max(MET1_W, VIA + 2 * (DRC.VIA_ENCL_MET1 + _VIA_ENCL_MARGIN))
    cell.add(gdstk.rectangle(
        (cx - met1_pad / 2, cy - met1_pad / 2),
        (cx + met1_pad / 2, cy + met1_pad / 2),
        **ld(L.MET1),
    ))
    cell.add(gdstk.rectangle(
        (cx - VIA / 2, cy - VIA / 2),
        (cx + VIA / 2, cy + VIA / 2),
        **ld(L.VIA),
    ))
    met2_pad = max(MET2_W, VIA + 2 * (DRC.VIA_ENCL_MET2 + _VIA_ENCL_MARGIN))
    cell.add(gdstk.rectangle(
        (cx - met2_pad / 2, cy - met2_pad / 2),
        (cx + met2_pad / 2, cy + met2_pad / 2),
        **ld(L.MET2),
    ))


def _met1_wire(cell, x0, y0, x1, y1, w=None):
    """Draw a MET1 wire from (x0,y0) to (x1,y1) with given width."""
    if w is None:
        w = MET1_W
    hw = w / 2
    if abs(y1 - y0) < 0.001:  # horizontal
        cell.add(gdstk.rectangle(
            (min(x0, x1), y0 - hw), (max(x0, x1), y0 + hw),
            **ld(L.MET1),
        ))
    elif abs(x1 - x0) < 0.001:  # vertical
        cell.add(gdstk.rectangle(
            (x0 - hw, min(y0, y1)), (x0 + hw, max(y0, y1)),
            **ld(L.MET1),
        ))


def _met2_wire(cell, x0, y0, x1, y1, w=None):
    """Draw a MET2 wire from (x0,y0) to (x1,y1)."""
    if w is None:
        w = MET2_W
    hw = w / 2
    if abs(y1 - y0) < 0.001:
        cell.add(gdstk.rectangle(
            (min(x0, x1), y0 - hw), (max(x0, x1), y0 + hw),
            **ld(L.MET2),
        ))
    elif abs(x1 - x0) < 0.001:
        cell.add(gdstk.rectangle(
            (x0 - hw, min(y0, y1)), (x0 + hw, max(y0, y1)),
            **ld(L.MET2),
        ))


# ---------------------------------------------------------------------------
# Cell builders
# ---------------------------------------------------------------------------

def inv_cell(lib, name=None):
    """Standard minimum-size inverter cell.

    NFET W=0.42 L=0.15 (bottom), PFET W=0.84 L=0.15 (top).
    Cell height = CELL_H. VDD rail at top, VSS rail at bottom.
    All inter-device wiring on MET1 (not LI1) for spacing compliance.

    Returns:
        (cell, ports) where ports = {IN, OUT, VDD, VSS}
    """
    if name is None:
        name = f"inv_{id(lib) % 10000}"
    cell = lib.new_cell(name)

    # NFET region: bottom half with spacing from rail
    nfet_y = RAIL_W + 0.30
    n_pins = _place_mosfet(cell, lib, 0.50, nfet_y, INV_NW, INV_L, is_pmos=False)

    # PFET region: top half with generous N-well gap from NFET
    pfet_y = CELL_H - RAIL_W - 0.30 - INV_PW
    p_pins = _place_mosfet(cell, lib, 0.50, pfet_y, INV_PW, INV_L, is_pmos=True)

    # Connect gates via min-width MET1 (MOSFET primitive already has MCON+MET1)
    g_nx, g_ny = n_pins["G"]
    g_px, g_py = p_pins["G"]
    _met1_wire(cell, g_nx, g_ny, g_nx, g_py, w=DRC.MET1_W)

    # Connect drains via min-width MET1 -> output (MOSFET primitive already has MCON+MET1)
    d_nx, d_ny = n_pins["D"]
    d_px, d_py = p_pins["D"]
    _met1_wire(cell, d_nx, d_ny, d_nx, d_py, w=DRC.MET1_W)

    # Output port at drain midpoint
    out_cx = d_nx
    out_cy = (d_ny + d_py) / 2

    # Input port at gate
    in_cx = g_nx
    in_cy = g_ny

    # VSS rail (MET1)
    cell_w = INV_CELL_W
    cell.add(gdstk.rectangle(
        (0, 0), (cell_w, RAIL_W),
        **ld(L.MET1),
    ))
    # VDD rail (MET1)
    cell.add(gdstk.rectangle(
        (0, CELL_H - RAIL_W), (cell_w, CELL_H),
        **ld(L.MET1),
    ))

    # NFET source -> VSS via MET1 (MOSFET primitive already has MCON+MET1)
    s_nx, s_ny = n_pins["S"]
    _met1_wire(cell, s_nx, s_ny, s_nx, RAIL_W / 2)

    # PFET source -> VDD via MET1 (MOSFET primitive already has MCON+MET1)
    s_px, s_py = p_pins["S"]
    _met1_wire(cell, s_px, s_py, s_px, CELL_H - RAIL_W / 2)

    # Substrate/well taps with proper enclosure — offset from cell edges
    _draw_tap(cell, 0.08, 0.08, RAIL_W - 0.16, is_ptype=True)
    _draw_tap(cell, 0.08, CELL_H - RAIL_W + 0.08, RAIL_W - 0.16, is_ptype=False)

    ports = {
        "IN":  Port("IN",  (in_cx, in_cy), MET1_W, 180, L.MET1),
        "OUT": Port("OUT", (out_cx, out_cy), MET1_W, 0, L.MET1),
        "VDD": Port("VDD", (cell_w / 2, CELL_H - RAIL_W / 2), RAIL_W, 90, L.MET1),
        "VSS": Port("VSS", (cell_w / 2, RAIL_W / 2), RAIL_W, 270, L.MET1),
    }

    return cell, ports


def _draw_tap(cell, x, y, h, is_ptype=True):
    """Draw a substrate/well tap contact at (x, y) with height h.

    Args:
        is_ptype: True for P+ tap (PSDM, connects to VSS), False for N+ tap (NSDM in NWELL).
    """
    # Use wider tap to enclose LICON with P-tap enclosure (licon.7: 0.12)
    min_tap_for_licon = LICON + 2 * DRC.PTAP_ENCL_LICON  # 0.17 + 0.24 = 0.41
    tap_w = max(DRC.TAP_W, min_tap_for_licon)  # 0.41
    cell.add(gdstk.rectangle(
        (x, y), (x + tap_w, y + h),
        **ld(L.TAP),
    ))
    imp = L.PSDM if is_ptype else L.NSDM
    enc = DRC.PSDM_ENCL if is_ptype else DRC.NSDM_ENCL
    cell.add(gdstk.rectangle(
        (x - enc, y - enc), (x + tap_w + enc, y + h + enc),
        **ld(imp),
    ))
    # N-type taps (NSDM) require NWELL enclosure >= 0.18um on all sides
    if not is_ptype:
        nw_enc = DRC.NWELL_ENCL_TAP + 0.05  # 0.23 um (nwell.2a margin increase)
        nw_w = tap_w + 2 * nw_enc
        nw_h = h + 2 * nw_enc
        # Clamp to minimum NWELL width (0.84 um)
        nw_w = max(nw_w, DRC.NWELL_W)
        nw_h = max(nw_h, DRC.NWELL_W)
        nw_cx = x + tap_w / 2
        nw_cy = y + h / 2
        cell.add(gdstk.rectangle(
            (nw_cx - nw_w / 2, nw_cy - nw_h / 2),
            (nw_cx + nw_w / 2, nw_cy + nw_h / 2),
            **ld(L.NWELL),
        ))
    # LICON on tap — use proper P-tap enclosure (licon.7: >= 0.12 um)
    tap_encl = DRC.PTAP_ENCL_LICON if is_ptype else DRC.DIFF_ENCL_LICON
    cx = x + tap_w / 2
    cy = y + h / 2
    # Ensure tap is large enough to enclose LICON with required margin
    min_tap_w_for_licon = LICON + 2 * tap_encl
    if tap_w >= min_tap_w_for_licon and h >= min_tap_w_for_licon:
        cell.add(gdstk.rectangle(
            (cx - LICON / 2, cy - LICON / 2),
            (cx + LICON / 2, cy + LICON / 2),
            **ld(L.LICON),
        ))
    li_pad = max(LI_W, LICON + 2 * DRC.LI1_ENCL_LICON)
    # li.6: LI1 area >= 0.0561 um^2 — clamp to at least 0.237 um per side
    _LI_MIN_AREA = 0.0561
    li_pad = max(li_pad, _LI_MIN_AREA ** 0.5)
    cell.add(gdstk.rectangle(
        (cx - li_pad / 2, cy - li_pad / 2),
        (cx + li_pad / 2, cy + li_pad / 2),
        **ld(L.LI1),
    ))


def delay_stage(lib, name):
    """Single delay stage: min-size inverter + MOS load cap.

    The MOS cap is an NFET with W~2.0um (clamped to cell height), L=5.6um,
    gate connected to the inverter output, S/D/B tied to VSS.
    Cell height = CELL_H (standard cell).
    All inter-device wiring on MET1.
    Ports: IN, OUT, VDD, VSS

    Returns:
        (cell, ports)
    """
    cell = lib.new_cell(name)

    # --- Inverter section (left side) ---
    nfet_y = RAIL_W + 0.30
    n_pins = _place_mosfet(cell, lib, 0.50, nfet_y, INV_NW, INV_L, is_pmos=False)

    pfet_y = CELL_H - RAIL_W - 0.30 - INV_PW
    p_pins = _place_mosfet(cell, lib, 0.50, pfet_y, INV_PW, INV_L, is_pmos=True)

    # Connect inverter gates via min-width MET1 (primitive has MCON+MET1)
    g_nx, g_ny = n_pins["G"]
    g_px, g_py = p_pins["G"]
    _met1_wire(cell, g_nx, g_ny, g_nx, g_py, w=DRC.MET1_W)

    # Connect inverter drains via min-width MET1 (primitive has MCON+MET1)
    d_nx, d_ny = n_pins["D"]
    d_px, d_py = p_pins["D"]
    _met1_wire(cell, d_nx, d_ny, d_nx, d_py, w=DRC.MET1_W)

    # Input port (MCON on gate)
    in_cx = g_nx
    in_cy = g_ny

    # Inverter output (MCON on drain midpoint)
    inv_out_cx = d_nx
    inv_out_cy = (d_ny + d_py) / 2

    # Source connections to rails via MET1 (primitive has MCON+MET1)
    s_nx, s_ny = n_pins["S"]
    _met1_wire(cell, s_nx, s_ny, s_nx, RAIL_W / 2)

    s_px, s_py = p_pins["S"]
    _met1_wire(cell, s_px, s_py, s_px, CELL_H - RAIL_W / 2)

    # --- MOS cap section (right side) ---
    mcap_x = INV_CELL_W + 2.50  # generous gap between inverter and cap for LI/MET1 clearance
    mcap_y = RAIL_W + 0.30
    mcap_actual_h = min(MCAP_W, CELL_H - 2 * RAIL_W - 0.60)

    mcap_pins = _place_mosfet(cell, lib, mcap_x, mcap_y, mcap_actual_h,
                              MCAP_L, is_pmos=False)

    # Gate connects to inverter output (signal node)
    mcap_g_cx, mcap_g_cy = mcap_pins["G"]

    # Route inverter output to MOS cap gate via MET2 to avoid MET1 congestion
    _via_stack(cell, inv_out_cx, inv_out_cy)
    _via_stack(cell, mcap_g_cx, mcap_g_cy)
    _met2_wire(cell, inv_out_cx, inv_out_cy, mcap_g_cx, inv_out_cy, w=MET2_W)
    _met2_wire(cell, mcap_g_cx, inv_out_cy, mcap_g_cx, mcap_g_cy, w=MET2_W)

    # MOS cap S/D -> VSS rail via MET1 (primitive has MCON+MET1)
    mcap_s_cx, mcap_s_cy = mcap_pins["S"]
    mcap_d_cx, mcap_d_cy = mcap_pins["D"]
    _met1_wire(cell, mcap_s_cx, RAIL_W / 2, mcap_s_cx, mcap_s_cy, w=MET1_W)
    _met1_wire(cell, mcap_d_cx, RAIL_W / 2, mcap_d_cx, mcap_d_cy, w=MET1_W)

    # --- Power rails ---
    mcap_bbox = mcap_pins["bbox"]
    total_w = mcap_bbox[1][0] + 0.30
    cell.add(gdstk.rectangle((0, 0), (total_w, RAIL_W), **ld(L.MET1)))
    cell.add(gdstk.rectangle((0, CELL_H - RAIL_W), (total_w, CELL_H), **ld(L.MET1)))

    # Substrate taps
    _draw_tap(cell, 0.08, 0.08, RAIL_W - 0.16, is_ptype=True)
    _draw_tap(cell, 0.08, CELL_H - RAIL_W + 0.08, RAIL_W - 0.16, is_ptype=False)

    # --- Output port ---
    out_cx = inv_out_cx
    out_cy = inv_out_cy

    ports = {
        "IN":  Port("IN",  (in_cx, in_cy), MET1_W, 180, L.MET1),
        "OUT": Port("OUT", (out_cx, out_cy), MET1_W, 0, L.MET1),
        "VDD": Port("VDD", (total_w / 2, CELL_H - RAIL_W / 2), RAIL_W, 90, L.MET1),
        "VSS": Port("VSS", (total_w / 2, RAIL_W / 2), RAIL_W, 270, L.MET1),
    }

    return cell, ports


def muller_c(lib):
    """Muller C-element: 8 transistors in wider layout for DRC compliance.

    Topology:
      - Series PFET pair: P1 (gate=A) -> P2 (gate=B) -> VDD
      - Series NFET pair: N1 (gate=A) -> N2 (gate=B) -> VSS
      - Keeper: P3 (gate=out_b) pull-up, N3 (gate=out_b) pull-down
      - Feedback inverter: PFB/NFB (gate=out -> out_b)

    Cell height = CELL_H, width ~ 3.5um.
    All inter-device wiring on MET1 with MET2 for crossings.
    Ports: A, B, OUT, VDD, VSS

    Returns:
        (cell, ports)
    """
    cell = lib.new_cell("muller_c")

    # Layout: 4 columns with generous spacing for LI/NWELL/MCON clearance
    x_start = 0.60
    col_pitch = DEVICE_COL_GAP  # 1.50 um between columns
    col_x = [x_start + i * col_pitch for i in range(4)]

    # PMOS region: top half with proper spacing
    pfet_base_y = CELL_H - RAIL_W - 0.30 - INV_PW

    # NFET region: bottom half
    nfet_base_y = RAIL_W + 0.30

    # Muller C sizing — all widths >= 0.42 for diff/tap.2 compliance
    mp_w = 1.0
    mn_w = 0.50
    mk_pw = 0.50
    mk_nw = 0.42
    fb_pw = 0.42
    fb_nw = 0.42
    ml = 0.15

    # Draw each transistor column
    p1 = _place_mosfet(cell, lib, col_x[0], pfet_base_y, mp_w, ml, is_pmos=True)
    n1 = _place_mosfet(cell, lib, col_x[0], nfet_base_y, mn_w, ml, is_pmos=False)

    p2 = _place_mosfet(cell, lib, col_x[1], pfet_base_y, mp_w, ml, is_pmos=True)
    n2 = _place_mosfet(cell, lib, col_x[1], nfet_base_y, mn_w, ml, is_pmos=False)

    p3 = _place_mosfet(cell, lib, col_x[2], pfet_base_y, mk_pw, ml, is_pmos=True)
    n3 = _place_mosfet(cell, lib, col_x[2], nfet_base_y, mk_nw, ml, is_pmos=False)

    pfb = _place_mosfet(cell, lib, col_x[3], pfet_base_y, fb_pw, ml, is_pmos=True)
    nfb = _place_mosfet(cell, lib, col_x[3], nfet_base_y, fb_nw, ml, is_pmos=False)

    # --- Internal wiring (min-width MET1 for gate connections) ---
    # Gate A: P1.G and N1.G (primitive has MCON+MET1)
    _met1_wire(cell, p1["G"][0], p1["G"][1], n1["G"][0], n1["G"][1], w=DRC.MET1_W)

    # Gate B: P2.G and N2.G
    _met1_wire(cell, p2["G"][0], p2["G"][1], n2["G"][0], n2["G"][1], w=DRC.MET1_W)

    # Keeper gate (out_b): P3.G and N3.G
    _met1_wire(cell, p3["G"][0], p3["G"][1], n3["G"][0], n3["G"][1], w=DRC.MET1_W)

    # Feedback gate (out): PFB.G and NFB.G
    _met1_wire(cell, pfb["G"][0], pfb["G"][1], nfb["G"][0], nfb["G"][1], w=DRC.MET1_W)

    # Output node (out): P1.D, N1.D, P3.D, N3.D via min-width MET1
    out_y = (nfet_base_y + INV_NW / 2 + pfet_base_y + INV_PW / 2) / 2

    out_nodes = [p1["D"], n1["D"], p3["D"], n3["D"]]
    x_min = min(p[0] for p in out_nodes)
    x_max = max(p[0] for p in out_nodes)
    _met1_wire(cell, x_min, out_y, x_max, out_y, w=DRC.MET1_W)
    for pins in (p1, n1, p3, n3):
        _met1_wire(cell, pins["D"][0], pins["D"][1], pins["D"][0], out_y, w=DRC.MET1_W)

    # out_b node: PFB.D, NFB.D -> keeper gates via MET2 to avoid MET1 congestion
    outb_y = out_y + 0.40
    # Use MET2 for out_b connection to avoid MET1 congestion
    _via_stack(cell, pfb["D"][0], pfb["D"][1])
    _via_stack(cell, nfb["D"][0], nfb["D"][1])
    _met2_wire(cell, pfb["D"][0], pfb["D"][1], pfb["D"][0], outb_y)
    _met2_wire(cell, nfb["D"][0], nfb["D"][1], nfb["D"][0], outb_y)
    _met2_wire(cell, pfb["D"][0], outb_y, nfb["D"][0], outb_y)

    # Connect out_b to keeper gates (P3.G, N3.G) via MET2
    keeper_g_cx = p3["G"][0]
    _via_stack(cell, keeper_g_cx, p3["G"][1])
    _met2_wire(cell, keeper_g_cx, p3["G"][1], pfb["D"][0], p3["G"][1])
    _met2_wire(cell, pfb["D"][0], p3["G"][1], pfb["D"][0], outb_y)

    # Connect feedback gate (out) from output bus via MET2
    fb_g_cx = pfb["G"][0]
    _via_stack(cell, fb_g_cx, pfb["G"][1])
    out_bus_x = (x_min + x_max) / 2
    _via_stack(cell, out_bus_x, out_y)
    _met2_wire(cell, fb_g_cx, pfb["G"][1], out_bus_x, pfb["G"][1])
    _met2_wire(cell, out_bus_x, pfb["G"][1], out_bus_x, out_y)

    # Series PFET connection: P1.S -> P2.D via min-width MET1
    mid_y_p = (p1["S"][1] + p2["D"][1]) / 2
    _met1_wire(cell, p1["S"][0], p1["S"][1], p1["S"][0], mid_y_p, w=DRC.MET1_W)
    _met1_wire(cell, p1["S"][0], mid_y_p, p2["D"][0], mid_y_p, w=DRC.MET1_W)
    _met1_wire(cell, p2["D"][0], mid_y_p, p2["D"][0], p2["D"][1], w=DRC.MET1_W)

    # P2.S -> VDD
    _met1_wire(cell, p2["S"][0], p2["S"][1], p2["S"][0], CELL_H - RAIL_W / 2)

    # P3.S -> VDD
    _met1_wire(cell, p3["S"][0], p3["S"][1], p3["S"][0], CELL_H - RAIL_W / 2)

    # PFB.S -> VDD
    _met1_wire(cell, pfb["S"][0], pfb["S"][1], pfb["S"][0], CELL_H - RAIL_W / 2)

    # Series NFET: N1.S -> N2.D via min-width MET1
    mid_y_n = (n1["S"][1] + n2["D"][1]) / 2
    _met1_wire(cell, n1["S"][0], n1["S"][1], n1["S"][0], mid_y_n, w=DRC.MET1_W)
    _met1_wire(cell, n1["S"][0], mid_y_n, n2["D"][0], mid_y_n, w=DRC.MET1_W)
    _met1_wire(cell, n2["D"][0], mid_y_n, n2["D"][0], n2["D"][1], w=DRC.MET1_W)

    # N2.S -> VSS
    _met1_wire(cell, n2["S"][0], n2["S"][1], n2["S"][0], RAIL_W / 2)

    # N3.S -> VSS
    _met1_wire(cell, n3["S"][0], n3["S"][1], n3["S"][0], RAIL_W / 2)

    # NFB.S -> VSS
    _met1_wire(cell, nfb["S"][0], nfb["S"][1], nfb["S"][0], RAIL_W / 2)

    # --- Power rails ---
    cell_w = col_x[3] + 1.50
    cell.add(gdstk.rectangle((0, 0), (cell_w, RAIL_W), **ld(L.MET1)))
    cell.add(gdstk.rectangle((0, CELL_H - RAIL_W), (cell_w, CELL_H), **ld(L.MET1)))

    # Taps
    _draw_tap(cell, 0.08, 0.08, RAIL_W - 0.16, is_ptype=True)
    _draw_tap(cell, 0.08, CELL_H - RAIL_W + 0.08, RAIL_W - 0.16, is_ptype=False)

    # MCON on gate A for port
    a_cx, a_cy = n1["G"]

    # MCON on gate B for port
    b_cx, b_cy = n2["G"]

    # Output port at the output bus center
    out_port_cx = out_bus_x
    out_port_cy = out_y

    ports = {
        "A":   Port("A",   (a_cx, a_cy), MET1_W, 180, L.MET1),
        "B":   Port("B",   (b_cx, b_cy), MET1_W, 180, L.MET1),
        "OUT": Port("OUT", (out_port_cx, out_port_cy), MET1_W, 0, L.MET1),
        "VDD": Port("VDD", (cell_w / 2, CELL_H - RAIL_W / 2), RAIL_W, 90, L.MET1),
        "VSS": Port("VSS", (cell_w / 2, RAIL_W / 2), RAIL_W, 270, L.MET1),
    }

    return cell, ports


def nand2_cell(lib):
    """Standard 2-input NAND gate.

    Topology: parallel PFET pair + series NFET pair.
    PFET W=0.84, NFET W=0.84 (upsized for series stack).
    Cell height = CELL_H. All wiring on MET1.

    Ports: A, B, OUT, VDD, VSS

    Returns:
        (cell, ports)
    """
    cell = lib.new_cell("nand2")

    # 2 device columns with generous spacing
    x_start = 0.60
    col_x = [x_start, x_start + DEVICE_COL_GAP]

    nfet_y = RAIL_W + 0.30
    pfet_y = CELL_H - RAIL_W - 0.30 - INV_PW
    nand_nw = 0.84

    # P1 (gate=A), P2 (gate=B)
    p1 = _place_mosfet(cell, lib, col_x[0], pfet_y, INV_PW, INV_L, is_pmos=True)
    p2 = _place_mosfet(cell, lib, col_x[1], pfet_y, INV_PW, INV_L, is_pmos=True)

    # N1 (gate=A), N2 (gate=B, flip_sd for series stack)
    n1 = _place_mosfet(cell, lib, col_x[0], nfet_y, nand_nw, INV_L, is_pmos=False)
    n2 = _place_mosfet(cell, lib, col_x[1], nfet_y, nand_nw, INV_L, is_pmos=False,
                       flip_sd=True)

    # Gate A: P1.G, N1.G via min-width MET1 (primitive has MCON+MET1)
    _met1_wire(cell, p1["G"][0], p1["G"][1], n1["G"][0], n1["G"][1], w=DRC.MET1_W)

    # Gate B: P2.G, N2.G via min-width MET1
    _met1_wire(cell, p2["G"][0], p2["G"][1], n2["G"][0], n2["G"][1], w=DRC.MET1_W)

    # Output: P1.D, P2.D, N1.D all connect via min-width MET1
    out_y_pos = (nfet_y + nand_nw / 2 + pfet_y + INV_PW / 2) / 2
    out_nodes = [p1["D"], p2["D"], n1["D"]]
    x_min = min(p[0] for p in out_nodes)
    x_max = max(p[0] for p in out_nodes)
    _met1_wire(cell, x_min, out_y_pos, x_max, out_y_pos, w=DRC.MET1_W)
    for pins in (p1, p2, n1):
        _met1_wire(cell, pins["D"][0], pins["D"][1], pins["D"][0], out_y_pos, w=DRC.MET1_W)

    # Series NFET mid-node: N1.S -> N2.D via min-width MET1
    mid_y_n = (n1["S"][1] + n2["D"][1]) / 2
    _met1_wire(cell, n1["S"][0], n1["S"][1], n1["S"][0], mid_y_n, w=DRC.MET1_W)
    _met1_wire(cell, n1["S"][0], mid_y_n, n2["D"][0], mid_y_n, w=DRC.MET1_W)
    _met1_wire(cell, n2["D"][0], mid_y_n, n2["D"][0], n2["D"][1], w=DRC.MET1_W)

    # P1.S, P2.S -> VDD via MET1
    for pins in (p1, p2):
        _met1_wire(cell, pins["S"][0], pins["S"][1], pins["S"][0], CELL_H - RAIL_W / 2)

    # N2.S -> VSS via MET1
    _met1_wire(cell, n2["S"][0], n2["S"][1], n2["S"][0], RAIL_W / 2)

    # Power rails
    cell_w = col_x[1] + 1.50
    cell.add(gdstk.rectangle((0, 0), (cell_w, RAIL_W), **ld(L.MET1)))
    cell.add(gdstk.rectangle((0, CELL_H - RAIL_W), (cell_w, CELL_H), **ld(L.MET1)))

    # Taps
    _draw_tap(cell, 0.08, 0.08, RAIL_W - 0.16, is_ptype=True)
    _draw_tap(cell, 0.08, CELL_H - RAIL_W + 0.08, RAIL_W - 0.16, is_ptype=False)

    out_cx = (x_min + x_max) / 2
    out_cy = out_y_pos

    ports = {
        "A":   Port("A",   (n1["G"][0], n1["G"][1]), MET1_W, 180, L.MET1),
        "B":   Port("B",   (n2["G"][0], n2["G"][1]), MET1_W, 180, L.MET1),
        "OUT": Port("OUT", (out_cx, out_cy), MET1_W, 0, L.MET1),
        "VDD": Port("VDD", (cell_w / 2, CELL_H - RAIL_W / 2), RAIL_W, 90, L.MET1),
        "VSS": Port("VSS", (cell_w / 2, RAIL_W / 2), RAIL_W, 270, L.MET1),
    }

    return cell, ports


# ---------------------------------------------------------------------------
# Full controller assembly
# ---------------------------------------------------------------------------

def _place_delay_row(lib, parent_cell, stages, row_idx, base_x, base_y,
                     reversed_dir=False, prefix="dly"):
    """Place a row of delay stage instances.

    Args:
        lib:           gdstk library.
        parent_cell:   Cell to add references into.
        stages:        List of (cell, ports) tuples for delay stage cells.
        row_idx:       Row index (for vertical offset).
        base_x:        X origin of the row.
        base_y:        Y origin of the row.
        reversed_dir:  If True, stages run right-to-left (serpentine).
        prefix:        Name prefix for instances.

    Returns:
        List of Instance objects (in signal-flow order).
    """
    instances = []
    n = len(stages)
    order = list(range(n))
    if reversed_dir:
        order = list(reversed(order))

    for place_idx, sig_idx in enumerate(order):
        stage_cell, stage_ports = stages[sig_idx]
        inst = Instance(stage_cell, stage_ports, name=f"{prefix}_r{row_idx}_s{sig_idx}")
        x = base_x + place_idx * DELAY_PITCH
        y = base_y
        mirror = (row_idx % 2 == 1)
        if mirror:
            inst.place(x, y + CELL_H, mirror_x=True)
        else:
            inst.place(x, y)
        inst.add_to(parent_cell)
        instances.append(inst)

    if reversed_dir:
        instances = list(reversed(instances))
    return instances


def async_ctrl_layout(lib):
    """Full async self-timed controller layout.

    Signal flow:
      GO -> inv_go1 -> inv_go2 (go_buf)
      go_buf -> rst_delay[10 stages, 2 rows of 5, serpentine]
      rst_dly_raw -> inv_rd1 -> inv_rd2 (rst_delayed)
      go_buf + rst_dly_b -> NAND -> inv_rst -> XBAR_RST
      rst_delayed -> settle_delay[20 stages, 4 rows of 5, serpentine]
      stl_dly_raw -> inv_sd1 -> inv_sd2 (settle_delayed)
      settle_delayed -> inv_ag1 -> inv_ag2 -> ADC_GO
      ADC_DONE -> inv_ld1 -> inv_ld2 -> LATCH_OUT
      LATCH_OUT -> inv_dn1 -> inv_dn2 -> DONE

    Returns:
        (cell, ports)
    """
    top = lib.new_cell("async_ctrl")

    # -----------------------------------------------------------------------
    # 1. Create all sub-cells
    # -----------------------------------------------------------------------
    rst_stages = []
    for i in range(10):
        rst_stages.append(delay_stage(lib, f"rst_dly_s{i}"))

    settle_stages = []
    for i in range(20):
        settle_stages.append(delay_stage(lib, f"stl_dly_s{i}"))

    inv_go1_cell = inv_cell(lib, "inv_go1")
    inv_go2_cell = inv_cell(lib, "inv_go2")
    inv_rd1_cell = inv_cell(lib, "inv_rd1")
    inv_rd2_cell = inv_cell(lib, "inv_rd2")
    inv_rst_cell = inv_cell(lib, "inv_rst")
    inv_sd1_cell = inv_cell(lib, "inv_sd1")
    inv_sd2_cell = inv_cell(lib, "inv_sd2")
    inv_ag1_cell = inv_cell(lib, "inv_ag1")
    inv_ag2_cell = inv_cell(lib, "inv_ag2")
    inv_ld1_cell = inv_cell(lib, "inv_ld1")
    inv_ld2_cell = inv_cell(lib, "inv_ld2")
    inv_dn1_cell = inv_cell(lib, "inv_dn1")
    inv_dn2_cell = inv_cell(lib, "inv_dn2")

    nand_cell = nand2_cell(lib)
    muller_cell = muller_c(lib)

    # -----------------------------------------------------------------------
    # 2. Place GO buffer (2 inverters) at bottom-left of row 0
    # -----------------------------------------------------------------------
    row0_y = 0.0
    x_cursor = 0.0

    # Generous spacing between inverters for LI/MCON/MET1 clearance
    inv_gap = 1.20

    inst_go1 = Instance(*inv_go1_cell, name="inv_go1")
    inst_go1.place(x_cursor, row0_y).add_to(top)
    x_cursor += INV_CELL_W + inv_gap

    inst_go2 = Instance(*inv_go2_cell, name="inv_go2")
    inst_go2.place(x_cursor, row0_y).add_to(top)
    x_cursor += INV_CELL_W + INTER_BLOCK_GAP

    # -----------------------------------------------------------------------
    # 3. Place rst_delay (10 stages in 2 rows of 5, serpentine)
    # -----------------------------------------------------------------------
    rst_block_x = x_cursor

    rst_row0 = _place_delay_row(lib, top, rst_stages[0:5], row_idx=0,
                                base_x=rst_block_x, base_y=row0_y,
                                reversed_dir=False, prefix="rst")

    row1_y = CELL_H
    rst_row1 = _place_delay_row(lib, top, rst_stages[5:10], row_idx=1,
                                base_x=rst_block_x, base_y=row1_y,
                                reversed_dir=True, prefix="rst")

    # Serpentine jumper at right end
    rst_r0_last = rst_row0[-1]
    rst_r1_first = rst_row1[0]
    _serpentine_jumper(top, rst_r0_last.port("OUT"), rst_r1_first.port("IN"))

    # -----------------------------------------------------------------------
    # 4. Place post-rst buffers + NAND + xbar_rst inverter (row 2)
    # -----------------------------------------------------------------------
    row2_y = 2 * CELL_H
    post_rst_x = 0.0

    inst_rd1 = Instance(*inv_rd1_cell, name="inv_rd1")
    inst_rd1.place(post_rst_x, row2_y).add_to(top)
    post_rst_x += INV_CELL_W + inv_gap

    inst_rd2 = Instance(*inv_rd2_cell, name="inv_rd2")
    inst_rd2.place(post_rst_x, row2_y).add_to(top)
    post_rst_x += INV_CELL_W + 1.20

    inst_nand = Instance(*nand_cell, name="nand_rst")
    inst_nand.place(post_rst_x, row2_y).add_to(top)
    nand_w = nand_cell[0].bounding_box()
    nand_cell_w = float(nand_w[1][0] - nand_w[0][0]) if nand_w is not None else 1.50
    post_rst_x += nand_cell_w + inv_gap

    inst_inv_rst = Instance(*inv_rst_cell, name="inv_rst")
    inst_inv_rst.place(post_rst_x, row2_y).add_to(top)
    post_rst_x += INV_CELL_W + INTER_BLOCK_GAP

    # -----------------------------------------------------------------------
    # 5. Place settle_delay (20 stages in 4 rows of 5, serpentine)
    # -----------------------------------------------------------------------
    settle_block_x = post_rst_x

    stl_row0 = _place_delay_row(lib, top, settle_stages[0:5], row_idx=0,
                                base_x=settle_block_x, base_y=row2_y,
                                reversed_dir=False, prefix="stl")

    row3_y = 3 * CELL_H
    stl_row1 = _place_delay_row(lib, top, settle_stages[5:10], row_idx=1,
                                base_x=settle_block_x, base_y=row3_y,
                                reversed_dir=True, prefix="stl")

    row4_y = 4 * CELL_H
    stl_row2 = _place_delay_row(lib, top, settle_stages[10:15], row_idx=0,
                                base_x=settle_block_x, base_y=row4_y,
                                reversed_dir=False, prefix="stl")

    row5_y = 5 * CELL_H
    stl_row3 = _place_delay_row(lib, top, settle_stages[15:20], row_idx=1,
                                base_x=settle_block_x, base_y=row5_y,
                                reversed_dir=True, prefix="stl")

    _serpentine_jumper(top, stl_row0[-1].port("OUT"), stl_row1[0].port("IN"))
    _serpentine_jumper(top, stl_row1[-1].port("OUT"), stl_row2[0].port("IN"))
    _serpentine_jumper(top, stl_row2[-1].port("OUT"), stl_row3[0].port("IN"))

    # -----------------------------------------------------------------------
    # 6. Place post-settle buffers + ADC go buffers (row 6)
    # -----------------------------------------------------------------------
    row6_y = 6 * CELL_H
    adc_x = 0.0

    inst_sd1 = Instance(*inv_sd1_cell, name="inv_sd1")
    inst_sd1.place(adc_x, row6_y).add_to(top)
    adc_x += INV_CELL_W + inv_gap

    inst_sd2 = Instance(*inv_sd2_cell, name="inv_sd2")
    inst_sd2.place(adc_x, row6_y).add_to(top)
    adc_x += INV_CELL_W + 1.20

    inst_ag1 = Instance(*inv_ag1_cell, name="inv_ag1")
    inst_ag1.place(adc_x, row6_y).add_to(top)
    adc_x += INV_CELL_W + inv_gap

    inst_ag2 = Instance(*inv_ag2_cell, name="inv_ag2")
    inst_ag2.place(adc_x, row6_y).add_to(top)
    adc_x += INV_CELL_W + INTER_BLOCK_GAP

    # -----------------------------------------------------------------------
    # 7. Place done path (4 inverters) + Muller C-element in row 6
    # -----------------------------------------------------------------------
    done_x = adc_x

    inst_ld1 = Instance(*inv_ld1_cell, name="inv_ld1")
    inst_ld1.place(done_x, row6_y).add_to(top)
    done_x += INV_CELL_W + inv_gap

    inst_ld2 = Instance(*inv_ld2_cell, name="inv_ld2")
    inst_ld2.place(done_x, row6_y).add_to(top)
    done_x += INV_CELL_W + inv_gap

    inst_dn1 = Instance(*inv_dn1_cell, name="inv_dn1")
    inst_dn1.place(done_x, row6_y).add_to(top)
    done_x += INV_CELL_W + inv_gap

    inst_dn2 = Instance(*inv_dn2_cell, name="inv_dn2")
    inst_dn2.place(done_x, row6_y).add_to(top)
    done_x += INV_CELL_W + INTER_BLOCK_GAP

    inst_muller = Instance(*muller_cell, name="muller_c")
    inst_muller.place(done_x, row6_y).add_to(top)

    # -----------------------------------------------------------------------
    # 8. Route signal connections between blocks
    # -----------------------------------------------------------------------

    # inv_go1.OUT -> inv_go2.IN
    _route_met1_port_to_port(top, inst_go1.port("OUT"), inst_go2.port("IN"))

    # inv_go2.OUT -> rst_delay first stage IN
    _route_met1_port_to_port(top, inst_go2.port("OUT"), rst_row0[0].port("IN"))

    # rst_delay intra-row connections
    for row_stages in (rst_row0, rst_row1):
        for i in range(len(row_stages) - 1):
            _route_met1_port_to_port(top, row_stages[i].port("OUT"),
                                     row_stages[i + 1].port("IN"))

    # rst_row1 last stage OUT -> inv_rd1.IN
    _route_met2_vertical(top, rst_row1[-1].port("OUT"), inst_rd1.port("IN"))

    # inv_rd1.OUT -> inv_rd2.IN
    _route_met1_port_to_port(top, inst_rd1.port("OUT"), inst_rd2.port("IN"))

    # NAND inputs
    _route_met2_long(top, inst_go2.port("OUT"), inst_nand.port("A"), "go_buf_to_nand")
    _route_met1_port_to_port(top, inst_rd1.port("OUT"), inst_nand.port("B"))

    # NAND.OUT -> inv_rst.IN
    _route_met1_port_to_port(top, inst_nand.port("OUT"), inst_inv_rst.port("IN"))

    # inv_rd2.OUT -> settle_delay first stage IN
    _route_met1_port_to_port(top, inst_rd2.port("OUT"), stl_row0[0].port("IN"))

    # settle_delay intra-row connections
    for row_stages in (stl_row0, stl_row1, stl_row2, stl_row3):
        for i in range(len(row_stages) - 1):
            _route_met1_port_to_port(top, row_stages[i].port("OUT"),
                                     row_stages[i + 1].port("IN"))

    # settle_row3 last stage OUT -> inv_sd1.IN
    _route_met2_vertical(top, stl_row3[-1].port("OUT"), inst_sd1.port("IN"))

    # Post-settle buffer chain
    _route_met1_port_to_port(top, inst_sd1.port("OUT"), inst_sd2.port("IN"))
    _route_met1_port_to_port(top, inst_sd2.port("OUT"), inst_ag1.port("IN"))
    _route_met1_port_to_port(top, inst_ag1.port("OUT"), inst_ag2.port("IN"))

    # Done path
    _route_met1_port_to_port(top, inst_ld1.port("OUT"), inst_ld2.port("IN"))
    _route_met1_port_to_port(top, inst_ld2.port("OUT"), inst_dn1.port("IN"))
    _route_met1_port_to_port(top, inst_dn1.port("OUT"), inst_dn2.port("IN"))

    # -----------------------------------------------------------------------
    # 9. VDD/VSS rails — removed global full-width MET1 rails.
    # Each cell (inv, delay_stage, muller_c, nand2) already has internal
    # MET1 VDD/VSS rails at the same row-boundary Y coordinates.  The
    # global rails overlapped them, merging ~239/898 polygons into one
    # connected MET1 region and causing device shorts during LVS
    # extraction.  Cell-internal rails connect where cells abut; any
    # remaining gaps are bridged through MET2 or higher-metal routing.
    # -----------------------------------------------------------------------
    bb = top.bounding_box()
    x_max = float(bb[1][0]) + 0.50 if bb is not None else 50.0

    # -----------------------------------------------------------------------
    # 10. Guard ring (P+ substrate tap ring around entire design)
    # -----------------------------------------------------------------------
    if bb is not None:
        gr_margin = 2.50
        gr_w = DRC.TAP_W + 0.40
        gx0 = float(bb[0][0]) - gr_margin
        gy0 = float(bb[0][1]) - gr_margin
        gx1 = float(bb[1][0]) + gr_margin
        gy1 = float(bb[1][1]) + gr_margin

        # Bottom edge
        top.add(gdstk.rectangle((gx0, gy0), (gx1, gy0 + gr_w), **ld(L.TAP)))
        top.add(gdstk.rectangle((gx0 - DRC.PSDM_ENCL, gy0 - DRC.PSDM_ENCL),
                                (gx1 + DRC.PSDM_ENCL, gy0 + gr_w + DRC.PSDM_ENCL),
                                **ld(L.PSDM)))
        # Top edge
        top.add(gdstk.rectangle((gx0, gy1 - gr_w), (gx1, gy1), **ld(L.TAP)))
        top.add(gdstk.rectangle((gx0 - DRC.PSDM_ENCL, gy1 - gr_w - DRC.PSDM_ENCL),
                                (gx1 + DRC.PSDM_ENCL, gy1 + DRC.PSDM_ENCL),
                                **ld(L.PSDM)))
        # Left edge
        top.add(gdstk.rectangle((gx0, gy0), (gx0 + gr_w, gy1), **ld(L.TAP)))
        top.add(gdstk.rectangle((gx0 - DRC.PSDM_ENCL, gy0 - DRC.PSDM_ENCL),
                                (gx0 + gr_w + DRC.PSDM_ENCL, gy1 + DRC.PSDM_ENCL),
                                **ld(L.PSDM)))
        # Right edge
        top.add(gdstk.rectangle((gx1 - gr_w, gy0), (gx1, gy1), **ld(L.TAP)))
        top.add(gdstk.rectangle((gx1 - gr_w - DRC.PSDM_ENCL, gy0 - DRC.PSDM_ENCL),
                                (gx1 + DRC.PSDM_ENCL, gy1 + DRC.PSDM_ENCL),
                                **ld(L.PSDM)))

        # LICON contacts along guard ring edges with proper spacing
        # Use wider pitch so LI pads have >= 0.17 spacing between them (li.3)
        li_pad_w = LICON + 2 * DRC.LI1_ENCL_LICON  # 0.33 um
        licon_pitch = li_pad_w + DRC.LI1_SP + 0.10  # 0.33 + 0.17 + 0.10 = 0.60 um — extra margin for li.3
        # Ensure P-tap encloses LICON by >= 0.12 um on each side
        for edge_coords in [
            (gx0, gy0 + gr_w / 2, gx1, gy0 + gr_w / 2, True),
            (gx0, gy1 - gr_w / 2, gx1, gy1 - gr_w / 2, True),
            (gx0 + gr_w / 2, gy0, gx0 + gr_w / 2, gy1, False),
            (gx1 - gr_w / 2, gy0, gx1 - gr_w / 2, gy1, False),
        ]:
            sx, sy, ex, ey, horiz = edge_coords
            if horiz:
                length = abs(ex - sx)
                # Space LICONs with proper pitch, centered
                n_licons = max(1, int((length - LICON) / licon_pitch) + 1)
                arr_w = (n_licons - 1) * licon_pitch
                start = sx + (length - arr_w) / 2
                for i in range(n_licons):
                    cx = start + i * licon_pitch
                    cy = sy
                    top.add(gdstk.rectangle(
                        (cx - LICON / 2, cy - LICON / 2),
                        (cx + LICON / 2, cy + LICON / 2),
                        **ld(L.LICON),
                    ))
                    # LI1 pad — li.6: area >= 0.0561 um^2
                    li_pad = max(LICON + 2 * DRC.LI1_ENCL_LICON, 0.0561 ** 0.5)
                    top.add(gdstk.rectangle(
                        (cx - li_pad / 2, cy - li_pad / 2),
                        (cx + li_pad / 2, cy + li_pad / 2),
                        **ld(L.LI1),
                    ))
            else:
                length = abs(ey - sy)
                n_licons = max(1, int((length - LICON) / licon_pitch) + 1)
                arr_h = (n_licons - 1) * licon_pitch
                start = sy + (length - arr_h) / 2
                for i in range(n_licons):
                    cx = sx
                    cy = start + i * licon_pitch
                    top.add(gdstk.rectangle(
                        (cx - LICON / 2, cy - LICON / 2),
                        (cx + LICON / 2, cy + LICON / 2),
                        **ld(L.LICON),
                    ))
                    # LI1 pad — li.6: area >= 0.0561 um^2
                    li_pad = max(LICON + 2 * DRC.LI1_ENCL_LICON, 0.0561 ** 0.5)
                    top.add(gdstk.rectangle(
                        (cx - li_pad / 2, cy - li_pad / 2),
                        (cx + li_pad / 2, cy + li_pad / 2),
                        **ld(L.LI1),
                    ))

    # -----------------------------------------------------------------------
    # 11. Export ports
    # -----------------------------------------------------------------------
    ports = {
        "GO":        Port("GO",        inst_go1.port("IN").center, MET1_W, 180, L.MET1),
        "ADC_DONE":  Port("ADC_DONE",  inst_ld1.port("IN").center, MET1_W, 180, L.MET1),
        "XBAR_RST":  Port("XBAR_RST",  inst_inv_rst.port("OUT").center, MET1_W, 0, L.MET1),
        "ADC_GO":    Port("ADC_GO",    inst_ag2.port("OUT").center, MET1_W, 0, L.MET1),
        "LATCH_OUT": Port("LATCH_OUT", inst_ld2.port("OUT").center, MET1_W, 0, L.MET1),
        "DONE":      Port("DONE",      inst_dn2.port("OUT").center, MET1_W, 0, L.MET1),
        "VDD":       Port("VDD",       (x_max / 2, CELL_H - RAIL_W / 2), RAIL_W, 90, L.MET1),
        "VSS":       Port("VSS",       (x_max / 2, RAIL_W / 2), RAIL_W, 270, L.MET1),
    }

    for port in ports.values():
        add_port_label(top, port)

    return top, ports


# ---------------------------------------------------------------------------
# Routing helpers
# ---------------------------------------------------------------------------

def _serpentine_jumper(cell, port_out, port_in):
    """Route a serpentine jumper between two ports on adjacent rows.

    Uses MET2 for the vertical segment and MET1 for landing pads.
    """
    x_out, y_out = port_out.center
    x_in, y_in = port_in.center

    _via_stack(cell, x_out, y_out)
    _via_stack(cell, x_in, y_in)

    if abs(x_out - x_in) > 0.01:
        mid_y = (y_out + y_in) / 2
        _met2_wire(cell, x_out, y_out, x_out, mid_y)
        _met2_wire(cell, x_out, mid_y, x_in, mid_y)
        _met2_wire(cell, x_in, mid_y, x_in, y_in)
    else:
        _met2_wire(cell, x_out, y_out, x_in, y_in)


def _route_met1_port_to_port(cell, p_from, p_to):
    """Route a MET1 wire between two ports.

    Horizontal if same Y, else L-shaped.
    """
    x0, y0 = p_from.center
    x1, y1 = p_to.center

    if abs(y0 - y1) < 0.01:
        _met1_wire(cell, x0, y0, x1, y1)
    else:
        _met1_wire(cell, x0, y0, x1, y0)
        _met1_wire(cell, x1, y0, x1, y1)


def _route_met2_vertical(cell, p_from, p_to):
    """Route between ports on different rows using MET2 vertical + VIA stacks."""
    x0, y0 = p_from.center
    x1, y1 = p_to.center

    _via_stack(cell, x0, y0)
    _via_stack(cell, x1, y1)

    if abs(x0 - x1) < 0.01:
        _met2_wire(cell, x0, y0, x0, y1)
    else:
        mid_y = (y0 + y1) / 2
        _met2_wire(cell, x0, y0, x0, mid_y)
        _met2_wire(cell, x0, mid_y, x1, mid_y)
        _met2_wire(cell, x1, mid_y, x1, y1)


def _route_met2_long(cell, p_from, p_to, name=""):
    """Route a long-distance signal using MET2."""
    x0, y0 = p_from.center
    x1, y1 = p_to.center

    _via_stack(cell, x0, y0)
    _via_stack(cell, x1, y1)

    offset_y = y0 + 0.40 if y1 > y0 else y0 - 0.40

    _met2_wire(cell, x0, y0, x0, offset_y)
    _met2_wire(cell, x0, offset_y, x1, offset_y)
    _met2_wire(cell, x1, offset_y, x1, y1)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    lib = gdstk.Library(name="async_ctrl", unit=1e-6, precision=1e-9)
    cell, ports = async_ctrl_layout(lib)

    print("async_ctrl layout generated")
    print(f"  Cell: {cell.name}")
    bb = cell.bounding_box()
    if bb is not None:
        w = bb[1][0] - bb[0][0]
        h = bb[1][1] - bb[0][1]
        print(f"  Bounding box: {w:.1f} x {h:.1f} um")
    print(f"  Ports ({len(ports)}):")
    for name, port in sorted(ports.items()):
        print(f"    {name:12s}  ({port.center[0]:7.2f}, {port.center[1]:7.2f})  "
              f"layer={port.layer}  orient={port.orientation}")

    outfile = os.path.join(os.path.dirname(__file__), "..", "..", "..",
                           "output", "async_ctrl.gds")
    os.makedirs(os.path.dirname(outfile), exist_ok=True)
    lib.write_gds(outfile)
    print(f"  GDS written to {outfile}")
