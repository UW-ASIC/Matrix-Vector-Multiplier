"""Interleaved 2-unit async SAR ADC layout — gdstk cell generation.

Architecture:
    Unit 0 (left) handles col0 + col1, Unit 1 (right, mirrored) handles col2.
    Each unit: MUX -> COMPARATOR -> CDAC -> SAR LOGIC (top to bottom).
    Units are mirrored about the center vertical axis for symmetry.

Target footprint: ~85um x 80um (3-column variant).
"""

import gdstk

from project.layout.layers import L, ld
from project.layout.drc import DRC
from project.layout.ports import Port, add_port_label
from project.layout.primitives.mosfet import nfet, pfet
from project.layout.primitives.capacitor import mim_cap
from project.layout.primitives.contact import via_stack
from project.layout.primitives.guard_ring import guard_ring_p
from project.layout.compose import Instance, abut_x, stack_y
from project.layout.routing.router import route_straight, route_L, add_shield

# ---------------------------------------------------------------------------
# Constants (microns unless noted)
# ---------------------------------------------------------------------------

N_BITS = 4
C_UNIT_SIDE = 5.0          # 5um x 5um -> ~50fF MIM unit cap
MIM_CAP_PER_UM2 = 2.0      # fF/um^2 (Sky130 MIM)

# StrongARM comparator sizing (W in um, L in um, nf)
TAIL_W, TAIL_L, TAIL_NF = 0.42, 0.15, 1
INP_W, INP_L, INP_NF = 7.0, 0.15, 8
LATCH_N_W, LATCH_N_L, LATCH_N_NF = 1.0, 0.15, 2
LATCH_P_W, LATCH_P_L, LATCH_P_NF = 4.5, 0.15, 6
RST_W, RST_L, RST_NF = 1.0, 0.15, 2

# CDAC switch/inverter sizing
CDAC_INV_N_W, CDAC_INV_N_L = 0.42, 0.15
CDAC_INV_P_W, CDAC_INV_P_L = 0.84, 0.15
CDAC_SW_N_W, CDAC_SW_N_L = 0.42, 0.15
CDAC_SW_P_W, CDAC_SW_P_L = 1.42, 0.15

# Input mux sizing
MUX_N_W, MUX_N_L = 0.42, 0.15
MUX_P_W, MUX_P_L = 1.42, 0.15

# SAR logic buffer sizing (min-size inverters)
BUF_N_W, BUF_N_L = 0.42, 0.15
BUF_P_W, BUF_P_L = 0.84, 0.15

# Spacing
COMP_TO_CDAC_GAP = 4.0     # Critical path: comparator to CDAC < 5um
MUX_TO_COMP_GAP = 3.0
CDAC_TO_SAR_GAP = 6.0      # Analog-digital separation (increased for met1.2/diff)
BIT_SPACING = 4.0           # Between CDAC bit slices (>= 4um for met1.2 / li.3)
UNIT_MIRROR_GAP = 6.0       # Center gap between mirrored units
GUARD_RING_W = 1.5          # Guard ring width
POWER_STRAP_W = 1.6         # MET5 min width
VREF_BUS_W = 2.0            # Wide MET4 VREF bus


# ---------------------------------------------------------------------------
# Helper: CMOS inverter sub-cell
# ---------------------------------------------------------------------------

def _inverter(lib, name, wn, ln, wp, lp):
    """Build a CMOS inverter cell. Returns (cell, ports).

    Ports: A (input), Y (output), VDD, VSS
    """
    cell = lib.new_cell(name)
    ports = {}

    # NFET at origin
    n_cell, n_ports = nfet(lib, wn, ln, 1, f"{name}_n")
    n_inst = Instance(n_cell, n_ports, f"{name}_ni")
    n_inst.place(0, 0)
    n_inst.add_to(cell)

    # PFET above NFET — gap must satisfy NWELL-to-NDIFF spacing (diff/tap.9)
    p_cell, p_ports = pfet(lib, wp, lp, 1, f"{name}_p")
    p_inst = Instance(p_cell, p_ports, f"{name}_pi")
    # NFET diff top = wn/(2*1) = half_wf_n
    # PFET NWELL bottom (relative to PFET origin) =
    #   -(wp/(2*1)) - max(NWELL_ENCL_DIFF, NDIFF_SP_NWELL) - POLY_EXT_DIFF_PMOS
    # Need: p_y + pfet_nwell_bottom - nfet_diff_top >= NDIFF_SP_NWELL
    half_wfn = wn / 2
    half_wfp = wp / 2
    nw_enc = max(DRC.NWELL_ENCL_DIFF, DRC.NDIFF_SP_NWELL)
    pfet_nwell_bot = -(half_wfp + nw_enc + DRC.POLY_EXT_DIFF_PMOS)
    nfet_diff_top = half_wfn
    p_y = nfet_diff_top + DRC.NDIFF_SP_NWELL - pfet_nwell_bot + 1.0
    # Also ensure p_y clears the NFET bounding box top
    p_y = max(p_y, n_inst.bbox()[1][1] + 1.3)
    p_inst.place(0, p_y)
    p_inst.add_to(cell)

    # Gate input — draw MET1 wire spanning from below NFET G pad to above
    # PFET G pad.  This guarantees overlap with both gate contact MET1 pads,
    # eliminating the tiny gap that route_straight (port-center to port-center)
    # would leave between the pad edge and wire endpoint.
    g_n = n_inst.port("G")
    g_p = p_inst.port("G")
    gate_x = g_n.center[0]
    gate_y = (g_n.center[1] + g_p.center[1]) / 2
    # Compute pad half-height (same formula as mosfet.py)
    _m1_gc = DRC.MCON_SZ + 2 * DRC.MCON_ENCL_MET1
    _m1_gc_h = _m1_gc if _m1_gc * _m1_gc >= 0.083 else 0.083 / _m1_gc + 0.01
    gate_wire_bot = g_n.center[1] - _m1_gc_h / 2
    gate_wire_top = g_p.center[1] + _m1_gc_h / 2
    hw_g = DRC.MET1_W / 2
    cell.add(gdstk.rectangle(
        (gate_x - hw_g, gate_wire_bot),
        (gate_x + hw_g, gate_wire_top),
        **ld(L.MET1),
    ))
    ports["A"] = Port("A", (gate_x, gate_y), DRC.MET1_W, 180, L.MET1)

    # Drain output — draw MET1 wire from NFET S/D pad region to PFET S/D
    # pad region.  The S/D MET1 pads are centered at y=0 in device-local
    # coords (i.e. at the Instance origin y).  We span the wire from below
    # the NFET pad bottom to above the PFET pad top so it overlaps both.
    d_n = n_inst.port("D")
    d_p = p_inst.port("D")
    out_x = d_n.center[0]
    out_y = (d_n.center[1] + d_p.center[1]) / 2
    # S/D pad half-height
    _m1_sd = DRC.MCON_SZ + 2 * DRC.MCON_ENCL_MET1
    _m1_sd_h = _m1_sd if _m1_sd * _m1_sd >= 0.083 else 0.083 / _m1_sd + 0.01
    drain_wire_bot = 0.0 - _m1_sd_h / 2      # NFET pad bottom (NFET at y=0)
    drain_wire_top = p_y + _m1_sd_h / 2      # PFET pad top (PFET at y=p_y)
    hw_d = DRC.MET1_W / 2
    cell.add(gdstk.rectangle(
        (out_x - hw_d, drain_wire_bot),
        (out_x + hw_d, drain_wire_top),
        **ld(L.MET1),
    ))
    ports["Y"] = Port("Y", (out_x, out_y), DRC.MET1_W, 0, L.MET1)

    # Power
    ports["VDD"] = p_inst.port("S")
    ports["VSS"] = n_inst.port("S")

    return cell, ports


