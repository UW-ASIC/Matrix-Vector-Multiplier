"""StrongARM latch comparator layout — 9T, Sky130.

Symmetric two-band layout:
  - NFET band (bottom): tail (centered), input pair (inp/inn mirrored),
    cross-coupled NMOS (xnp/xnn flanking inputs)
  - PFET band (top): cross-coupled PMOS (xpp/xpn interdigitated),
    reset switches (rstp/rstn flanking)
  - P+ guard ring around NFET region (N+ ring removed — see section 5)
  - Cross-coupled routing on MET2 with mirror symmetry
  - VDD rail (MET1, top), VSS rail (MET1, bottom)
  - CLK on MET2 horizontal bus

Ports: VINP, VINN, OUTP, OUTN, CLK, VDD, VSS (all on MET1 or MET2).

Transistor sizing (from library/pdks/sky130.py):
  tail:      NFET  W=0.42  L=0.15  nf=1
  inp/inn:   NFET  W=7.0   L=0.15  nf=8  (differential input pair)
  xnp/xnn:  NFET  W=1.0   L=0.15  nf=2  (cross-coupled NMOS latch)
  xpp/xpn:  PFET  W=4.5   L=0.15  nf=6  (cross-coupled PMOS latch)
  rstp/rstn: PFET  W=1.0   L=0.15  nf=2  (reset switches)
"""

import sys
import os
import gdstk

# Allow running standalone or as a package import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from layout.layers import L, ld
from layout.drc import DRC
from layout.ports import Port, add_port_label
from layout.primitives.mosfet import nfet, pfet
from layout.primitives.guard_ring import guard_ring_p
from layout.primitives.contact import via_stack, mcon_array
from layout.compose import Instance
from layout.routing.router import route_straight, route_L


# ============================================================================
# Device dimensions
# ============================================================================

# Sizing from PDK config (sky130.py)
TAIL_W, TAIL_L, TAIL_NF = 0.42, 0.15, 1
IN_W, IN_L, IN_NF = 7.0, 0.15, 8
XN_W, XN_L, XN_NF = 1.0, 0.15, 2
XP_W, XP_L, XP_NF = 4.5, 0.15, 6
RST_W, RST_L, RST_NF = 1.0, 0.15, 2

# Layout geometry helpers
_POLY_PITCH = 0.15 + 0.27   # gate_l + SD_CONTACT_W = 0.42 um
_SD_W = 0.27


def _cell_width(nf):
    """Total horizontal extent of a MOSFET cell's diffusion."""
    return nf * _POLY_PITCH + _SD_W


def _cell_half_height(w, nf):
    """Half the diffusion height (per-finger width / 2)."""
    return (w / nf) / 2


def _gate_y(w, nf, is_pmos=False):
    """Y-coordinate of the gate contact (above diffusion)."""
    half_wf = _cell_half_height(w, nf)
    licon_sz = DRC.LICON_SZ        # 0.17
    # Must match mosfet.py: gc_y = half_wf + _POLY_LICON_DIFF_SP + licon_sz/2
    _POLY_LICON_DIFF_SP = 0.40
    return half_wf + _POLY_LICON_DIFF_SP + licon_sz / 2


# ============================================================================
# Main layout function
# ============================================================================

