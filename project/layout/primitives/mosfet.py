"""MOSFET layout generators for Sky130.

Generates DRC-clean NFET and PFET cells with multi-finger support,
proper enclosures, contacts, and labeled ports.

Layout structure (single finger, top view, x is horizontal, y is vertical):

    +------ poly (gate) ------+
    |         endcap          |
    +-----------+-------------+
    |   S/D     |  gate |  S/D|     DIFF region
    |  (LICON)  | (poly)|(LICON)
    +-----------+-------------+
    |         endcap          |
    +-------------------------+
    |     gate contact        |  NPC + LICON + LI1 on poly
    |     MCON -> MET1        |
    +-------------------------+

Multi-finger: S-G-D-G-S-G-D-G-S interdigitated.
Source = even-indexed S/D regions, Drain = odd-indexed.

Ports: S (met1, south), D (met1, north), G (met1, north).
Cell origin at geometric center.
"""

import gdstk
from ..layers import L, ld
from ..drc import DRC
from ..ports import Port
from .contact import licon_array, mcon_array


# ---------------------------------------------------------------------------
# Constants derived from DRC rules
# ---------------------------------------------------------------------------

# Minimum LICON-to-gate-edge spacing (licon.11)
_LICON_GATE_SP = 0.055

# Minimum poly-LICON-to-diffusion spacing (licon.14 / licon.9+psdm.5a)
# Use the stricter PMOS rule so the same geometry works for both.
# 0.40 um gives headroom over the 0.235 um minimum and ensures the gate contact
# LI1 pad clears S/D LI1 strips by > LI1_SP (0.17) in all finger configurations.
_POLY_LICON_DIFF_SP = 0.40

# Poly enclosure of LICON (licon.8/8a) — each side
# 0.08 um provides margin over the 0.05 um minimum to satisfy both licon.8 and licon.8a.
_POLY_ENCL_LICON = 0.08

# MET1 minimum area (met1.6)
_MET1_MIN_AREA = 0.083