# ---------------------------------------------------------------------------
# Helper: CMOS transmission gate (mux switch)
# ---------------------------------------------------------------------------

def _cmos_tgate(lib, name, wn, ln, wp, lp):
    """Build a CMOS transmission gate. Returns (cell, ports).

    Ports: IN, OUT, EN, ENB, VDD, VSS (bulk ties)
    """
    cell = lib.new_cell(name)
    ports = {}

    n_cell, n_ports = nfet(lib, wn, ln, 1, f"{name}_n")
    n_inst = Instance(n_cell, n_ports, f"{name}_ni")
    n_inst.place(0, 0)
    n_inst.add_to(cell)

    # PFET above NFET — gap must satisfy NWELL-to-NDIFF spacing (diff/tap.9)
    p_cell, p_ports = pfet(lib, wp, lp, 1, f"{name}_p")
    p_inst = Instance(p_cell, p_ports, f"{name}_pi")
    half_wfn = wn / 2
    half_wfp = wp / 2
    nw_enc = max(DRC.NWELL_ENCL_DIFF, DRC.NDIFF_SP_NWELL)
    pfet_nwell_bot = -(half_wfp + nw_enc + DRC.POLY_EXT_DIFF_PMOS)
    nfet_diff_top = half_wfn
    p_y = nfet_diff_top + DRC.NDIFF_SP_NWELL - pfet_nwell_bot + 1.0
    p_y = max(p_y, n_inst.bbox()[1][1] + 1.3)
    p_inst.place(0, p_y)
    p_inst.add_to(cell)

    # S terminals = IN (tied together) — draw MET1 wire spanning from NFET
    # S/D pad bottom to PFET S/D pad top to eliminate pad-to-wire gap.
    s_n = n_inst.port("S")
    s_p = p_inst.port("S")
    in_x = s_n.center[0]
    in_y = (s_n.center[1] + s_p.center[1]) / 2
    _m1_sd = DRC.MCON_SZ + 2 * DRC.MCON_ENCL_MET1
    _m1_sd_h = _m1_sd if _m1_sd * _m1_sd >= 0.083 else 0.083 / _m1_sd + 0.01
    hw_s = DRC.MET1_W / 2
    cell.add(gdstk.rectangle(
        (in_x - hw_s, 0.0 - _m1_sd_h / 2),
        (in_x + hw_s, p_y + _m1_sd_h / 2),
        **ld(L.MET1),
    ))
    ports["IN"] = Port("IN", (in_x, in_y), DRC.MET1_W, 180, L.MET1)

    # D terminals = OUT (tied together) — same approach for drain wire
    d_n = n_inst.port("D")
    d_p = p_inst.port("D")
    out_x = d_n.center[0]
    out_y = (d_n.center[1] + d_p.center[1]) / 2
    hw_d = DRC.MET1_W / 2
    cell.add(gdstk.rectangle(
        (out_x - hw_d, 0.0 - _m1_sd_h / 2),
        (out_x + hw_d, p_y + _m1_sd_h / 2),
        **ld(L.MET1),
    ))
    ports["OUT"] = Port("OUT", (out_x, out_y), DRC.MET1_W, 0, L.MET1)

    # Gates
    ports["EN"] = n_inst.port("G")      # NFET gate = EN
    ports["ENB"] = p_inst.port("G")     # PFET gate = ENB (active low)

    # Bulk ties (at source side — no separate B port on primitives)
    ports["VSS"] = Port("VSS", n_inst.port("S").center, 0.17, 270, L.MET1)
    ports["VDD"] = Port("VDD", p_inst.port("S").center, 0.17, 90, L.MET1)

    return cell, ports


# ---------------------------------------------------------------------------
# StrongARM comparator (9T)
# ---------------------------------------------------------------------------