def strongarm_layout(lib: gdstk.Library) -> tuple[gdstk.Cell, dict[str, Port]]:
    """Create the StrongARM comparator layout.

    Args:
        lib: gdstk Library to add cells to.

    Returns:
        (cell, ports) — the top-level cell and its port dictionary.
    """
    top = lib.new_cell("strongarm")

    # ------------------------------------------------------------------
    # 1. Generate sub-cells for all 9 FETs
    # ------------------------------------------------------------------
    tail_cell, tail_p = nfet(lib, TAIL_W, TAIL_L, TAIL_NF, "tail")
    inp_cell, inp_p = nfet(lib, IN_W, IN_L, IN_NF, "inp")
    inn_cell, inn_p = nfet(lib, IN_W, IN_L, IN_NF, "inn")
    xnp_cell, xnp_p = nfet(lib, XN_W, XN_L, XN_NF, "xnp")
    xnn_cell, xnn_p = nfet(lib, XN_W, XN_L, XN_NF, "xnn")
    xpp_cell, xpp_p = pfet(lib, XP_W, XP_L, XP_NF, "xpp")
    xpn_cell, xpn_p = pfet(lib, XP_W, XP_L, XP_NF, "xpn")
    rstp_cell, rstp_p = pfet(lib, RST_W, RST_L, RST_NF, "rstp")
    rstn_cell, rstn_p = pfet(lib, RST_W, RST_L, RST_NF, "rstn")

    # ------------------------------------------------------------------
    # 2. Compute placement coordinates
    # ------------------------------------------------------------------
    # All coordinates computed from device bounding boxes and DRC rules.
    # Symmetry axis is at x = 0.

    # --- Row spacing ---
    row_gap = 3.0       # vertical gap between rows (nwell.2a: N-well spacing >= 1.27)
    col_gap = 0.80      # horizontal gap (MCON spacing between adjacent devices)

    # --- Bounding box helpers ---
    def _bbox(cell):
        bb = cell.bounding_box()
        return (float(bb[0][0]), float(bb[0][1]), float(bb[1][0]), float(bb[1][1]))

    tail_bb = _bbox(tail_cell)
    inp_bb = _bbox(inp_cell)
    xnp_bb = _bbox(xnp_cell)
    xpp_bb = _bbox(xpp_cell)
    rstp_bb = _bbox(rstp_cell)

    tail_w = tail_bb[2] - tail_bb[0]
    tail_h = tail_bb[3] - tail_bb[1]
    inp_w = inp_bb[2] - inp_bb[0]
    inp_h = inp_bb[3] - inp_bb[1]
    xnp_w = xnp_bb[2] - xnp_bb[0]
    xnp_h = xnp_bb[3] - xnp_bb[1]
    xpp_w = xpp_bb[2] - xpp_bb[0]
    xpp_h = xpp_bb[3] - xpp_bb[1]
    rstp_w = rstp_bb[2] - rstp_bb[0]
    rstp_h = rstp_bb[3] - rstp_bb[1]

    # --- Row 0 (bottom): tail NFET centered at x=0 ---
    tail_x = 0.0
    tail_y = 0.0

    # --- Row 1: input pair + cross-coupled NMOS ---
    # inp to the left of center, inn to the right (mirrored)
    # xnp on the far left, xnn on the far right
    row1_y = tail_y + tail_h / 2 + row_gap + inp_h / 2

    # Input pair: inp at x < 0, inn at x > 0, mirrored about x=0
    # Leave a small gap at center between inp and inn
    inp_gap = 0.50  # gap between the two input devices at center (MCON spacing)
    inp_x = -(inp_w / 2 + inp_gap / 2)
    inn_x = (inp_w / 2 + inp_gap / 2)

    # Cross-coupled NMOS flank the input pair
    xnp_x = inp_x - inp_w / 2 - col_gap - xnp_w / 2
    xnn_x = inn_x + inp_w / 2 + col_gap + xnp_w / 2

    # --- Row 2 (top): PFET cross-coupled + reset ---
    row2_y = row1_y + max(inp_h, xnp_h) / 2 + row_gap + xpp_h / 2

    # xpp to the left, xpn to the right (mirrored)
    xpp_gap = 0.50
    xpp_x = -(xpp_w / 2 + xpp_gap / 2)
    xpn_x = (xpp_w / 2 + xpp_gap / 2)

    # Reset PFET flanking cross-coupled PMOS
    rstp_x = xpp_x - xpp_w / 2 - col_gap - rstp_w / 2
    rstn_x = xpn_x + xpp_w / 2 + col_gap + rstp_w / 2

    # ------------------------------------------------------------------
    # 3. Place instances
    # ------------------------------------------------------------------
    i_tail = Instance(tail_cell, tail_p, "tail").place(tail_x, tail_y)
    i_inp = Instance(inp_cell, inp_p, "inp").place(inp_x, row1_y)
    i_inn = Instance(inn_cell, inn_p, "inn").place(inn_x, row1_y)
    i_xnp = Instance(xnp_cell, xnp_p, "xnp").place(xnp_x, row1_y)
    i_xnn = Instance(xnn_cell, xnn_p, "xnn").place(xnn_x, row1_y)
    i_xpp = Instance(xpp_cell, xpp_p, "xpp").place(xpp_x, row2_y)
    i_xpn = Instance(xpn_cell, xpn_p, "xpn").place(xpn_x, row2_y)
    i_rstp = Instance(rstp_cell, rstp_p, "rstp").place(rstp_x, row2_y)
    i_rstn = Instance(rstn_cell, rstn_p, "rstn").place(rstn_x, row2_y)

    for inst in [i_tail, i_inp, i_inn, i_xnp, i_xnn,
                 i_xpp, i_xpn, i_rstp, i_rstn]:
        inst.add_to(top)

    # ------------------------------------------------------------------
    # 4. Routing
    # ------------------------------------------------------------------
    # Wire widths
    W_SIG = 0.42        # signal wires (MET1/MET2) — wider to avoid met1.2 spacing
    W_VIA = 0.40        # via landing pad width (VIA_SZ + 2*encl + margin)
    W_PWR = 0.50        # power rails
    W_CLK = 0.28        # clock bus

    # Helper to get port center coordinates
    def pc(inst, pname):
        """Get (x, y) center of a port on an instance."""
        return inst.port(pname).center

    # --- (a) tail.D -> inp.S, inn.S ---
    # The tail drain connects to both input pair sources (tail node).
    # Route on MET2 to avoid MET1 congestion with device internal pads.
    tail_d = pc(i_tail, "D")
    inp_s = pc(i_inp, "S")
    inn_s = pc(i_inn, "S")

    # Via up from tail.D, inp.S, inn.S to MET2
    via_stack(top, tail_d, L.MET1, L.MET2, width=W_VIA)
    via_stack(top, inp_s, L.MET1, L.MET2, width=W_VIA)
    via_stack(top, inn_s, L.MET1, L.MET2, width=W_VIA)

    # Vertical MET2 from tail.D up to the input pair source level
    route_straight(top, tail_d, (tail_d[0], inp_s[1]),
                   width=W_SIG, layer=L.MET2)
    # Horizontal MET2 bus connecting inp.S and inn.S through the center
    route_straight(top, inp_s, inn_s, width=W_SIG, layer=L.MET2)

    # --- (b) inp.D -> xnp.S (drn_p node) — route on MET2 to avoid MET1 congestion ---
    inp_d = pc(i_inp, "D")
    xnp_s = pc(i_xnp, "S")
    via_stack(top, inp_d, L.MET1, L.MET2, width=W_VIA)
    via_stack(top, xnp_s, L.MET1, L.MET2, width=W_VIA)
    route_L(top, inp_d, xnp_s, width=W_SIG, h_first=True, layer=L.MET2)

    # --- (c) inn.D -> xnn.S (drn_n node) — route on MET2 to avoid MET1 congestion ---
    inn_d = pc(i_inn, "D")
    xnn_s = pc(i_xnn, "S")
    via_stack(top, inn_d, L.MET1, L.MET2, width=W_VIA)
    via_stack(top, xnn_s, L.MET1, L.MET2, width=W_VIA)
    route_L(top, inn_d, xnn_s, width=W_SIG, h_first=True, layer=L.MET2)

    # --- (d) xnp.D -> xpp.D (outp node) — route on MET2, h_first to avoid
    #     MET2 spacing violations with cross-coupling vertical routes ---
    xnp_d = pc(i_xnp, "D")
    xpp_d = pc(i_xpp, "D")
    via_stack(top, xnp_d, L.MET1, L.MET2, width=W_VIA)
    via_stack(top, xpp_d, L.MET1, L.MET2, width=W_VIA)
    route_L(top, xnp_d, xpp_d, width=W_VIA, h_first=True, layer=L.MET2)

    # --- (e) xnn.D -> xpn.D (outn node) — route on MET2, h_first ---
    xnn_d = pc(i_xnn, "D")
    xpn_d = pc(i_xpn, "D")
    via_stack(top, xnn_d, L.MET1, L.MET2, width=W_VIA)
    via_stack(top, xpn_d, L.MET1, L.MET2, width=W_VIA)
    route_L(top, xnn_d, xpn_d, width=W_VIA, h_first=True, layer=L.MET2)

    # --- (f) rstp.D -> outp (xpp.D) — route on MET2 ---
    rstp_d = pc(i_rstp, "D")
    via_stack(top, rstp_d, L.MET1, L.MET2, width=W_VIA)
    route_L(top, rstp_d, xpp_d, width=W_VIA, h_first=True, layer=L.MET2)

    # --- (g) rstn.D -> outn (xpn.D) — route on MET2 ---
    rstn_d = pc(i_rstn, "D")
    via_stack(top, rstn_d, L.MET1, L.MET2, width=W_VIA)
    route_L(top, rstn_d, xpn_d, width=W_VIA, h_first=True, layer=L.MET2)

    # --- (h) Cross-coupling on MET2 (symmetric) ---
    # outp -> xnn.G and xpn.G  (outp drives the "n" side gates)
    # outn -> xnp.G and xpp.G  (outn drives the "p" side gates)

    # outp net at xpp.D, needs to reach xnn.G (right side) and xpn.G (right side)
    outp_pt = xpp_d    # MET1 anchor for outp
    xnn_g = pc(i_xnn, "G")
    xpn_g = pc(i_xpn, "G")

    # outn net at xpn.D, needs to reach xnp.G (left side) and xpp.G (left side)
    outn_pt = xpn_d    # MET1 anchor for outn
    xnp_g = pc(i_xnp, "G")
    xpp_g = pc(i_xpp, "G")

    # Cross-coupling uses MET2 to avoid MET1 conflicts.
    # Route: outp(MET1) -> via to MET2 -> horizontal MET2 -> via down to xnn.G(MET1)
    #        and continue to xpn.G(MET1)

    # MET2 horizontal bus Y-coordinates: use midpoints between rows
    m2_y_lower = (row1_y + row2_y) / 2 - 1.8   # outp cross-coupling bus
    m2_y_upper = (row1_y + row2_y) / 2 + 1.8   # outn cross-coupling bus

    # -- outp -> xnn.G, xpn.G (on MET2 at m2_y_lower) --
    via_stack(top, outp_pt, L.MET1, L.MET2, width=W_VIA)
    # Vertical MET2 jog from outp_pt down to bus level
    route_straight(top, outp_pt, (outp_pt[0], m2_y_lower),
                   width=W_VIA, layer=L.MET2)
    # Horizontal MET2 from outp_pt.x to xnn.G.x at bus level
    route_straight(top, (outp_pt[0], m2_y_lower), (xnn_g[0], m2_y_lower),
                   width=W_VIA, layer=L.MET2)
    # Via down to MET1 at xnn.G x
    via_stack(top, (xnn_g[0], m2_y_lower), L.MET1, L.MET2, width=W_VIA)
    route_straight(top, (xnn_g[0], m2_y_lower), xnn_g,
                   width=W_VIA, layer=L.MET1)
    # Also route MET2 to xpn.G x and via down
    route_straight(top, (xpn_g[0], m2_y_lower), (xnn_g[0], m2_y_lower),
                   width=W_VIA, layer=L.MET2)
    via_stack(top, (xpn_g[0], m2_y_lower), L.MET1, L.MET2, width=W_VIA)
    route_straight(top, (xpn_g[0], m2_y_lower), xpn_g,
                   width=W_VIA, layer=L.MET1)

    # -- outn -> xnp.G, xpp.G (on MET2 at m2_y_upper) --
    via_stack(top, outn_pt, L.MET1, L.MET2, width=W_VIA)
    route_straight(top, outn_pt, (outn_pt[0], m2_y_upper),
                   width=W_VIA, layer=L.MET2)
    route_straight(top, (outn_pt[0], m2_y_upper), (xnp_g[0], m2_y_upper),
                   width=W_VIA, layer=L.MET2)
    via_stack(top, (xnp_g[0], m2_y_upper), L.MET1, L.MET2, width=W_VIA)
    route_straight(top, (xnp_g[0], m2_y_upper), xnp_g,
                   width=W_VIA, layer=L.MET1)
    # Also to xpp.G
    route_straight(top, (xpp_g[0], m2_y_upper), (xnp_g[0], m2_y_upper),
                   width=W_VIA, layer=L.MET2)
    via_stack(top, (xpp_g[0], m2_y_upper), L.MET1, L.MET2, width=W_VIA)
    route_straight(top, (xpp_g[0], m2_y_upper), xpp_g,
                   width=W_VIA, layer=L.MET1)

    # --- (i) CLK bus on MET2 ---
    # Connect tail.G, rstp.G, rstn.G via a horizontal MET2 bus
    tail_g = pc(i_tail, "G")
    rstp_g = pc(i_rstp, "G")
    rstn_g = pc(i_rstn, "G")

    # CLK bus runs at the bottom, below the tail device
    clk_y = tail_y - tail_h / 2 - 0.8

    # tail.G -> via to MET2 -> vertical to bus
    via_stack(top, tail_g, L.MET1, L.MET2, width=max(W_CLK, W_VIA))
    route_straight(top, tail_g, (tail_g[0], clk_y),
                   width=W_CLK, layer=L.MET2)

    # rstp.G -> via to MET2 -> vertical to bus
    via_stack(top, rstp_g, L.MET1, L.MET2, width=max(W_CLK, W_VIA))
    route_straight(top, rstp_g, (rstp_g[0], clk_y),
                   width=W_CLK, layer=L.MET2)

    # rstn.G -> via to MET2 -> vertical to bus
    via_stack(top, rstn_g, L.MET1, L.MET2, width=max(W_CLK, W_VIA))
    route_straight(top, rstn_g, (rstn_g[0], clk_y),
                   width=W_CLK, layer=L.MET2)

    # Horizontal MET2 bus connecting all three CLK taps
    route_straight(top, (rstp_g[0], clk_y), (rstn_g[0], clk_y),
                   width=W_CLK, layer=L.MET2)

    # --- (j) VSS rail (MET1, bottom) ---
    # Horizontal MET1 rail below everything
    all_instances = [i_tail, i_inp, i_inn, i_xnp, i_xnn,
                     i_xpp, i_xpn, i_rstp, i_rstn]
    x_min = min(inst.bbox()[0][0] for inst in all_instances) - 1.0
    x_max = max(inst.bbox()[1][0] for inst in all_instances) + 1.0

    vss_y = clk_y - 0.8
    top.add(gdstk.rectangle(
        (x_min, vss_y - W_PWR / 2),
        (x_max, vss_y + W_PWR / 2),
        **ld(L.MET1),
    ))

    # Connect tail.S to VSS rail — route on MET2 to avoid MET1 overlap
    # with the P+ guard ring bottom segment, whose MET1 occupies x~0.
    # Via up to MET2 at tail.S, jog horizontally to an offset x, then
    # via back down to MET1 and connect to the VSS rail.
    tail_s = pc(i_tail, "S")
    tail_s_offset_x = tail_s[0] - 1.5   # shift left to clear guard ring MET1
    via_stack(top, tail_s, L.MET1, L.MET2, width=W_VIA)
    route_straight(top, tail_s, (tail_s_offset_x, tail_s[1]),
                   width=W_SIG, layer=L.MET2)
    route_straight(top, (tail_s_offset_x, tail_s[1]),
                   (tail_s_offset_x, vss_y),
                   width=W_SIG, layer=L.MET2)
    via_stack(top, (tail_s_offset_x, vss_y), L.MET1, L.MET2, width=W_VIA)
    # Short MET1 stub to ensure contact with the VSS rail at the offset x
    route_straight(top, (tail_s_offset_x, vss_y - W_PWR / 2),
                   (tail_s_offset_x, vss_y + W_PWR / 2),
                   width=W_SIG, layer=L.MET1)

    # NMOS bodies connect to VSS through the guard ring (section 5).

    # --- (k) VDD rail (MET1, top) ---
    vdd_y = row2_y + xpp_h / 2 + 1.5
    top.add(gdstk.rectangle(
        (x_min, vdd_y - W_PWR / 2),
        (x_max, vdd_y + W_PWR / 2),
        **ld(L.MET1),
    ))

    # Connect PMOS sources to VDD
    for inst in [i_xpp, i_xpn, i_rstp, i_rstn]:
        s_pt = pc(inst, "S")
        route_straight(top, s_pt, (s_pt[0], vdd_y),
                       width=W_SIG, layer=L.MET1)

    # ------------------------------------------------------------------
    # 5. Guard rings
    # ------------------------------------------------------------------
    # Compute bounding boxes for NFET and PFET regions
    nfet_insts = [i_tail, i_inp, i_inn, i_xnp, i_xnn]
    pfet_insts = [i_xpp, i_xpn, i_rstp, i_rstn]

    # Guard ring margins: enough clearance for N-well spacing (nwell.2a)
    # and NDIFF-to-NWELL spacing (diff/tap.9 = 0.34)
    gr_margin = 1.0

    n_x0 = min(inst.bbox()[0][0] for inst in nfet_insts) - gr_margin
    n_y0 = min(inst.bbox()[0][1] for inst in nfet_insts) - gr_margin
    n_x1 = max(inst.bbox()[1][0] for inst in nfet_insts) + gr_margin
    n_y1 = max(inst.bbox()[1][1] for inst in nfet_insts) + gr_margin

    # Continuous N-well blanket over all PFET devices — merges individual
    # device N-wells AND overlaps with the guard ring N-well to eliminate
    # all nwell.2a spacing violations. Must extend past the guard ring's
    # N-well inner edge at ~(pfet_bbox + pfet_gr_margin + 0.125 - 0.18).
    pfet_nw_margin = 1.5
    pfet_nw_x0 = min(inst.bbox()[0][0] for inst in pfet_insts) - pfet_nw_margin
    pfet_nw_y0 = min(inst.bbox()[0][1] for inst in pfet_insts) - pfet_nw_margin
    pfet_nw_x1 = max(inst.bbox()[1][0] for inst in pfet_insts) + pfet_nw_margin
    pfet_nw_y1 = max(inst.bbox()[1][1] for inst in pfet_insts) + pfet_nw_margin
    top.add(gdstk.rectangle(
        (pfet_nw_x0, pfet_nw_y0),
        (pfet_nw_x1, pfet_nw_y1),
        **ld(L.NWELL),
    ))

    # Guard ring cells are centered at origin with inner opening = (inner_w, inner_h)
    n_inner_w = n_x1 - n_x0
    n_inner_h = n_y1 - n_y0
    n_center_x = (n_x0 + n_x1) / 2
    n_center_y = (n_y0 + n_y1) / 2

    vss_ring_cell, vss_ring_ports = guard_ring_p(lib, "gring_nfet",
                                                 n_inner_w, n_inner_h,
                                                 ring_w=1.2)

    i_vss_ring = Instance(vss_ring_cell, vss_ring_ports, "gring_nfet")
    i_vss_ring.place(n_center_x, n_center_y).add_to(top)

    # N+ well ring removed: its MET1 bottom arm crossed the NFET-to-PFET
    # S/D straps, shorting signals to VDD through MET1 overlap.

    # Connect P+ guard ring MET1 segments to VSS rail
    for pkey, rp in i_vss_ring.ports.items():
        rx, ry = rp.center
        if "bot" in pkey:
            route_straight(top, (rx, ry), (rx, vss_y),
                           width=W_SIG, layer=L.MET1)

    # ------------------------------------------------------------------
    # 6. Define top-level ports
    # ------------------------------------------------------------------
    # VINP: input pair gate (left side, inp)
    vinp_g = pc(i_inp, "G")
    # VINN: input pair gate (right side, inn)
    vinn_g = pc(i_inn, "G")

    # OUTP: at xpp.D / xnp.D junction
    outp_x, outp_y = xpp_d
    # OUTN: at xpn.D / xnn.D junction
    outn_x, outn_y = xpn_d

    # CLK: on the MET2 bus
    clk_port_x = 0.0

    ports = {
        "VINP": Port("VINP", vinp_g, W_SIG, 90, L.MET1),
        "VINN": Port("VINN", vinn_g, W_SIG, 90, L.MET1),
        "OUTP": Port("OUTP", (outp_x, outp_y), W_SIG, 90, L.MET1),
        "OUTN": Port("OUTN", (outn_x, outn_y), W_SIG, 90, L.MET1),
        "CLK":  Port("CLK", (clk_port_x, clk_y), W_CLK, 0, L.MET2),
        "VDD":  Port("VDD", (0.0, vdd_y), W_PWR, 0, L.MET1),
        "VSS":  Port("VSS", (0.0, vss_y), W_PWR, 0, L.MET1),
    }

    # Add pin labels for all ports
    for p in ports.values():
        add_port_label(top, p)

    return top, ports


