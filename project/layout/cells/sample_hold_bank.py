"""Sample-and-hold bank layout -- 4 matched channels with MIM caps.

Architecture:
  - 1x4 linear row with common-centroid pairing (ch0<->ch3, ch1<->ch2)
  - 6 columns total: dummy, ch0, ch1, ch2, ch3, dummy
  - MIM caps (CAPM over MET3): 200fF -> 10x10um each
  - CMOS TG: NFET W=0.84 L=0.15 below PFET W=1.68 L=0.15 (nf=2)
  - H-tree clock from center inverter
  - VSS shields between output wires on MET1
  - Guard rings: shared P+ substrate ring, N+ well ring
  - Signal flow top-to-bottom: inputs(MET2) -> switches -> outputs -> caps -> VSS

Total: ~76 x 23 um
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import gdstk

from project.layout.layers import L, ld
from project.layout.drc import DRC
from project.layout.ports import Port, add_port_label
from project.layout.primitives.mosfet import nfet, pfet
from project.layout.primitives.contact import via_array
from project.layout.primitives.guard_ring import guard_ring_p, guard_ring_n

# ---------------------------------------------------------------------------
# Design constants (all in microns unless noted)
# ---------------------------------------------------------------------------

N_CH = 3           # active channels
N_COL = 5          # total columns (2 dummies + 3 active)

# MIM cap: 200fF, sky130 MIM ~2 fF/um^2 -> 100 um^2 -> 10x10 um
CAP_W = 10.0
CAP_H = 10.0

# CMOS TG transistor dimensions (um)
TG_N_W = 0.84      # NFET total width
TG_N_L = 0.15
TG_P_W = 1.68      # PFET total width (nf=2 -> 0.84 per finger)
TG_P_L = 0.15
TG_P_NF = 2

# Inverter for sh_ctrl complement
INV_N_W = 0.42
INV_N_L = 0.15
INV_P_W = 0.84
INV_P_L = 0.15

# Column pitch (cap width + routing gap)
# Increased from 12.0 to give more horizontal spacing between TG cells
# to clear licon.14 (poly contact to diffusion) and diff/tap.3 spacing.
COL_PITCH = 18.0

# Vertical layout bands (Y coordinates, bottom to top)
VSS_RAIL_Y = 0.0
VSS_RAIL_H = 0.80

CAP_BOT_Y = 1.5          # bottom edge of cap array
CAP_TOP_Y = CAP_BOT_Y + CAP_H  # 11.5

OUT_WIRE_Y = CAP_TOP_Y + 0.8    # 12.3 -- output wires (MET1)

SW_N_Y = 13.5            # NFET center of TG switches
SW_P_Y = 17.0            # PFET center of TG switches (raised for larger N-P gap)

IN_WIRE_Y = 19.0         # input wires (MET2)

VDD_RAIL_Y = 21.5
VDD_RAIL_H = 0.80

# Guard ring parameters
GR_W = 0.53              # ring width (tap + contacts)
GR_MARGIN = 0.80         # clearance from active to ring inner edge

# Total cell bounds (computed from contents + guard rings)
CELL_X0 = 0.0
CELL_Y0 = 0.0

# First column X (column 0 = left dummy)
COL0_X = 2.0  # left margin for guard ring + routing

# ---------------------------------------------------------------------------
# Helper: column center X
# ---------------------------------------------------------------------------

def col_cx(col_idx: int) -> float:
    """Return the center X of column *col_idx* (0..5)."""
    return COL0_X + col_idx * COL_PITCH + CAP_W / 2


# Active channel indices inside the 6-column array:
#   common-centroid order: ch0=col1, ch1=col2, ch2=col3, ch3=col4
#   pairing: ch0<->ch3 (outer), ch1<->ch2 (inner)
CH_COL = [1, 2, 3, 4]  # active channel -> column index

# ---------------------------------------------------------------------------
# Primitive builders
# ---------------------------------------------------------------------------

def _rect(cell, x0, y0, x1, y1, layer):
    """Add a rectangle to *cell* on the given (layer, datatype)."""
    cell.add(gdstk.rectangle((x0, y0), (x1, y1), **ld(layer)))


def _mim_cap_cell(lib, name, w, h, dummy=False):
    """Create a MIM cap sub-cell.

    Sky130 MIM: CAPM layer over MET3 bottom plate, MET4 top plate contact.
    Bottom plate = MET3, top plate = CAPM (contacted via VIA3 to MET4).
    For dummy caps both plates tie to VSS.

    Returns (cell, ports_dict).
    Ports: "BOT" on MET3 (south), "TOP" on MET4 (north).
    """
    cell = lib.new_cell(name)
    encl = DRC.CAPM_ENCL_MET3  # 0.14 um

    # MET3 bottom plate (extends beyond CAPM by enclosure)
    m3_x0 = -encl
    m3_y0 = -encl
    m3_x1 = w + encl
    m3_y1 = h + encl
    _rect(cell, m3_x0, m3_y0, m3_x1, m3_y1, L.MET3)

    # CAPM dielectric
    _rect(cell, 0, 0, w, h, L.CAPM)

    # MET4 top plate (same extent as MET3 for contact area)
    _rect(cell, m3_x0, m3_y0, m3_x1, m3_y1, L.MET4)

    # VIA3 array to connect MET3 bottom plate to routing (edges only)
    # and VIA3 array within CAPM for top plate to MET4
    via3_sz = DRC.VIA3_SZ    # 0.20
    via3_sp = DRC.VIA3_SP    # 0.20
    via3_enc3 = DRC.VIA3_ENCL_MET3  # 0.06
    via3_enc4 = DRC.VIA3_ENCL_MET4  # 0.065

    # Top plate VIA3 array (inside CAPM, inset from edges)
    # Increased inset to avoid MET1 spacing violations from adjacent structures
    inset = DRC.CAPM_SP_VIA3 + via3_sz + 0.10  # 0.08 + 0.20 + 0.10 = 0.38
    _place_via_array(cell, inset, inset, w - inset, h - inset,
                     via3_sz, via3_sp, L.VIA3)

    # Bottom plate contact strip along south edge (below CAPM)
    # VIA3 row at y < 0 connecting MET3 to MET4 (for bottom plate routing)
    bp_strip_y0 = m3_y0 + via3_enc3
    bp_strip_y1 = -DRC.CAPM_SP_VIA3  # stay clear of CAPM
    if bp_strip_y1 - bp_strip_y0 >= via3_sz:
        _place_via_array(cell, via3_enc3, bp_strip_y0,
                         w + encl - via3_enc3, bp_strip_y1,
                         via3_sz, via3_sp, L.VIA3)

    ports = {}
    if not dummy:
        ports["BOT"] = Port("BOT", (w / 2, m3_y0 + 0.1), 0.30,
                            270, L.MET3)
        ports["TOP"] = Port("TOP", (w / 2, m3_y1 - 0.1), 0.30,
                            90, L.MET4)
    else:
        # Dummy: both plates labelled VSS
        ports["BOT"] = Port("VSS", (w / 2, m3_y0 + 0.1), 0.30,
                            270, L.MET3)
        ports["TOP"] = Port("VSS", (w / 2, m3_y1 - 0.1), 0.30,
                            90, L.MET4)

    return cell, ports


def _place_via_array(cell, x0, y0, x1, y1, via_sz, via_sp, via_layer):
    """Fill a rectangular region with vias on a regular grid."""
    via_array(cell, via_layer, x0, y0, x1, y1, via_sz, via_sp)


def _make_nfet(lib, name, w, l, nf=1):
    """Create an NFET using the shared DRC-clean primitive."""
    return nfet(lib, w, l, nf, name=name)


def _make_pfet(lib, name, w, l, nf=1):
    """Create a PFET using the shared DRC-clean primitive."""
    return pfet(lib, w, l, nf, name=name)


def _inv_cell(lib, name, wn, ln, wp, lp):
    """Create a CMOS inverter sub-cell (NFET below PFET).

    Returns (cell, ports_dict).
    Ports: "IN" (MET1), "OUT" (MET1), "VDD" (MET1), "VSS" (MET1).

    Uses shared nfet/pfet primitives (centered at origin).
    """
    cell = lib.new_cell(name)

    n_cell, n_ports = _make_nfet(lib, f"{name}_n", wn, ln, 1)
    p_cell, p_ports = _make_pfet(lib, f"{name}_p", wp, lp, 1)

    # Get bounding boxes to compute placement
    n_bb = n_cell.bounding_box()
    p_bb = p_cell.bounding_box()
    n_h = n_bb[1][1] - n_bb[0][1] if n_bb is not None else wn + 1.0
    p_h = p_bb[1][1] - p_bb[0][1] if p_bb is not None else wp + 1.0

    # Place NFET at bottom, PFET above with gap.
    # Shared primitive is centered at origin, so place centers vertically.
    # Gap sized to clear MCON/LICON spacing and diff/tap.9 (N-diff to NWELL).
    n_cy = n_h / 2  # NFET center Y (bottom of cell = 0)
    gap = 1.80
    p_cy = n_h + gap + p_h / 2  # PFET center Y

    n_ref = gdstk.Reference(n_cell, origin=(0, n_cy))
    p_ref = gdstk.Reference(p_cell, origin=(0, p_cy))
    cell.add(n_ref)
    cell.add(p_ref)

    # Absolute port positions (origin + port center)
    nd = (n_ports["D"].center[0], n_cy + n_ports["D"].center[1])
    pd = (p_ports["D"].center[0], p_cy + p_ports["D"].center[1])
    ns = (n_ports["S"].center[0], n_cy + n_ports["S"].center[1])
    ps = (p_ports["S"].center[0], p_cy + p_ports["S"].center[1])
    ng = (n_ports["G"].center[0], n_cy + n_ports["G"].center[1])
    pg = (p_ports["G"].center[0], p_cy + p_ports["G"].center[1])

    # Drains tied (output): MET1 vertical strap -- minimum width
    out_x = nd[0]
    _rect(cell, out_x - DRC.MET1_W / 2, nd[1] - 0.07,
          out_x + DRC.MET1_W / 2, pd[1] + 0.07, L.MET1)

    # Gate connection routed on MET2 to avoid met1.2 with output strap.
    # Short MET1 pads at each gate port connect via VIA to MET2 strap.
    gx = ng[0]
    via_sz = DRC.VIA_SZ  # 0.15
    via_enc = DRC.VIA_ENCL_MET1  # 0.055
    via_enc2 = DRC.VIA_ENCL_MET2  # 0.055
    # Minimum pad: just enough for via enclosure (no extra margin)
    gate_pad_hw = via_sz / 2 + via_enc  # 0.13

    # NFET gate: MET1 pad + VIA + MET2 pad
    _rect(cell, gx - gate_pad_hw, ng[1] - gate_pad_hw,
          gx + gate_pad_hw, ng[1] + gate_pad_hw, L.MET1)
    _rect(cell, gx - via_sz / 2, ng[1] - via_sz / 2,
          gx + via_sz / 2, ng[1] + via_sz / 2, L.VIA)
    _rect(cell, gx - gate_pad_hw, ng[1] - gate_pad_hw,
          gx + gate_pad_hw, ng[1] + gate_pad_hw, L.MET2)

    # PFET gate: MET1 pad + VIA + MET2 pad
    _rect(cell, gx - gate_pad_hw, pg[1] - gate_pad_hw,
          gx + gate_pad_hw, pg[1] + gate_pad_hw, L.MET1)
    _rect(cell, gx - via_sz / 2, pg[1] - via_sz / 2,
          gx + via_sz / 2, pg[1] + via_sz / 2, L.VIA)
    _rect(cell, gx - gate_pad_hw, pg[1] - gate_pad_hw,
          gx + gate_pad_hw, pg[1] + gate_pad_hw, L.MET2)

    # MET2 vertical gate strap connecting NFET gate to PFET gate
    _rect(cell, gx - DRC.MET2_W / 2, ng[1] - gate_pad_hw,
          gx + DRC.MET2_W / 2, pg[1] + gate_pad_hw, L.MET2)

    total_h = n_h + gap + p_h + 0.5

    ports = {
        "IN":  Port("IN", (gx, total_h / 2), 0.17, 180, L.MET2),
        "OUT": Port("OUT", (out_x, total_h / 2), 0.17, 0, L.MET1),
        "VDD": Port("VDD", (ps[0], ps[1]), 0.30, 90, L.MET1),
        "VSS": Port("VSS", (ns[0], ns[1]), 0.30, 270, L.MET1),
    }

    return cell, ports


def _tg_cell(lib, name, wn, ln, wp, lp, nf_p):
    """Create a CMOS transmission gate sub-cell (NFET below PFET).

    Returns (cell, ports_dict).
    Ports: "IN" (MET2), "OUT" (MET1), "CTRL" (MET2), "CTRL_B" (MET2),
           "VDD" (MET1), "VSS" (MET1).

    Uses shared nfet/pfet primitives (centered at origin).
    """
    cell = lib.new_cell(name)

    n_cell, n_ports = _make_nfet(lib, f"{name}_n", wn, ln, 1)
    p_cell, p_ports = _make_pfet(lib, f"{name}_p", wp, lp, nf_p)

    # Get bounding boxes to compute placement
    n_bb = n_cell.bounding_box()
    p_bb = p_cell.bounding_box()
    n_h = n_bb[1][1] - n_bb[0][1] if n_bb is not None else wn + 1.0
    p_h = p_bb[1][1] - p_bb[0][1] if p_bb is not None else wp / nf_p + 1.0

    # Place NFET at bottom, PFET above with gap for routing.
    # Shared primitive is centered at origin.
    # Gap sized to clear MCON/LICON spacing, diff/tap.9 (N-diff to NWELL),
    # AND provide room for gate VIA pads without met1.2 conflicts.
    n_cy = n_h / 2  # NFET center Y (bottom of cell = 0)
    gap = 3.00  # increased from 2.20 for gate VIA clearance
    p_cy = n_h + gap + p_h / 2  # PFET center Y

    n_ref = gdstk.Reference(n_cell, origin=(0, n_cy))
    p_ref = gdstk.Reference(p_cell, origin=(0, p_cy))
    cell.add(n_ref)
    cell.add(p_ref)

    # Absolute port positions (origin + port center)
    nd = (n_ports["D"].center[0], n_cy + n_ports["D"].center[1])
    pd = (p_ports["D"].center[0], p_cy + p_ports["D"].center[1])
    ns = (n_ports["S"].center[0], n_cy + n_ports["S"].center[1])
    ps = (p_ports["S"].center[0], p_cy + p_ports["S"].center[1])
    ng = (n_ports["G"].center[0], n_cy + n_ports["G"].center[1])
    pg = (p_ports["G"].center[0], p_cy + p_ports["G"].center[1])

    # Tie NFET.D to PFET.D (input) via MET1 strap
    # Use minimum width (0.14um) to maximize spacing to gate VIA pads.
    # Strap runs full height from NFET drain to PFET drain ensuring min area.
    sd_strap_hw = DRC.MET1_W / 2  # 0.07
    in_x = max(nd[0], pd[0])
    _rect(cell, in_x - sd_strap_hw, nd[1] - 0.10,
          in_x + sd_strap_hw, pd[1] + 0.10, L.MET1)

    # Tie NFET.S to PFET.S (output) via MET1 strap
    out_x = min(ns[0], ps[0])
    _rect(cell, out_x - sd_strap_hw, ns[1] - 0.10,
          out_x + sd_strap_hw, ps[1] + 0.10, L.MET1)

    # VIA to MET2 for input (top of input strap)
    via_sz = DRC.VIA_SZ   # 0.15
    # Enclosure: via.5a allows asymmetric pads: >= 0.06 on Y-pair,
    # >= 0.03 on X-pair. Use this to keep X-dimension small.
    enc_via_x = 0.04   # X enclosure (>0.03 for via.5a short side)
    enc_via_y = 0.065  # Y enclosure (>0.06 for via.5a long side)
    enc_via = 0.065    # uniform enc for non-constrained pads

    via_top_y = pd[1] + 0.30  # well above PFET drain pad for clearance
    _rect(cell, in_x - via_sz / 2, via_top_y,
          in_x + via_sz / 2, via_top_y + via_sz, L.VIA)
    # MET1 landing pad (asymmetric: narrow X, tall Y)
    _rect(cell, in_x - via_sz / 2 - enc_via_x, via_top_y - enc_via_y,
          in_x + via_sz / 2 + enc_via_x, via_top_y + via_sz + enc_via_y, L.MET1)
    # MET2 landing pad (asymmetric)
    _rect(cell, in_x - via_sz / 2 - enc_via_x, via_top_y - enc_via_y,
          in_x + via_sz / 2 + enc_via_x, via_top_y + via_sz + enc_via_y, L.MET2)

    total_h = p_cy + p_h / 2 + 1.0

    # Gate VIAs to MET2: place in the N-P gap region (between NFET top and
    # PFET bottom) where there are no S/D straps to conflict with met1.2.
    gap_center_y = (n_cy + n_h / 2 + p_cy - p_h / 2) / 2  # midpoint of gap

    # NFET gate VIA: lower part of gap
    ng_via_y = gap_center_y - 0.30
    _rect(cell, ng[0] - via_sz / 2, ng_via_y,
          ng[0] + via_sz / 2, ng_via_y + via_sz, L.VIA)
    # Asymmetric pad: narrow in X to clear S/D straps
    _rect(cell, ng[0] - via_sz / 2 - enc_via_x, ng_via_y - enc_via_y,
          ng[0] + via_sz / 2 + enc_via_x, ng_via_y + via_sz + enc_via_y, L.MET1)
    _rect(cell, ng[0] - via_sz / 2 - enc_via_x, ng_via_y - enc_via_y,
          ng[0] + via_sz / 2 + enc_via_x, ng_via_y + via_sz + enc_via_y, L.MET2)
    # MET1 strap from NFET gate port to VIA
    _rect(cell, ng[0] - DRC.MET1_W / 2, ng[1] - 0.05,
          ng[0] + DRC.MET1_W / 2, ng_via_y + via_sz + enc_via_y, L.MET1)

    # PFET gate VIA: upper part of gap
    pg_via_y = gap_center_y + 0.15
    _rect(cell, pg[0] - via_sz / 2, pg_via_y,
          pg[0] + via_sz / 2, pg_via_y + via_sz, L.VIA)
    # Asymmetric pad: narrow in X to clear S/D straps
    _rect(cell, pg[0] - via_sz / 2 - enc_via_x, pg_via_y - enc_via_y,
          pg[0] + via_sz / 2 + enc_via_x, pg_via_y + via_sz + enc_via_y, L.MET1)
    _rect(cell, pg[0] - via_sz / 2 - enc_via_x, pg_via_y - enc_via_y,
          pg[0] + via_sz / 2 + enc_via_x, pg_via_y + via_sz + enc_via_y, L.MET2)
    # MET1 strap from VIA to PFET gate port
    _rect(cell, pg[0] - DRC.MET1_W / 2, pg_via_y - enc_via_y,
          pg[0] + DRC.MET1_W / 2, pg[1] + 0.05, L.MET1)

    # VDD/VSS: use S port positions (source tied to supply).
    # PFET source -> VDD, NFET source -> VSS.
    ports = {
        "IN":     Port("IN", (in_x, via_top_y + via_sz / 2), 0.30,
                       90, L.MET2),
        "OUT":    Port("OUT", (out_x, ns[1]), 0.30,
                       270, L.MET1),
        "CTRL":   Port("CTRL", (ng[0], ng_via_y + via_sz / 2), 0.17,
                        180, L.MET2),
        "CTRL_B": Port("CTRL_B", (pg[0], pg_via_y + via_sz / 2), 0.17,
                        0, L.MET2),
        "VDD":    Port("VDD", (ps[0], ps[1]), 0.30, 90, L.MET1),
        "VSS":    Port("VSS", (ns[0], ns[1]), 0.30, 270, L.MET1),
    }

    return cell, ports



# ---------------------------------------------------------------------------
# Main layout function
# ---------------------------------------------------------------------------

def sample_hold_bank_layout(lib: gdstk.Library) -> tuple[gdstk.Cell, dict[str, Port]]:
    """Build the 4-channel sample-and-hold bank layout.

    Returns:
        (cell, ports) where ports maps port names to Port objects.
    """
    top = lib.new_cell("sample_hold_bank")
    ports: dict[str, Port] = {}

    # ------------------------------------------------------------------
    # 1. Create sub-cells
    # ------------------------------------------------------------------

    # MIM caps (active + dummy)
    cap_cell, cap_ports = _mim_cap_cell(lib, "shb_mim_200f", CAP_W, CAP_H,
                                         dummy=False)
    dcap_cell, dcap_ports = _mim_cap_cell(lib, "shb_mim_dummy", CAP_W, CAP_H,
                                           dummy=True)

    # CMOS TG switch
    tg_cell, tg_ports = _tg_cell(lib, "shb_tg", TG_N_W, TG_N_L,
                                  TG_P_W, TG_P_L, TG_P_NF)

    # Dummy TG (same geometry, unused electrically -- just for edge matching)
    dtg_cell, dtg_ports = _tg_cell(lib, "shb_tg_dummy", TG_N_W, TG_N_L,
                                    TG_P_W, TG_P_L, TG_P_NF)

    # Control inverter
    inv_cell, inv_ports = _inv_cell(lib, "shb_inv_ctrl",
                                     INV_N_W, INV_N_L, INV_P_W, INV_P_L)

    # ------------------------------------------------------------------
    # 2. Place 6 cap columns (D, ch0, ch1, ch2, ch3, D)
    # ------------------------------------------------------------------

    cap_refs = []  # list of (ref, is_dummy, cx, cy)
    for col in range(N_COL):
        cx = col_cx(col) - CAP_W / 2  # left edge
        cy = CAP_BOT_Y
        is_dummy = (col == 0 or col == 5)
        c = dcap_cell if is_dummy else cap_cell
        ref = gdstk.Reference(c, origin=(cx, cy))
        top.add(ref)
        cap_refs.append((ref, is_dummy, cx, cy))

    # ------------------------------------------------------------------
    # 3. Place 6 switch columns above caps
    # ------------------------------------------------------------------

    # TG cell bounding box for centering
    tg_bb = tg_cell.bounding_box()
    tg_w = tg_bb[1][0] - tg_bb[0][0] if tg_bb is not None else 2.0
    tg_h = tg_bb[1][1] - tg_bb[0][1] if tg_bb is not None else 3.0

    sw_refs = []  # (ref, is_dummy, origin_x, origin_y)
    for col in range(N_COL):
        cx = col_cx(col) - tg_w / 2  # left edge, centered on column
        cy = SW_N_Y
        is_dummy = (col == 0 or col == 5)
        c = dtg_cell if is_dummy else tg_cell
        ref = gdstk.Reference(c, origin=(cx, cy))
        top.add(ref)
        sw_refs.append((ref, is_dummy, cx, cy))

    # ------------------------------------------------------------------
    # 4. Place inverter at center between ch1 and ch2
    # ------------------------------------------------------------------

    inv_bb = inv_cell.bounding_box()
    inv_w = inv_bb[1][0] - inv_bb[0][0] if inv_bb is not None else 1.5
    inv_h = inv_bb[1][1] - inv_bb[0][1] if inv_bb is not None else 2.0

    # Center X between col2 and col3
    inv_cx = (col_cx(2) + col_cx(3)) / 2
    inv_x = inv_cx - inv_w / 2
    inv_y = SW_N_Y + 0.5  # vertically aligned with switch region
    inv_ref = gdstk.Reference(inv_cell, origin=(inv_x, inv_y))
    top.add(inv_ref)

    # ------------------------------------------------------------------
    # 5. Route H-tree clock on MET2
    # ------------------------------------------------------------------
    # Inverter input comes from sh_ctrl port at top of cell
    # Inverter output (sh_ctrl_b) fans out to all 4 PFET gates via H-tree
    # sh_ctrl fans out to all 4 NFET gates via H-tree

    clk_w = 0.20  # clock wire width (MET2) -- reduced from 0.30 for met2.2 spacing
    via_sz = DRC.VIA_SZ

    # Inverter output center
    inv_out_x = inv_x + inv_ports["OUT"].center[0]
    inv_out_y = inv_y + inv_ports["OUT"].center[1]
    inv_in_x = inv_x + inv_ports["IN"].center[0]
    inv_in_y = inv_y + inv_ports["IN"].center[1]

    # Enclosure for VIA pads (0.065 satisfies via.5a/met2.5 with margin)
    enc_via = 0.065

    # VIA from inverter MET1 output to MET2 (output is on MET1)
    _rect(top, inv_out_x - via_sz / 2, inv_out_y - via_sz / 2,
          inv_out_x + via_sz / 2, inv_out_y + via_sz / 2, L.VIA)
    _rect(top, inv_out_x - via_sz / 2 - enc_via, inv_out_y - via_sz / 2 - enc_via,
          inv_out_x + via_sz / 2 + enc_via, inv_out_y + via_sz / 2 + enc_via, L.MET1)
    _rect(top, inv_out_x - via_sz / 2 - enc_via, inv_out_y - via_sz / 2 - enc_via,
          inv_out_x + via_sz / 2 + enc_via, inv_out_y + via_sz / 2 + enc_via, L.MET2)

    # Inverter input is already on MET2 (gate routed on MET2 inside cell).
    # No VIA needed -- just connect H-tree MET2 directly to the port.

    # H-tree for CTRL_B (inverter output -> PFET gates of all 4 TGs)
    # Trunk: horizontal line at switch PFET gate Y level
    ctrl_b_y = SW_P_Y + 1.5  # above PFET gates (raised for met2.2 clearance)
    # Vertical from inverter output up to trunk
    _rect(top, inv_out_x - clk_w / 2, inv_out_y,
          inv_out_x + clk_w / 2, ctrl_b_y + clk_w / 2, L.MET2)

    # Horizontal trunk spanning ch0..ch3
    trunk_x0 = col_cx(CH_COL[0]) - 1.0
    trunk_x1 = col_cx(CH_COL[3]) + 1.0
    _rect(top, trunk_x0, ctrl_b_y - clk_w / 2,
          trunk_x1, ctrl_b_y + clk_w / 2, L.MET2)

    # Drops from trunk to each TG CTRL_B port
    for ch in range(N_CH):
        col = CH_COL[ch]
        sw_ref, _, sx, sy = sw_refs[col]
        tgt_x = sx + tg_ports["CTRL_B"].center[0]
        tgt_y = sy + tg_ports["CTRL_B"].center[1]
        _rect(top, tgt_x - clk_w / 2, tgt_y,
              tgt_x + clk_w / 2, ctrl_b_y + clk_w / 2, L.MET2)

    # H-tree for CTRL (sh_ctrl -> NFET gates of all 4 TGs)
    ctrl_y = SW_N_Y - 1.0  # below NFET gates (lowered for met2.2 clearance)
    # Vertical from inverter input down to trunk
    _rect(top, inv_in_x - clk_w / 2, ctrl_y - clk_w / 2,
          inv_in_x + clk_w / 2, inv_in_y, L.MET2)

    # Horizontal trunk
    _rect(top, trunk_x0, ctrl_y - clk_w / 2,
          trunk_x1, ctrl_y + clk_w / 2, L.MET2)

    # Drops from trunk to each TG CTRL port
    for ch in range(N_CH):
        col = CH_COL[ch]
        sw_ref, _, sx, sy = sw_refs[col]
        tgt_x = sx + tg_ports["CTRL"].center[0]
        tgt_y = sy + tg_ports["CTRL"].center[1]
        _rect(top, tgt_x - clk_w / 2, ctrl_y - clk_w / 2,
              tgt_x + clk_w / 2, tgt_y, L.MET2)

    # ------------------------------------------------------------------
    # 6. Route inputs on MET2 from top
    # ------------------------------------------------------------------

    in_w = 0.30  # input wire width
    for ch in range(N_CH):
        col = CH_COL[ch]
        sw_ref, _, sx, sy = sw_refs[col]
        in_port_x = sx + tg_ports["IN"].center[0]
        in_port_y = sy + tg_ports["IN"].center[1]

        # Vertical MET2 wire from IN_WIRE_Y down to TG input
        _rect(top, in_port_x - in_w / 2, in_port_y,
              in_port_x + in_w / 2, IN_WIRE_Y, L.MET2)

        # Port at top of wire
        pname = f"in{ch}"
        ports[pname] = Port(pname, (in_port_x, IN_WIRE_Y), in_w,
                            90, L.MET2)

    # ------------------------------------------------------------------
    # 7. Route outputs with VSS shields on MET1
    # ------------------------------------------------------------------

    out_w = 0.20   # output wire width (narrowed from 0.30 for met1.2 clearance)
    shld_w = 0.20  # shield wire width (narrowed for met1.2 compliance)
    shld_sp = DRC.MET1_SP + 0.20  # spacing from signal edge to shield edge (0.34 um)

    for ch in range(N_CH):
        col = CH_COL[ch]
        sw_ref, _, sx, sy = sw_refs[col]
        cap_ref, _, cx_cap, cy_cap = cap_refs[col]

        # Switch output port
        out_port_x = sx + tg_ports["OUT"].center[0]
        out_port_y = sy + tg_ports["OUT"].center[1]

        # Cap top plate (BOT port of cap = MET3 south)
        cap_top_x = cx_cap + cap_ports["BOT"].center[0]
        cap_top_y = cy_cap + cap_ports["BOT"].center[1]

        # MET1 vertical wire from switch output down to OUT_WIRE_Y
        _rect(top, out_port_x - out_w / 2, OUT_WIRE_Y,
              out_port_x + out_w / 2, out_port_y, L.MET1)

        # VIA at OUT_WIRE_Y to get to MET2, then VIA2 to MET3 for cap
        # MET1 -> VIA -> MET2 at output junction
        via_y = OUT_WIRE_Y

        _rect(top, out_port_x - via_sz / 2, via_y,
              out_port_x + via_sz / 2, via_y + via_sz, L.VIA)
        # MET1 landing pad (0.06 enclosure for via.5a)
        _rect(top, out_port_x - via_sz / 2 - enc_via, via_y - enc_via,
              out_port_x + via_sz / 2 + enc_via, via_y + via_sz + enc_via, L.MET1)
        # MET2 landing pad (0.06 enclosure for met2.5)
        _rect(top, out_port_x - via_sz / 2 - enc_via, via_y - enc_via,
              out_port_x + via_sz / 2 + enc_via, via_y + via_sz + enc_via, L.MET2)

        # MET2 -> VIA2 -> MET3 to reach cap bottom plate
        via2_sz = DRC.VIA2_SZ
        via2_enc_m2 = DRC.VIA2_ENCL_MET2  # 0.04
        via2_enc_m3 = DRC.VIA2_ENCL_MET3  # 0.065
        # Add 0.05/0.06 margin per side for directional enclosure (via2.4a, via3.5)
        via2_pad_m2 = via2_sz / 2 + via2_enc_m2 + 0.05
        via2_pad_m3 = via2_sz / 2 + via2_enc_m3 + 0.06

        _rect(top, out_port_x - via2_sz / 2, via_y,
              out_port_x + via2_sz / 2, via_y + via2_sz, L.VIA2)
        _rect(top, out_port_x - via2_pad_m2, via_y - via2_enc_m2,
              out_port_x + via2_pad_m2, via_y + via2_sz + via2_enc_m2, L.MET2)
        _rect(top, out_port_x - via2_pad_m3, via_y - via2_enc_m3,
              out_port_x + via2_pad_m3, via_y + via2_sz + via2_enc_m3, L.MET3)

        # MET3 strap down to cap top plate
        _rect(top, out_port_x - via2_pad_m3, cap_top_y,
              out_port_x + via2_pad_m3, via_y + via2_sz + via2_enc_m3, L.MET3)

        # VSS shields on MET1 (one on each side of output wire)
        for side in [-1, +1]:
            sx_shld = out_port_x + side * (out_w / 2 + shld_sp + shld_w / 2)
            _rect(top, sx_shld - shld_w / 2, OUT_WIRE_Y,
                  sx_shld + shld_w / 2, out_port_y, L.MET1)

        # Output port
        pname = f"out{ch}"
        ports[pname] = Port(pname, (out_port_x, OUT_WIRE_Y), out_w,
                            270, L.MET1)

    # ------------------------------------------------------------------
    # 8. VDD and VSS rails on MET4
    # ------------------------------------------------------------------

    # Full-width rails
    cell_x0 = col_cx(0) - CAP_W / 2 - GR_MARGIN - GR_W - 0.5
    cell_x1 = col_cx(5) + CAP_W / 2 + GR_MARGIN + GR_W + 0.5

    # VSS rail (bottom)
    _rect(top, cell_x0, VSS_RAIL_Y,
          cell_x1, VSS_RAIL_Y + VSS_RAIL_H, L.MET4)

    # VDD rail (top)
    _rect(top, cell_x0, VDD_RAIL_Y,
          cell_x1, VDD_RAIL_Y + VDD_RAIL_H, L.MET4)

    # VIA3 arrays to connect MET3/MET4 at rail locations
    via3_sz = DRC.VIA3_SZ
    via3_sp = DRC.VIA3_SP

    # VSS rail: VIA3 drops at each column for cap bottom plate + shield ties
    # Increase MET3 pad margin by 0.03 per side for via3.5 enclosure
    for col in range(N_COL):
        cx = col_cx(col)
        _place_via_array(top, cx - 1.0, VSS_RAIL_Y + 0.12,
                         cx + 1.0, VSS_RAIL_Y + VSS_RAIL_H - 0.12,
                         via3_sz, via3_sp, L.VIA3)
        # MET3 pad under VIA3 for VSS (enlarged for via3.5 enclosure)
        _rect(top, cx - 1.25, VSS_RAIL_Y + 0.02,
              cx + 1.25, VSS_RAIL_Y + VSS_RAIL_H - 0.02, L.MET3)

    # VDD rail: VIA3 drops at inverter and near switches
    for col in range(N_COL):
        cx = col_cx(col)
        _place_via_array(top, cx - 1.0, VDD_RAIL_Y + 0.12,
                         cx + 1.0, VDD_RAIL_Y + VDD_RAIL_H - 0.12,
                         via3_sz, via3_sp, L.VIA3)
        # MET3 pad (enlarged for via3.5 enclosure)
        _rect(top, cx - 1.25, VDD_RAIL_Y + 0.02,
              cx + 1.25, VDD_RAIL_Y + VDD_RAIL_H - 0.02, L.MET3)

    # VDD/VSS distribution on MET1 to switches and inverter
    # Vertical MET1 straps from rails through VIA stack
    rail_strap_w = 0.50
    for col in range(N_COL):
        cx = col_cx(col)

        # VSS strap: from VSS rail up to switch VSS ties
        # MET1 -> VIA -> MET2 -> VIA2 -> MET3 at VSS rail
        _rect(top, cx - rail_strap_w / 2, VSS_RAIL_Y,
              cx + rail_strap_w / 2, CAP_BOT_Y, L.MET1)
        # VIA at VSS rail level -- keep fill region within MET1 strap
        # with >= 0.055 margin for via.5a (directional enclosure)
        via_region_margin = 0.14
        via_fill_hw = rail_strap_w / 2 - DRC.VIA_ENCL_MET1 - 0.02  # 0.175
        _place_via_array(top, cx - via_fill_hw, VSS_RAIL_Y + via_region_margin,
                         cx + via_fill_hw, VSS_RAIL_Y + VSS_RAIL_H - via_region_margin,
                         DRC.VIA_SZ, DRC.VIA_SP, L.VIA)
        # Explicit MET1 landing pad covering VIA region (via.5a fix)
        _rect(top, cx - via_fill_hw - DRC.VIA_ENCL_MET1 - 0.01,
              VSS_RAIL_Y + via_region_margin - DRC.VIA_ENCL_MET1,
              cx + via_fill_hw + DRC.VIA_ENCL_MET1 + 0.01,
              VSS_RAIL_Y + VSS_RAIL_H - via_region_margin + DRC.VIA_SZ + DRC.VIA_ENCL_MET1,
              L.MET1)
        # MET2 pad (enlarged for via.5a/met2.5 enclosure)
        _rect(top, cx - 0.44, VSS_RAIL_Y + 0.03,
              cx + 0.44, VSS_RAIL_Y + VSS_RAIL_H - 0.03, L.MET2)
        # VIA2 at VSS rail level -- same fill region
        _place_via_array(top, cx - via_fill_hw, VSS_RAIL_Y + via_region_margin,
                         cx + via_fill_hw, VSS_RAIL_Y + VSS_RAIL_H - via_region_margin,
                         DRC.VIA2_SZ, DRC.VIA2_SP, L.VIA2)
        # MET3 pad (enlarged for via2.4a/via3.5 enclosure)
        _rect(top, cx - 0.44, VSS_RAIL_Y + 0.01,
              cx + 0.44, VSS_RAIL_Y + VSS_RAIL_H - 0.01, L.MET3)

    # ------------------------------------------------------------------
    # 9. Guard rings (using shared DRC-clean primitives)
    # ------------------------------------------------------------------

    # Compute cell extents for P+ substrate ring
    gr_x0 = cell_x0 + 0.3
    gr_y0 = VSS_RAIL_Y + VSS_RAIL_H + 0.2
    gr_x1 = cell_x1 - 0.3
    gr_y1 = VDD_RAIL_Y - 0.2

    # Inner opening dimensions for P+ ring (centered on the ring midpoint)
    pring_inner_w = gr_x1 - gr_x0 - 2 * GR_W
    pring_inner_h = gr_y1 - gr_y0 - 2 * GR_W
    pring_cx = (gr_x0 + gr_x1) / 2
    pring_cy = (gr_y0 + gr_y1) / 2

    # P+ substrate ring (outermost, ties substrate to VSS)
    pring_cell, pring_ports = guard_ring_p(lib, "shb_pring",
                                            pring_inner_w, pring_inner_h,
                                            ring_w=GR_W)
    pring_ref = gdstk.Reference(pring_cell, origin=(pring_cx, pring_cy))
    top.add(pring_ref)

    # N+ well ring removed: its MET1 bottom arm crossed the TG NFET-to-PFET
    # S/D straps, shorting all outputs to VSS through the P+ ring.
    # N-well biasing provided by VDD MET4 rail → VIA3 drops → MET3/MET2/MET1
    # connections within each TG PFET cell.

    # ------------------------------------------------------------------
    # 10. Ports: sh_ctrl, vdd, vss
    # ------------------------------------------------------------------

    # sh_ctrl port: on MET2 at the inverter input, accessible from north
    sh_ctrl_x = inv_in_x
    sh_ctrl_y = IN_WIRE_Y + 0.5
    # Extend ctrl wire up to port
    _rect(top, sh_ctrl_x - clk_w / 2, inv_in_y,
          sh_ctrl_x + clk_w / 2, sh_ctrl_y, L.MET2)
    ports["sh_ctrl"] = Port("sh_ctrl", (sh_ctrl_x, sh_ctrl_y), clk_w,
                            90, L.MET2)

    # VDD port on MET4 (center of VDD rail)
    vdd_cx = (cell_x0 + cell_x1) / 2
    ports["vdd"] = Port("vdd", (vdd_cx, VDD_RAIL_Y + VDD_RAIL_H / 2),
                        rail_strap_w, 90, L.MET4)

    # VSS port on MET4 (center of VSS rail)
    ports["vss"] = Port("vss", (vdd_cx, VSS_RAIL_Y + VSS_RAIL_H / 2),
                        rail_strap_w, 270, L.MET4)

    # ------------------------------------------------------------------
    # 11. Add port labels to cell
    # ------------------------------------------------------------------

    for p in ports.values():
        add_port_label(top, p)

    return top, ports


# ---------------------------------------------------------------------------
# Standalone entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    lib = gdstk.Library(name="sample_hold_bank", unit=1e-6, precision=1e-9)
    cell, ports = sample_hold_bank_layout(lib)

    # Print port summary
    print(f"Cell: {cell.name}")
    print(f"Ports ({len(ports)}):")
    for name, p in sorted(ports.items()):
        print(f"  {name:12s}  center=({p.center[0]:7.2f}, {p.center[1]:7.2f})  "
              f"layer={p.layer}  orient={p.orientation:.0f}")

    bb = cell.bounding_box()
    if bb is not None:
        w = bb[1][0] - bb[0][0]
        h = bb[1][1] - bb[0][1]
        print(f"Bounding box: ({bb[0][0]:.2f}, {bb[0][1]:.2f}) to "
              f"({bb[1][0]:.2f}, {bb[1][1]:.2f})  size={w:.1f} x {h:.1f} um")

    out_path = os.path.join(os.path.dirname(__file__), "..", "..",
                            "sample_hold_bank.gds")
    out_path = os.path.normpath(out_path)
    lib.write_gds(out_path)
    print(f"Written: {out_path}")