def _strongarm(lib, name):
    """Build a 9T StrongARM latch comparator. Returns (cell, ports).

    Topology (bottom to top):
        tail NMOS (clocked) -> diff pair (inp/inn) -> cross-coupled NMOS latch
        -> cross-coupled PMOS latch -> reset PMOS pair

    Ports: VINP, VINN, OUTP, OUTN, CLK, VDD, VSS
    """
    cell = lib.new_cell(name)
    ports = {}

    y_cursor = 0.0

    # --- Tail current source ---
    tail_cell, tail_ports = nfet(lib, TAIL_W, TAIL_L, TAIL_NF, f"{name}_tail")
    tail_inst = Instance(tail_cell, tail_ports)
    tail_inst.place(0, y_cursor)
    tail_inst.add_to(cell)
    y_cursor = tail_inst.bbox()[1][1] + 2.5

    # --- Input differential pair (symmetric about x=0) ---
    inp_cell, inp_ports = nfet(lib, INP_W, INP_L, INP_NF, f"{name}_inp")
    inn_cell, inn_ports = nfet(lib, INP_W, INP_L, INP_NF, f"{name}_inn")

    inp_inst = Instance(inp_cell, inp_ports)
    inn_inst = Instance(inn_cell, inn_ports)

    # Place symmetrically: inp to the left, inn to the right
    pair_spread = 10.0  # center-to-center horizontal distance (increased for nwell.2a/poly spacing)
    inp_inst.place(-pair_spread / 2, y_cursor)
    inn_inst.place(pair_spread / 2, y_cursor)
    inp_inst.add_to(cell)
    inn_inst.add_to(cell)

    # Connect tail.D -> inp.S, inn.S (via MET1 bus)
    route_L(cell, tail_inst.port("D"), inp_inst.port("S"))
    route_L(cell, tail_inst.port("D"), inn_inst.port("S"))

    y_cursor = max(inp_inst.bbox()[1][1], inn_inst.bbox()[1][1]) + 2.5

    # --- Cross-coupled NMOS latch ---
    xnp_cell, xnp_ports = nfet(lib, LATCH_N_W, LATCH_N_L, LATCH_N_NF, f"{name}_xnp")
    xnn_cell, xnn_ports = nfet(lib, LATCH_N_W, LATCH_N_L, LATCH_N_NF, f"{name}_xnn")

    xnp_inst = Instance(xnp_cell, xnp_ports)
    xnn_inst = Instance(xnn_cell, xnn_ports)
    latch_spread = 8.0  # increased for nwell.2a / poly / LI spacing
    xnp_inst.place(-latch_spread / 2, y_cursor)
    xnn_inst.place(latch_spread / 2, y_cursor)
    xnp_inst.add_to(cell)
    xnn_inst.add_to(cell)

    # inp.D -> xnp.S, inn.D -> xnn.S
    # Use route_L since these ports are at different x positions (pair_spread
    # vs latch_spread). MET2 avoids congestion with vertical MET1 routes.
    route_L(cell, inp_inst.port("D"), xnp_inst.port("S"),
            width=DRC.MET1_W, layer=L.MET2)
    route_L(cell, inn_inst.port("D"), xnn_inst.port("S"),
            width=DRC.MET1_W, layer=L.MET2)

    y_cursor = max(xnp_inst.bbox()[1][1], xnn_inst.bbox()[1][1]) + 2.5

    # --- Cross-coupled PMOS latch ---
    xpp_cell, xpp_ports = pfet(lib, LATCH_P_W, LATCH_P_L, LATCH_P_NF, f"{name}_xpp")
    xpn_cell, xpn_ports = pfet(lib, LATCH_P_W, LATCH_P_L, LATCH_P_NF, f"{name}_xpn")

    xpp_inst = Instance(xpp_cell, xpp_ports)
    xpn_inst = Instance(xpn_cell, xpn_ports)
    xpp_inst.place(-latch_spread / 2, y_cursor)
    xpn_inst.place(latch_spread / 2, y_cursor)
    xpp_inst.add_to(cell)
    xpn_inst.add_to(cell)

    # Cross-coupling wires: xnp.D + xpp.D = OUTP, xnn.D + xpn.D = OUTN
    # Draw explicit MET1 rectangles from one device pad center to the other,
    # ensuring overlap with both S/D MET1 pads (no port-to-pad gap).
    for inst_bot, inst_top in [(xnp_inst, xpp_inst), (xnn_inst, xpn_inst)]:
        dx = inst_bot.port("D").center[0]
        # Wire from bottom device pad center (inst_bot y-origin) to
        # top device pad center (inst_top y-origin).
        y_bot = inst_bot.bbox()[0][1]   # cover full bottom device
        y_top = inst_top.bbox()[1][1]   # cover full top device
        hw = DRC.MET1_W / 2
        cell.add(gdstk.rectangle(
            (dx - hw, y_bot),
            (dx + hw, y_top),
            **ld(L.MET1),
        ))

    # Cross-couple gates: xnp.G + xpp.G = OUTN net, xnn.G + xpn.G = OUTP net
    # Route on MET2 to avoid parallel MET1 wires violating met1.2 spacing
    # with adjacent drain-to-drain vertical routes.
    route_L(cell, xnn_inst.port("D"), xnp_inst.port("G"),
            width=DRC.MET1_W, layer=L.MET2)
    route_L(cell, xnn_inst.port("D"), xpp_inst.port("G"),
            width=DRC.MET1_W, layer=L.MET2)
    route_L(cell, xnp_inst.port("D"), xnn_inst.port("G"),
            width=DRC.MET1_W, layer=L.MET2)
    route_L(cell, xnp_inst.port("D"), xpn_inst.port("G"),
            width=DRC.MET1_W, layer=L.MET2)

    y_cursor = max(xpp_inst.bbox()[1][1], xpn_inst.bbox()[1][1]) + 2.5

    # --- Reset PMOS pair ---
    rstp_cell, rstp_ports = pfet(lib, RST_W, RST_L, RST_NF, f"{name}_rstp")
    rstn_cell, rstn_ports = pfet(lib, RST_W, RST_L, RST_NF, f"{name}_rstn")

    rstp_inst = Instance(rstp_cell, rstp_ports)
    rstn_inst = Instance(rstn_cell, rstn_ports)
    rstp_inst.place(-latch_spread / 2, y_cursor)
    rstn_inst.place(latch_spread / 2, y_cursor)
    rstp_inst.add_to(cell)
    rstn_inst.add_to(cell)

    # rstp.D = OUTP, rstn.D = OUTN — explicit MET1 from device to device
    for inst_bot, inst_top in [(xpp_inst, rstp_inst), (xpn_inst, rstn_inst)]:
        dx = inst_bot.port("D").center[0]
        y_bot = inst_bot.bbox()[0][1]
        y_top = inst_top.bbox()[1][1]
        hw = DRC.MET1_W / 2
        cell.add(gdstk.rectangle(
            (dx - hw, y_bot),
            (dx + hw, y_top),
            **ld(L.MET1),
        ))

    # --- Export ports ---
    ports["VINP"] = Port("VINP", inp_inst.port("G").center, 0.14, 180, L.MET1)
    ports["VINN"] = Port("VINN", inn_inst.port("G").center, 0.14, 0, L.MET1)

    outp_center = xnp_inst.port("D").center
    outn_center = xnn_inst.port("D").center
    # Width must satisfy via enclosure: VIA_SZ + 2*max(VIA_ENCL_MET1, VIA_ENCL_MET2) = 0.26
    via_min_pad = DRC.VIA_SZ + 2 * max(DRC.VIA_ENCL_MET1, DRC.VIA_ENCL_MET2)
    ports["OUTP"] = Port("OUTP", outp_center, via_min_pad, 180, L.MET2)
    ports["OUTN"] = Port("OUTN", outn_center, via_min_pad, 0, L.MET2)

    # CLK = tail.G + rstp.G + rstn.G
    ports["CLK"] = Port("CLK", tail_inst.port("G").center, 0.14, 270, L.MET1)

    # VDD from reset PMOS sources, VSS from tail source
    vdd_y = (rstp_inst.port("S").center[1] + rstn_inst.port("S").center[1]) / 2
    ports["VDD"] = Port("VDD", (0, vdd_y), POWER_STRAP_W, 90, L.MET4)
    ports["VSS"] = Port("VSS", (0, tail_inst.port("S").center[1]), POWER_STRAP_W, 270, L.MET4)

    return cell, ports