# ============================================================================
# Standalone execution
# ============================================================================

if __name__ == "__main__":
    lib = gdstk.Library("strongarm")
    cell, ports = strongarm_layout(lib)

    # Compute bounding box for reporting
    bb = cell.bounding_box()
    if bb is not None:
        w = bb[1][0] - bb[0][0]
        h = bb[1][1] - bb[0][1]
        print(f"Cell: {cell.name}")
        print(f"Bounding box: ({bb[0][0]:.2f}, {bb[0][1]:.2f}) to "
              f"({bb[1][0]:.2f}, {bb[1][1]:.2f})")
        print(f"Size: {w:.2f} x {h:.2f} um")
    else:
        print(f"Cell: {cell.name} (empty)")

    print(f"\nPorts ({len(ports)}):")
    for name, port in ports.items():
        x, y = port.center
        print(f"  {name:6s}  ({x:+7.3f}, {y:+7.3f})  w={port.width:.2f}  "
              f"layer={port.layer}  orient={port.orientation}")

    # Write GDS
    out_dir = os.path.join(os.path.dirname(__file__), "..", "..")
    gds_path = os.path.join(out_dir, "strongarm.gds")
    lib.write_gds(gds_path)
    print(f"\nGDS: {os.path.abspath(gds_path)}")

    # Write SVG (for quick visual check)
    svg_path = os.path.join(out_dir, "strongarm.svg")
    # gdstk SVG export — one cell at a time
    cell.write_svg(svg_path, background="none", pad=2)
    print(f"SVG: {os.path.abspath(svg_path)}")