def _mosfet_cell(lib: gdstk.Library, w: float, l: float, nf: int,
                 name: str, is_pmos: bool) -> tuple[gdstk.Cell, dict[str, Port]]:
    """Build an nf-finger MOSFET cell centered at the origin.

    Coordinate system:
        x: horizontal (across fingers)
        y: vertical (along channel width)
    """
    cell = lib.new_cell(name)

    wf = w / nf            # per-finger channel width
    gate_l = l              # drawn gate length
    # poly.7: PMOS requires 0.25 um poly extension past diff; NMOS uses 0.13.
    poly_ext = DRC.POLY_EXT_DIFF_PMOS if is_pmos else DRC.POLY_EXT_DIFF
    poly_endcap = DRC.POLY_ENDCAP  # 0.13 um -- diff extends beyond poly (same value)

    # LICON / MCON geometry
    licon_sz = DRC.LICON_SZ         # 0.17
    licon_sp = DRC.LICON_SP         # 0.17
    licon_pitch = licon_sz + licon_sp  # 0.34
    li_enc = DRC.LI1_ENCL_LICON    # 0.08
    mcon_sz = DRC.MCON_SZ           # 0.17
    mcon_sp = DRC.MCON_SP           # 0.19

    # Use non-wide enclosure rule for MET1 around MCON (met1.4: >= 0.03)
    # The wide rule (met1.5: 0.06) only applies when MET1 width >= 0.36 um;
    # our S/D pads are narrower, so the non-wide rule is correct.
    m1_enc = DRC.MCON_ENCL_MET1  # 0.03

    # S/D contact region width: must fit LICON with proper gate clearance
    # licon.11: LICON edge to gate edge >= 0.055
    sd_contact_w = max(
        licon_sz + 2 * _LICON_GATE_SP,     # 0.17 + 0.11 = 0.28
        licon_sz + 2 * DRC.DIFF_ENCL_LICON, # 0.17 + 0.08 = 0.25
    )

    # LI1 width over S/D contacts
    li_w = licon_sz + 2 * li_enc  # 0.17 + 0.16 = 0.33

    # Finger pitch: gate_l + max(sd_contact_w, li_w + LI1_SP)
    # Must satisfy:
    # 1) S/D contact region fits: gate_l + sd_contact_w
    # 2) LI1 spacing between adjacent S/D LI1 strips: gap = pitch - li_w >= LI1_SP (0.17)
    # 3) MET1 spacing between adjacent MET1 pads
    m1_w = mcon_sz + 2 * m1_enc  # 0.17 + 0.12 = 0.29
    min_pitch_li = li_w + DRC.LI1_SP       # 0.33 + 0.17 = 0.50
    min_pitch_sd = gate_l + sd_contact_w   # 0.15 + 0.28 = 0.43
    min_pitch_m1 = m1_w + DRC.MET1_SP      # 0.29 + 0.14 = 0.43
    # diff/tap.3: S/D contact regions need >= DIFF_SP apart.
    min_pitch_diff = sd_contact_w + DRC.DIFF_SP  # 0.28 + 0.27 = 0.55
    # MET1 routing: a min-width (0.14um) wire at gate x=0 must clear the
    # S/D MET1 pad at x=poly_pitch/2 with >= MET1_SP spacing, and vice-versa.
    # Note: gate MET1 pad is at gc_y (above diffusion), not at S/D y=0, so they
    # don't conflict directly.  This constraint is for external routing wires.
    min_pitch_m1_routing = m1_w + DRC.MET1_W + 2 * DRC.MET1_SP + 0.03  # 0.68
    poly_pitch = max(min_pitch_li, min_pitch_sd, min_pitch_m1, min_pitch_diff,
                     min_pitch_m1_routing)

    # Recalculate sd_contact_w to fill available space (pitch - gate_l)
    sd_contact_w = poly_pitch - gate_l     # 0.55 - 0.15 = 0.40

    # Total array width: (nf+1) S/D regions + nf gates
    arr_w = nf * poly_pitch + sd_contact_w
    half_arr_w = arr_w / 2
    half_wf = wf / 2

    # Number of vertical LICONs that fit in a S/D region
    usable_h = wf - 2 * DRC.DIFF_ENCL_LICON
    n_licon_y = max(1, int((usable_h + licon_sp) / licon_pitch))

    # ---- Diffusion ----
    cell.add(gdstk.rectangle(
        (-half_arr_w, -half_wf),
        (half_arr_w, half_wf),
        **ld(L.DIFF),
    ))

    # ---- Implant (NSDM for NMOS, PSDM for PMOS) ----
    imp_enc = DRC.NSDM_ENCL
    imp_layer = L.PSDM if is_pmos else L.NSDM
    imp_enc_y = max(imp_enc, poly_ext + 0.01)
    cell.add(gdstk.rectangle(
        (-half_arr_w - imp_enc, -half_wf - imp_enc_y),
        (half_arr_w + imp_enc, half_wf + imp_enc_y),
        **ld(imp_layer),
    ))

    # ---- N-well for PMOS ----
    if is_pmos:
        # Use max of NWELL_ENCL_DIFF and NDIFF_SP_NWELL to ensure the NWELL
        # edge is far enough from any adjacent NFET diffusion (diff/tap.9).
        # Add 0.04 um margin to avoid boundary-case violations from grid snapping.
        nw_enc = max(DRC.NWELL_ENCL_DIFF, DRC.NDIFF_SP_NWELL) + 0.04
        cell.add(gdstk.rectangle(
            (-half_arr_w - nw_enc, -half_wf - nw_enc - poly_ext),
            (half_arr_w + nw_enc, half_wf + nw_enc + poly_ext),
            **ld(L.NWELL),
        ))

    # ---- Poly gates ----
    # Gate i center: -half_arr_w + sd_contact_w + i*poly_pitch + gate_l/2
    gate_xs = []
    for i in range(nf):
        gx = -half_arr_w + sd_contact_w + i * poly_pitch + gate_l / 2
        gate_xs.append(gx)
        cell.add(gdstk.rectangle(
            (gx - gate_l / 2, -half_wf - poly_ext),
            (gx + gate_l / 2, half_wf + poly_ext),
            **ld(L.POLY),
        ))

    # ---- S/D contacts ----
    # There are nf+1 S/D regions. Region 0 = source, 1 = drain, 2 = source ...
    sd_centers = []  # (x_center, "S" or "D")
    for i in range(nf + 1):
        sx = -half_arr_w + sd_contact_w / 2 + i * poly_pitch
        is_source = (i % 2 == 0)
        sd_centers.append((sx, "S" if is_source else "D"))

        # LICON array vertically within diffusion
        for j in range(n_licon_y):
            ly = -(n_licon_y - 1) * licon_pitch / 2 + j * licon_pitch
            cell.add(gdstk.rectangle(
                (sx - licon_sz / 2, ly - licon_sz / 2),
                (sx + licon_sz / 2, ly + licon_sz / 2),
                **ld(L.LICON),
            ))

        # LI1 strip over S/D contacts — height covers all LICONs with enclosure.
        # Cap the top to maintain >= LI1_SP from gate contact LI1 bottom edge
        # (relevant for nf>=2 where middle S/D is at same x as gate contact).
        li_h_raw = max(li_w, (n_licon_y - 1) * licon_pitch + licon_sz + 2 * li_enc)
        li_pad_h = licon_sz + 2 * li_enc  # gate LI1 pad height
        # Gate LI1 bottom edge y-coordinate:
        gc_li_bot = (half_wf + _POLY_LICON_DIFF_SP + licon_sz / 2) - li_pad_h / 2
        # Maximum S/D LI1 top edge to maintain li.3 clearance:
        max_li_top = gc_li_bot - DRC.LI1_SP
        # Keep symmetric about y=0 unless constrained:
        li_h = li_h_raw
        if li_h / 2 > max_li_top and max_li_top > 0:
            li_h = 2 * max_li_top
        cell.add(gdstk.rectangle(
            (sx - li_w / 2, -li_h / 2),
            (sx + li_w / 2, li_h / 2),
            **ld(L.LI1),
        ))

        # MCON (centered at S/D) — single contact
        cell.add(gdstk.rectangle(
            (sx - mcon_sz / 2, -mcon_sz / 2),
            (sx + mcon_sz / 2, mcon_sz / 2),
            **ld(L.MCON),
        ))

        # MET1 pad — use wide enclosure, ensure minimum area
        m1_h = m1_w  # square pad
        if m1_w * m1_h < _MET1_MIN_AREA:
            # Increase height to meet minimum area
            m1_h = _MET1_MIN_AREA / m1_w + 0.01
        cell.add(gdstk.rectangle(
            (sx - m1_w / 2, -m1_h / 2),
            (sx + m1_w / 2, m1_h / 2),
            **ld(L.MET1),
        ))

    # ---- Gate contact above diffusion ----
    # licon.14 / licon.9+psdm.5a: poly LICON to diffusion >= 0.235
    # Distance from bottom of gate LICON to top of diff = poly_ext + gc_gap
    gc_gap = _POLY_LICON_DIFF_SP - poly_ext  # 0.25 - 0.13 = 0.12
    gc_y = half_wf + poly_ext + gc_gap + licon_sz / 2

    # Poly bus height: must enclose LICON by >= 0.08 each side (licon.8/8a)
    poly_bus_h = licon_sz + 2 * _POLY_ENCL_LICON  # 0.17 + 0.16 = 0.33

    # Multi-finger: horizontal poly bus connecting all gates at gate contact y
    if nf > 1:
        cell.add(gdstk.rectangle(
            (gate_xs[0] - gate_l / 2, gc_y - poly_bus_h / 2),
            (gate_xs[-1] + gate_l / 2, gc_y + poly_bus_h / 2),
            **ld(L.POLY),
        ))

    # Extend existing gate poly up to cover gate contact area
    # The gate poly already extends to half_wf + poly_ext. We need poly to
    # reach gc_y + poly_bus_h/2. Add a poly rectangle from gate to cover.
    for gx in gate_xs:
        poly_top = half_wf + poly_ext
        gc_poly_top = gc_y + poly_bus_h / 2
        if gc_poly_top > poly_top:
            cell.add(gdstk.rectangle(
                (gx - gate_l / 2, poly_top),
                (gx + gate_l / 2, gc_poly_top),
                **ld(L.POLY),
            ))

    # Gate LICON (centered horizontally on the device)
    gc_x = 0.0

    # Poly pad at gate contact: must enclose LICON by _POLY_ENCL_LICON on all sides.
    # For nf=1 the gate poly is only gate_l wide (0.15), which is narrower than
    # the LICON (0.17). Add a wider poly rectangle centered at the gate contact.
    poly_gc_w = licon_sz + 2 * _POLY_ENCL_LICON  # 0.17 + 0.16 = 0.33
    cell.add(gdstk.rectangle(
        (gc_x - poly_gc_w / 2, gc_y - poly_bus_h / 2),
        (gc_x + poly_gc_w / 2, gc_y + poly_bus_h / 2),
        **ld(L.POLY),
    ))
    cell.add(gdstk.rectangle(
        (gc_x - licon_sz / 2, gc_y - licon_sz / 2),
        (gc_x + licon_sz / 2, gc_y + licon_sz / 2),
        **ld(L.LICON),
    ))

    # NPC around gate LICON
    npc_enc = DRC.NPC_ENCL_LICON
    cell.add(gdstk.rectangle(
        (gc_x - licon_sz / 2 - npc_enc, gc_y - licon_sz / 2 - npc_enc),
        (gc_x + licon_sz / 2 + npc_enc, gc_y + licon_sz / 2 + npc_enc),
        **ld(L.NPC),
    ))

    # LI1 pad over gate LICON
    li_pad = licon_sz + 2 * li_enc
    cell.add(gdstk.rectangle(
        (gc_x - li_pad / 2, gc_y - li_pad / 2),
        (gc_x + li_pad / 2, gc_y + li_pad / 2),
        **ld(L.LI1),
    ))

    # MCON on gate LI1 -> MET1
    cell.add(gdstk.rectangle(
        (gc_x - mcon_sz / 2, gc_y - mcon_sz / 2),
        (gc_x + mcon_sz / 2, gc_y + mcon_sz / 2),
        **ld(L.MCON),
    ))

    # MET1 pad for gate — non-wide enclosure, ensure min area
    m1_w_gc = mcon_sz + 2 * m1_enc
    m1_h_gc = m1_w_gc
    if m1_w_gc * m1_h_gc < _MET1_MIN_AREA:
        m1_h_gc = _MET1_MIN_AREA / m1_w_gc + 0.01
    cell.add(gdstk.rectangle(
        (gc_x - m1_w_gc / 2, gc_y - m1_h_gc / 2),
        (gc_x + m1_w_gc / 2, gc_y + m1_h_gc / 2),
        **ld(L.MET1),
    ))

    # ---- Collect S/D centers and build MET1 buses ----
    s_xs = [sx for sx, t in sd_centers if t == "S"]
    d_xs = [sx for sx, t in sd_centers if t == "D"]

    m1_bus_h = mcon_sz + 2 * m1_enc

    # Ensure bus meets minimum area (width * height >= 0.083)
    # Width for multi-source/drain buses spans from min to max pad edges.

    # MET1 bus connecting all source pads
    if len(s_xs) > 1:
        bus_w = max(s_xs) - min(s_xs) + m1_w
        bus_h = max(m1_bus_h, _MET1_MIN_AREA / bus_w + 0.001)
        cell.add(gdstk.rectangle(
            (min(s_xs) - m1_w / 2, -bus_h / 2),
            (max(s_xs) + m1_w / 2, bus_h / 2),
            **ld(L.MET1),
        ))

    # MET1 bus connecting all drain pads
    if len(d_xs) > 1:
        bus_w = max(d_xs) - min(d_xs) + m1_w
        bus_h = max(m1_bus_h, _MET1_MIN_AREA / bus_w + 0.001)
        cell.add(gdstk.rectangle(
            (min(d_xs) - m1_w / 2, -bus_h / 2),
            (max(d_xs) + m1_w / 2, bus_h / 2),
            **ld(L.MET1),
        ))

    # ---- Ports ----
    s_port_x = sum(s_xs) / len(s_xs) if s_xs else 0.0
    d_port_x = sum(d_xs) / len(d_xs) if d_xs else 0.0

    ports = {
        "G": Port("G", (gc_x, gc_y), m1_w_gc, 90.0, L.MET1),
        "S": Port("S", (s_port_x, -half_wf), m1_bus_h, 270.0, L.MET1),
        "D": Port("D", (d_port_x, half_wf), m1_bus_h, 90.0, L.MET1),
    }

    return cell, ports


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def nfet(lib: gdstk.Library, w: float, l: float, nf: int = 1,
         name: str | None = None) -> tuple[gdstk.Cell, dict[str, Port]]:
    """Generate an N-channel MOSFET layout cell.

    Args:
        lib:  gdstk Library to add the cell to.
        w:    Total channel width in microns (split across fingers).
        l:    Drawn gate length in microns (typically 0.15).
        nf:   Number of fingers.
        name: Cell name. Auto-generated if None.

    Returns:
        (cell, ports) with ports "G" (met1, north), "S" (met1, south),
        "D" (met1, north).
    """
    if name is None:
        w_nm = round(w * 1000)
        l_nm = round(l * 1000)
        name = f"sky130_nfet_w{w_nm}_l{l_nm}_nf{nf}"
    return _mosfet_cell(lib, w, l, nf, name, is_pmos=False)


def pfet(lib: gdstk.Library, w: float, l: float, nf: int = 1,
         name: str | None = None) -> tuple[gdstk.Cell, dict[str, Port]]:
    """Generate a P-channel MOSFET layout cell.

    Args:
        lib:  gdstk Library to add the cell to.
        w:    Total channel width in microns (split across fingers).
        l:    Drawn gate length in microns (typically 0.15).
        nf:   Number of fingers.
        name: Cell name. Auto-generated if None.

    Returns:
        (cell, ports) with ports "G" (met1, north), "S" (met1, south),
        "D" (met1, north). Includes NWELL.
    """
    if name is None:
        w_nm = round(w * 1000)
        l_nm = round(l * 1000)
        name = f"sky130_pfet_w{w_nm}_l{l_nm}_nf{nf}"
    return _mosfet_cell(lib, w, l, nf, name, is_pmos=True)