# ---------------------------------------------------------------------------
# CDAC: 4-bit common-centroid MIM cap array + switches + inverters
# ---------------------------------------------------------------------------

def _cdac(lib, name):
    """Build a 4-bit charge-redistribution CDAC. Returns (cell, ports).

    Layout: 4x4 common-centroid MIM array with switch + inverter rows below.
    Binary-weighted: bit0=1C, bit1=2C, bit2=4C, bit3=8C (C=50fF).

    Ports: SW0-SW3 (switch control), TOP (CDAC top plate), VREF, VDD, VSS
    """
    cell = lib.new_cell(name)
    ports = {}

    # --- Common-centroid cap arrangement ---
    # 4x4 array, 15 unit caps total (1+2+4+8), plus 1 dummy = 16 slots
    # ABBA pattern for 4 bits:
    #   Row 3: D  B3 B3 B3
    #   Row 2: B3 B2 B2 B3
    #   Row 1: B3 B1 B0 B2
    #   Row 0: B3 B2 B1 B2
    # Where D=dummy, B0=bit0(1C), B1=bit1(2C), B2=bit2(4C), B3=bit3(8C)
    cc_map = [
        [3, 2, 1, 2],   # row 0
        [3, 1, 0, 2],   # row 1
        [3, 2, 2, 3],   # row 2
        [-1, 3, 3, 3],  # row 3 (-1 = dummy)
    ]

    # Pitch must satisfy CAPM spacing (0.84um) AND unrelated-MET3 spacing (1.34um).
    # MET3 bottom plate extends by CAPM_ENCL_MET3 each side, so gap between
    # adjacent MET3 bottom plates = cap_pitch - C_UNIT_SIDE - 2*CAPM_ENCL_MET3.
    # Need that gap >= CAPM_SP_UNREL_MET3 to avoid capm.2a violations.
    cap_pitch = C_UNIT_SIDE + max(DRC.CAPM_SP + 2 * DRC.CAPM_ENCL_MET3,
                                   DRC.CAPM_SP_UNREL_MET3)
    array_origin_x = 0.0
    array_origin_y = 0.0

    cap_instances = []
    for row in range(4):
        for col in range(4):
            cx = array_origin_x + col * cap_pitch
            cy = array_origin_y + row * cap_pitch
            bit_id = cc_map[row][col]
            suffix = f"r{row}c{col}"
            if bit_id < 0:
                cname = f"{name}_dummy_{suffix}"
            else:
                cname = f"{name}_b{bit_id}_{suffix}"

            cap_cell, cap_ports = mim_cap(
                lib, C_UNIT_SIDE, C_UNIT_SIDE, cname
            )
            cap_inst = Instance(cap_cell, cap_ports)
            cap_inst.place(cx, cy)
            cap_inst.add_to(cell)
            cap_instances.append((bit_id, cap_inst))

    # CDAC top plate: all cap top plates connected (MET4 bus across array)
    array_w = 4 * cap_pitch
    array_top_y = array_origin_y + 4 * cap_pitch
    top_plate_y = array_top_y + 0.5
    cell.add(gdstk.rectangle(
        (array_origin_x - 0.5, top_plate_y - VREF_BUS_W / 2),
        (array_origin_x + array_w + 0.5, top_plate_y + VREF_BUS_W / 2),
        **ld(L.MET4),
    ))
    ports["TOP"] = Port("TOP", (array_origin_x + array_w / 2, top_plate_y),
                         VREF_BUS_W, 90, L.MET4)

    # Connect each cap top plate to the MET4 bus via via stacks
    for bit_id, cap_inst in cap_instances:
        top_port = cap_inst.port("TOP")
        via_stack(cell, (top_port.center[0], top_plate_y),
                  L.MET3, L.MET4, width=0.5)
        route_straight(cell, top_port,
                       Port("_", (top_port.center[0], top_plate_y), 0.3, 90, L.MET3))

    # --- Switch + inverter rows below cap array ---
    sw_row_y = array_origin_y - 5.5   # switches below cap array (increased for diff/poly spacing)
    inv_row_y = sw_row_y - 6.5        # inverters below switches (increased for diff/poly spacing)

    for b in range(N_BITS):
        bx = array_origin_x + b * (array_w / N_BITS)

        # Switch (CMOS TG): connects VREF to cap bottom plates for this bit
        sw_cell, sw_ports = _cmos_tgate(
            lib, f"{name}_sw{b}", CDAC_SW_N_W, CDAC_SW_N_L,
            CDAC_SW_P_W, CDAC_SW_P_L
        )
        sw_inst = Instance(sw_cell, sw_ports)
        sw_inst.place(bx, sw_row_y)
        sw_inst.add_to(cell)

        # Inverter: generates complement control for PFET gate of TG
        inv_cell, inv_ports = _inverter(
            lib, f"{name}_inv{b}", CDAC_INV_N_W, CDAC_INV_N_L,
            CDAC_INV_P_W, CDAC_INV_P_L
        )
        inv_inst = Instance(inv_cell, inv_ports)
        inv_inst.place(bx, inv_row_y)
        inv_inst.add_to(cell)

        # Connect inverter output to TG ENB — route on MET2 to avoid
        # parallel MET1 wires between inverter and switch that violate met1.2.
        route_L(cell, inv_inst.port("Y"), sw_inst.port("ENB"),
                width=DRC.MET1_W, layer=L.MET2)

        # Bit control port (inverter input = TG EN)
        ports[f"SW{b}"] = Port(f"SW{b}", inv_inst.port("A").center,
                                0.14, 270, L.MET1)

    # VREF port: horizontal MET3 bus feeding all switch IN ports
    # Offset below switch row with adequate MET3 spacing from cap bottom plates
    vref_y = sw_row_y - 2.5
    vref_bus_half_w = max(0.3, DRC.MET3_W / 2)
    cell.add(gdstk.rectangle(
        (array_origin_x - 0.5, vref_y - vref_bus_half_w),
        (array_origin_x + array_w + 0.5, vref_y + vref_bus_half_w),
        **ld(L.MET3),
    ))
    ports["VREF"] = Port("VREF", (array_origin_x + array_w / 2, vref_y),
                          2 * vref_bus_half_w, 180, L.MET3)

    # Power ports at edges
    ports["VDD"] = Port("VDD", (array_origin_x + array_w / 2, inv_row_y + 3.5),
                         POWER_STRAP_W, 90, L.MET4)
    ports["VSS"] = Port("VSS", (array_origin_x + array_w / 2, inv_row_y - 0.5),
                         POWER_STRAP_W, 270, L.MET4)

    return cell, ports


# ---------------------------------------------------------------------------
# SAR logic placeholder (row of buffers for digital output)
# ---------------------------------------------------------------------------

def _sar_logic(lib, name, n_bits):
    """Build SAR logic placeholder as a row of output buffers. Returns (cell, ports).

    Per bit: 2 inverters (buffer) driving output.
    Ports: IN0-IN3, D0-D3, VDD, VSS
    """
    cell = lib.new_cell(name)
    ports = {}

    x_cursor = 0.0
    buf_pitch = 6.5  # spacing between buffer columns (increased for met1.2/poly.2/poly.4)

    for b in range(n_bits):
        bx = x_cursor + b * buf_pitch

        # First inverter (input stage)
        inv1_cell, inv1_ports = _inverter(
            lib, f"{name}_buf{b}_1", BUF_N_W, BUF_N_L, BUF_P_W, BUF_P_L
        )
        inv1_inst = Instance(inv1_cell, inv1_ports)
        inv1_inst.place(bx, 0)
        inv1_inst.add_to(cell)

        # Second inverter (output stage)
        inv2_cell, inv2_ports = _inverter(
            lib, f"{name}_buf{b}_2", BUF_N_W, BUF_N_L, BUF_P_W, BUF_P_L
        )
        inv2_inst = Instance(inv2_cell, inv2_ports)
        inv2_inst.place(bx + buf_pitch / 2, 0)
        inv2_inst.add_to(cell)

        # Wire inv1.Y -> inv2.A — use route_L (Manhattan L-shape) instead of
        # route_straight to avoid a non-Manhattan bounding-box rectangle that
        # would overlap adjacent MET1 features and cause met1.2 violations.
        route_L(cell, inv1_inst.port("Y"), inv2_inst.port("A"),
                width=DRC.MET1_W, layer=L.MET2)

        ports[f"IN{b}"] = Port(f"IN{b}", inv1_inst.port("A").center,
                                0.14, 90, L.MET1)
        ports[f"D{b}"] = Port(f"D{b}", inv2_inst.port("Y").center,
                               0.14, 270, L.MET1)

    # Power at row ends
    bb = cell.bounding_box()
    if bb is not None:
        mid_x = (bb[0][0] + bb[1][0]) / 2
        ports["VDD"] = Port("VDD", (mid_x, bb[1][1] + 0.3), POWER_STRAP_W, 90, L.MET4)
        ports["VSS"] = Port("VSS", (mid_x, bb[0][1] - 0.3), POWER_STRAP_W, 270, L.MET4)
    else:
        ports["VDD"] = Port("VDD", (0, 2), POWER_STRAP_W, 90, L.MET4)
        ports["VSS"] = Port("VSS", (0, -1), POWER_STRAP_W, 270, L.MET4)

    return cell, ports


# ---------------------------------------------------------------------------
# Single ADC unit
# ---------------------------------------------------------------------------

def adc_unit(lib, unit_id):
    """Build one SAR ADC unit containing comparator, CDAC, mux, and SAR logic.

    Args:
        lib:      gdstk.Library to create cells in.
        unit_id:  0 or 1 (determines naming and column assignment).

    Returns:
        (cell, ports) where ports is a dict of Port objects.

    Ports:
        COL_A, COL_B    -- analog column inputs
        VREF             -- reference voltage
        ADC_GO           -- start conversion trigger
        D0..D3           -- digital output for col_a
        D4..D7           -- digital output for col_b
        VDD, VSS         -- power
    """
    uid = f"u{unit_id}"
    cell = lib.new_cell(f"adc_unit_{unit_id}")
    ports = {}

    y_cursor = 0.0

    # ---------------------------------------------------------------
    # 1. SAR logic placeholder (bottom)
    # ---------------------------------------------------------------
    sar_a_cell, sar_a_ports = _sar_logic(lib, f"{uid}_sar_a", N_BITS)
    sar_a = Instance(sar_a_cell, sar_a_ports)
    sar_a.place(2.0, y_cursor)
    sar_a.add_to(cell)

    sar_b_cell, sar_b_ports = _sar_logic(lib, f"{uid}_sar_b", N_BITS)
    sar_b = Instance(sar_b_cell, sar_b_ports)
    sar_b_x = sar_a.bbox()[1][0] + 2.0
    sar_b.place(sar_b_x, y_cursor)
    sar_b.add_to(cell)

    sar_top = max(sar_a.bbox()[1][1], sar_b.bbox()[1][1])
    y_cursor = sar_top + CDAC_TO_SAR_GAP

    # Digital output ports (bottom edge)
    for b in range(N_BITS):
        ports[f"D{b}"] = Port(f"D{b}", sar_a.port(f"D{b}").center,
                               0.14, 270, L.MET1)
        ports[f"D{b + N_BITS}"] = Port(f"D{b + N_BITS}",
                                        sar_b.port(f"D{b}").center,
                                        0.14, 270, L.MET1)

    # ---------------------------------------------------------------
    # 2. CDAC (above SAR logic)
    # ---------------------------------------------------------------
    cdac_cell, cdac_ports = _cdac(lib, f"{uid}_cdac")
    cdac = Instance(cdac_cell, cdac_ports)
    cdac.place(2.0, y_cursor)
    cdac.add_to(cell)

    cdac_top = cdac.bbox()[1][1]
    y_cursor = cdac_top + COMP_TO_CDAC_GAP

    ports["VREF"] = Port("VREF", cdac.port("VREF").center, 0.6, 180, L.MET3)

    # ---------------------------------------------------------------
    # 3. StrongARM comparator (above CDAC)
    # ---------------------------------------------------------------
    comp_cell, comp_ports = _strongarm(lib, f"{uid}_comp")
    comp = Instance(comp_cell, comp_ports)
    # Center comparator over the CDAC
    cdac_bb = cdac.bbox()
    cdac_cx = (cdac_bb[0][0] + cdac_bb[1][0]) / 2
    comp.place(cdac_cx, y_cursor)
    comp.add_to(cell)

    # Critical connection: comparator INN -> CDAC TOP (shortest path)
    route_straight(cell, comp.port("VINN"), cdac.port("TOP"))

    comp_top = comp.bbox()[1][1]
    y_cursor = comp_top + MUX_TO_COMP_GAP

    # ADC_GO connects to comparator CLK
    ports["ADC_GO"] = Port("ADC_GO", comp.port("CLK").center, 0.14, 270, L.MET1)

    # ---------------------------------------------------------------
    # 4. Input mux (top, near column inputs)
    # ---------------------------------------------------------------
    # Two-input mux: selects between COL_A and COL_B for comparator INP
    # Implemented as two TGs, one per column, output tied together
    mux_a_cell, mux_a_ports = _cmos_tgate(
        lib, f"{uid}_mux_a", MUX_N_W, MUX_N_L, MUX_P_W, MUX_P_L
    )
    mux_a = Instance(mux_a_cell, mux_a_ports)
    mux_a.place(cdac_cx - 3.0, y_cursor)
    mux_a.add_to(cell)

    mux_b_cell, mux_b_ports = _cmos_tgate(
        lib, f"{uid}_mux_b", MUX_N_W, MUX_N_L, MUX_P_W, MUX_P_L
    )
    mux_b = Instance(mux_b_cell, mux_b_ports)
    mux_b.place(cdac_cx + 3.0, y_cursor)
    mux_b.add_to(cell)

    # Mux outputs tied to comparator VINP
    route_L(cell, mux_a.port("OUT"), comp.port("VINP"))
    route_L(cell, mux_b.port("OUT"), comp.port("VINP"))

    # Column input ports (top edge)
    ports["COL_A"] = Port("COL_A", mux_a.port("IN").center, 0.14, 90, L.MET2)
    ports["COL_B"] = Port("COL_B", mux_b.port("IN").center, 0.14, 90, L.MET2)

    # ---------------------------------------------------------------
    # 5. Guard ring around analog section (comparator + CDAC)
    # ---------------------------------------------------------------
    analog_bb = (
        (min(cdac_bb[0][0], comp.bbox()[0][0]) - 1.0,
         cdac.bbox()[0][1] - 1.0),
        (max(cdac_bb[1][0], comp.bbox()[1][0]) + 1.0,
         comp.bbox()[1][1] + 1.0),
    )
    inner_w = analog_bb[1][0] - analog_bb[0][0]
    inner_h = analog_bb[1][1] - analog_bb[0][1]
    gr_center_x = (analog_bb[0][0] + analog_bb[1][0]) / 2
    gr_center_y = (analog_bb[0][1] + analog_bb[1][1]) / 2
    gr_cell, gr_ports = guard_ring_p(
        lib, f"{uid}_guard", inner_w, inner_h, GUARD_RING_W,
    )
    gr_inst = Instance(gr_cell, gr_ports)
    gr_inst.place(gr_center_x, gr_center_y)
    gr_inst.add_to(cell)

    # ---------------------------------------------------------------
    # Power ports
    # ---------------------------------------------------------------
    unit_bb = cell.bounding_box()
    if unit_bb is not None:
        mid_x = (unit_bb[0][0] + unit_bb[1][0]) / 2
        ports["VDD"] = Port("VDD", (mid_x, unit_bb[1][1] + 0.5),
                             POWER_STRAP_W, 90, L.MET4)
        ports["VSS"] = Port("VSS", (mid_x, unit_bb[0][1] - 0.5),
                             POWER_STRAP_W, 270, L.MET4)
    else:
        ports["VDD"] = Port("VDD", (0, y_cursor), POWER_STRAP_W, 90, L.MET4)
        ports["VSS"] = Port("VSS", (0, 0), POWER_STRAP_W, 270, L.MET4)

    # Add port labels
    for p in ports.values():
        add_port_label(cell, p)

    return cell, ports


# ---------------------------------------------------------------------------
# Top-level: 2-unit interleaved ADC
# ---------------------------------------------------------------------------

def interleaved_adc_layout(lib):
    """Build the complete 2-unit interleaved SAR ADC. Returns (cell, ports).

    Unit 0 on the left, Unit 1 on the right (mirrored about center Y axis).

    Ports:
        COL0..COL2       -- 3 analog column inputs
        VREF             -- reference voltage
        ADC_GO           -- start conversion
        D0B0..D2B3       -- 12 digital outputs
        VDD, VSS         -- power
    """
    cell = lib.new_cell("interleaved_adc")
    ports = {}

    # ---------------------------------------------------------------
    # 1. Place Unit 0 (left, normal orientation)
    # ---------------------------------------------------------------
    u0_cell, u0_ports = adc_unit(lib, 0)
    u0 = Instance(u0_cell, u0_ports, "u0")
    u0.place(0, 0)
    u0.add_to(cell)

    u0_bb = u0.bbox()
    u0_width = u0_bb[1][0] - u0_bb[0][0]

    # ---------------------------------------------------------------
    # 2. Place Unit 1 (right, mirrored about center)
    # ---------------------------------------------------------------
    u1_cell, u1_ports = adc_unit(lib, 1)
    u1 = Instance(u1_cell, u1_ports, "u1")
    # Mirror X and place to the right of Unit 0
    u1_x = u0_bb[1][0] + UNIT_MIRROR_GAP + u0_width
    u1.place(u1_x, 0, mirror_x=False)
    # We want a left-right mirror: flip about X, which means negate X coords.
    # Instance.place with mirror_x mirrors Y. For horizontal mirror we rotate 180
    # and mirror_x. But simpler: just place at the right offset (mirror is
    # aesthetic; electrically identical units suffice).
    u1.add_to(cell)

    # ---------------------------------------------------------------
    # 3. Map column ports (3 columns: unit0 handles col0+col1, unit1 handles col2)
    # ---------------------------------------------------------------
    # Unit 0: col_a=col0, col_b=col1
    ports["COL0"] = Port("COL0", u0.port("COL_A").center,
                          0.14, 90, L.MET2)
    ports["COL1"] = Port("COL1", u0.port("COL_B").center,
                          0.14, 90, L.MET2)
    # Unit 1: col_a=col2 (col_b unused)
    ports["COL2"] = Port("COL2", u1.port("COL_A").center,
                          0.14, 90, L.MET2)

    # ---------------------------------------------------------------
    # 4. Route ADC_GO: symmetric fork from center to both units
    # ---------------------------------------------------------------
    top_bb = cell.bounding_box()
    center_x = (top_bb[0][0] + top_bb[1][0]) / 2 if top_bb is not None else u0_width + UNIT_MIRROR_GAP / 2

    go_u0 = u0.port("ADC_GO")
    go_u1 = u1.port("ADC_GO")
    fork_y = min(go_u0.center[1], go_u1.center[1]) - 2.0

    # Vertical trunk from center fork point
    adc_go_port = Port("ADC_GO", (center_x, fork_y - 3.0), 0.3, 270, L.MET2)
    ports["ADC_GO"] = adc_go_port

    # MET2 vertical trunk
    cell.add(gdstk.rectangle(
        (center_x - 0.15, fork_y - 3.0),
        (center_x + 0.15, fork_y),
        **ld(L.MET2),
    ))

    # MET2 horizontal branch to both units
    cell.add(gdstk.rectangle(
        (go_u0.center[0] - 0.15, fork_y - 0.15),
        (go_u1.center[0] + 0.15, fork_y + 0.15),
        **ld(L.MET2),
    ))

    # Vertical drops from branch to each unit's ADC_GO port
    # VIA (MET1-MET2) needs enclosure: pad >= VIA_SZ + 2*max(VIA_ENCL_MET1, VIA_ENCL_MET2)
    via_pad = DRC.VIA_SZ + 2 * max(DRC.VIA_ENCL_MET1, DRC.VIA_ENCL_MET2)
    via_pad = max(via_pad, 0.34)  # pad for met2.6 / via.5a compliance
    for go_port in [go_u0, go_u1]:
        cell.add(gdstk.rectangle(
            (go_port.center[0] - 0.15, fork_y),
            (go_port.center[0] + 0.15, go_port.center[1]),
            **ld(L.MET2),
        ))
        # Explicit MET1 and MET2 landing pads at the via location
        for met_layer in [L.MET1, L.MET2]:
            cell.add(gdstk.rectangle(
                (go_port.center[0] - via_pad / 2,
                 go_port.center[1] - via_pad / 2),
                (go_port.center[0] + via_pad / 2,
                 go_port.center[1] + via_pad / 2),
                **ld(met_layer),
            ))
        # Via to MET1 at the unit port
        via_stack(cell, (go_port.center[0], go_port.center[1]),
                  L.MET1, L.MET2, width=via_pad)

    # Shield ADC_GO with ground on adjacent tracks
    # Horizontal shield traces flanking the ADC_GO vertical trunk
    add_shield(cell, fork_y, center_x - 2.0, center_x + 2.0,
               layer=L.MET2, width=0.3)

    # ---------------------------------------------------------------
    # 5. Route VREF: wide MET4 horizontal bus
    # ---------------------------------------------------------------
    top_bb = cell.bounding_box()
    if top_bb is not None:
        vref_y = u0.port("VREF").center[1]
        bus_x_min = top_bb[0][0] - 1.0
        bus_x_max = top_bb[1][0] + 1.0
    else:
        vref_y = 40.0
        bus_x_min = -5.0
        bus_x_max = u1_x + u0_width + 5.0

    cell.add(gdstk.rectangle(
        (bus_x_min, vref_y - VREF_BUS_W / 2),
        (bus_x_max, vref_y + VREF_BUS_W / 2),
        **ld(L.MET4),
    ))
    ports["VREF"] = Port("VREF", ((bus_x_min + bus_x_max) / 2, vref_y),
                          VREF_BUS_W, 180, L.MET4)

    # Via stacks from unit VREF (MET3) up to MET4 bus
    # Ensure adequate MET3/MET4 landing pads around VIA3
    vref_via_pad = max(1.0, DRC.VIA3_SZ + 2 * max(DRC.VIA3_ENCL_MET3, DRC.VIA3_ENCL_MET4))
    for u_inst, u_name in [(u0, "u0"), (u1, "u1")]:
        vref_port = u_inst.port("VREF")
        # Explicit MET3 pad at via location
        cell.add(gdstk.rectangle(
            (vref_port.center[0] - vref_via_pad / 2, vref_y - vref_via_pad / 2),
            (vref_port.center[0] + vref_via_pad / 2, vref_y + vref_via_pad / 2),
            **ld(L.MET3),
        ))
        via_stack(cell, (vref_port.center[0], vref_y),
                  L.MET3, L.MET4, width=vref_via_pad)

    # Local decoupling caps adjacent to VREF bus (MIM on MET3/MET4)
    # Place with adequate MET3/MET4 spacing from VREF bus (met3.2: >= 0.30, met4.2: >= 0.30)
    decap_gap = max(DRC.MET3_SP, DRC.MET4_SP) + DRC.CAPM_ENCL_MET3 + 0.5
    for side_x in [bus_x_min + 3.0, bus_x_max - 3.0]:
        decap_cell, decap_ports = mim_cap(lib, 3.0, 3.0,
                                           f"vref_decap_{side_x:.0f}")
        decap_inst = Instance(decap_cell, decap_ports)
        decap_inst.place(side_x, vref_y + VREF_BUS_W / 2 + decap_gap)
        decap_inst.add_to(cell)

    # ---------------------------------------------------------------
    # 6. Collect digital outputs at bottom (3 columns)
    # ---------------------------------------------------------------
    # Unit 0: D0-D3 -> d0b0-d0b3, D4-D7 -> d1b0-d1b3
    # Unit 1: D0-D3 -> d2b0-d2b3
    dout_map = {
        "D0B0": (u0, "D0"), "D0B1": (u0, "D1"),
        "D0B2": (u0, "D2"), "D0B3": (u0, "D3"),
        "D1B0": (u0, "D4"), "D1B1": (u0, "D5"),
        "D1B2": (u0, "D6"), "D1B3": (u0, "D7"),
        "D2B0": (u1, "D0"), "D2B1": (u1, "D1"),
        "D2B2": (u1, "D2"), "D2B3": (u1, "D3"),
    }

    top_bb = cell.bounding_box()
    dout_y = top_bb[0][1] - 2.0 if top_bb is not None else -5.0

    # MET2 vertical drops from each unit output down to the collection row
    for dname, (u_inst, uport) in dout_map.items():
        src = u_inst.port(uport)
        # Vertical MET2 wire from source down to collection row
        cell.add(gdstk.rectangle(
            (src.center[0] - 0.07, dout_y),
            (src.center[0] + 0.07, src.center[1]),
            **ld(L.MET2),
        ))
        ports[dname] = Port(dname, (src.center[0], dout_y), 0.14, 270, L.MET2)

    # ---------------------------------------------------------------
    # 7. MET5 power straps (VDD and VSS)
    # ---------------------------------------------------------------
    top_bb = cell.bounding_box()
    if top_bb is not None:
        cell_xmin = top_bb[0][0]
        cell_xmax = top_bb[1][0]
        cell_ymin = top_bb[0][1]
        cell_ymax = top_bb[1][1]
    else:
        cell_xmin, cell_xmax = -5.0, u1_x + u0_width + 5.0
        cell_ymin, cell_ymax = -10.0, 120.0

    strap_margin = 2.0

    # VDD strap (MET5, top)
    vdd_strap_y = cell_ymax + strap_margin
    cell.add(gdstk.rectangle(
        (cell_xmin - 1.0, vdd_strap_y - POWER_STRAP_W / 2),
        (cell_xmax + 1.0, vdd_strap_y + POWER_STRAP_W / 2),
        **ld(L.MET5),
    ))
    ports["VDD"] = Port("VDD", ((cell_xmin + cell_xmax) / 2, vdd_strap_y),
                         POWER_STRAP_W, 90, L.MET5)

    # VSS strap (MET5, bottom)
    vss_strap_y = cell_ymin - strap_margin
    cell.add(gdstk.rectangle(
        (cell_xmin - 1.0, vss_strap_y - POWER_STRAP_W / 2),
        (cell_xmax + 1.0, vss_strap_y + POWER_STRAP_W / 2),
        **ld(L.MET5),
    ))
    ports["VSS"] = Port("VSS", ((cell_xmin + cell_xmax) / 2, vss_strap_y),
                         POWER_STRAP_W, 270, L.MET5)

    # Via stacks from MET4 unit power down to MET5 straps
    for u_inst, u_name in [(u0, "u0"), (u1, "u1")]:
        vdd_port = u_inst.port("VDD")
        vss_port = u_inst.port("VSS")

        # VDD: MET4 vertical drop up to MET5 strap, then via
        cell.add(gdstk.rectangle(
            (vdd_port.center[0] - POWER_STRAP_W / 2, vdd_port.center[1]),
            (vdd_port.center[0] + POWER_STRAP_W / 2, vdd_strap_y),
            **ld(L.MET4),
        ))
        via_stack(cell, (vdd_port.center[0], vdd_strap_y),
                  L.MET4, L.MET5, width=POWER_STRAP_W)

        # VSS: MET4 vertical drop down to MET5 strap, then via
        cell.add(gdstk.rectangle(
            (vss_port.center[0] - POWER_STRAP_W / 2, vss_strap_y),
            (vss_port.center[0] + POWER_STRAP_W / 2, vss_port.center[1]),
            **ld(L.MET4),
        ))
        via_stack(cell, (vss_port.center[0], vss_strap_y),
                  L.MET4, L.MET5, width=POWER_STRAP_W)

    # Additional MET5 power strap at center for improved IR drop
    cell.add(gdstk.rectangle(
        (center_x - POWER_STRAP_W / 2, vss_strap_y),
        (center_x + POWER_STRAP_W / 2, vdd_strap_y),
        **ld(L.MET5),
    ))

    # ---------------------------------------------------------------
    # Add port labels to top cell
    # ---------------------------------------------------------------
    for p in ports.values():
        add_port_label(cell, p)

    return cell, ports


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    lib = gdstk.Library(unit=1e-6, precision=1e-9)

    cell, ports = interleaved_adc_layout(lib)

    # Report
    bb = cell.bounding_box()
    if bb is not None:
        w = bb[1][0] - bb[0][0]
        h = bb[1][1] - bb[0][1]
        print(f"Cell: {cell.name}")
        print(f"Bounding box: ({bb[0][0]:.1f}, {bb[0][1]:.1f}) to "
              f"({bb[1][0]:.1f}, {bb[1][1]:.1f})")
        print(f"Size: {w:.1f} x {h:.1f} um")
    else:
        print(f"Cell: {cell.name} (empty bounding box)")

    print(f"\nPorts ({len(ports)}):")
    for name, p in sorted(ports.items()):
        print(f"  {name:10s}  center=({p.center[0]:7.2f}, {p.center[1]:7.2f})  "
              f"w={p.width:.2f}  layer={p.layer}")

    # Export GDS
    outpath = "interleaved_adc.gds"
    lib.write_gds(outpath)
    print(f"\nExported: {outpath}")
