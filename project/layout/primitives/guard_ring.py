"""Guard ring generators for Sky130.

P+ guard ring (substrate contact) around NFET regions -- connects to VSS.
N+ guard ring (N-well contact) around PFET regions -- connects to VDD.

The ring is drawn using boolean operations (outer - inner) so all layers
form continuous frames with no overlapping segments at corners.

inner_w / inner_h define the guaranteed-clear opening.  No guard-ring
layer (TAP, implant, LI1, MET1) extends into this region.  NWELL may
extend slightly (~0.055um) past the inner boundary to maintain the
required NWELL enclosure of TAP (0.18um).

Each function returns (cell, ports) where ports has "VSS" or "VDD" keys
at the midpoint of each ring segment.
"""

import gdstk
from ..layers import L, ld
from ..drc import DRC
from ..ports import Port
from .contact import licon_array, mcon_array, via_array


def _ring_rect(outer_hw, outer_hh, inner_hw, inner_hh, layer):
    """Create a ring shape via boolean (outer rect - inner rect).

    Returns a list of gdstk polygons on the given layer.
    """
    outer = gdstk.rectangle((-outer_hw, -outer_hh), (outer_hw, outer_hh))
    inner = gdstk.rectangle((-inner_hw, -inner_hh), (inner_hw, inner_hh))
    return gdstk.boolean(outer, inner, "not",
                         layer=layer[0], datatype=layer[1])


def _guard_ring(lib: gdstk.Library, name: str,
                inner_w: float, inner_h: float, ring_w: float,
                imp_layer: tuple[int, int], nwell: bool,
                port_name: str) -> tuple[gdstk.Cell, dict[str, Port]]:
    """Draw a rectangular guard ring cell.

    The inner opening is centered at the origin with dimensions inner_w x inner_h.
    NWELL may extend slightly into this rectangle to meet enclosure rules.

    The TAP ring is inset from the inner boundary by the implant enclosure
    so that the implant ring's inner edge aligns exactly with inner_w/inner_h.
    """
    cell = lib.new_cell(name)

    imp_enc = DRC.NSDM_ENCL   # same value for PSDM
    li_enc = DRC.LI1_ENCL_LICON
    m1_enc = DRC.MCON_ENCL_MET1

    hiw = inner_w / 2
    hih = inner_h / 2

    # TAP inner edge is inset by imp_enc so implant stays outside inner_w x inner_h
    tap_inner_hw = hiw + imp_enc
    tap_inner_hh = hih + imp_enc

    # TAP outer edge
    tap_outer_hw = tap_inner_hw + ring_w
    tap_outer_hh = tap_inner_hh + ring_w

    # --- TAP ring ---
    cell.add(*_ring_rect(tap_outer_hw, tap_outer_hh,
                         tap_inner_hw, tap_inner_hh, L.TAP))

    # --- Implant ring (encloses TAP by imp_enc on all sides) ---
    imp_outer_hw = tap_outer_hw + imp_enc
    imp_outer_hh = tap_outer_hh + imp_enc
    # Inner edge of implant = TAP inner edge - imp_enc = hiw + imp_enc - imp_enc = hiw
    imp_inner_hw = hiw
    imp_inner_hh = hih
    cell.add(*_ring_rect(imp_outer_hw, imp_outer_hh,
                         imp_inner_hw, imp_inner_hh, imp_layer))

    # --- NWELL ring (for N+ guard ring only) ---
    if nwell:
        nw_enc = DRC.NWELL_ENCL_TAP
        nw_outer_hw = tap_outer_hw + nw_enc
        nw_outer_hh = tap_outer_hh + nw_enc
        # Inner edge: TAP inner minus nwell enclosure
        # NWELL must enclose TAP by nw_enc on all sides, including the inner edge.
        # This means NWELL extends slightly (0.055um) into the opening -- safe for isolation.
        nw_inner_hw = tap_inner_hw - nw_enc
        nw_inner_hh = tap_inner_hh - nw_enc
        # Clamp: N-well ring arm width must meet nwell.1 minimum (0.84 um)
        nw_arm_w = nw_outer_hw - nw_inner_hw
        if nw_arm_w < DRC.NWELL_W:
            nw_outer_hw = nw_inner_hw + DRC.NWELL_W
        nw_arm_h = nw_outer_hh - nw_inner_hh
        if nw_arm_h < DRC.NWELL_W:
            nw_outer_hh = nw_inner_hh + DRC.NWELL_W
        cell.add(*_ring_rect(nw_outer_hw, nw_outer_hh,
                             nw_inner_hw, nw_inner_hh, L.NWELL))

    # --- Contacts and metal as boolean rings (no corner overlaps) ---
    # LICON fill region: TAP inset by DIFF_ENCL_LICON
    ct_margin = DRC.DIFF_ENCL_LICON
    ct_inner_hw = tap_inner_hw + ct_margin
    ct_inner_hh = tap_inner_hh + ct_margin
    ct_outer_hw = tap_outer_hw - ct_margin
    ct_outer_hh = tap_outer_hh - ct_margin

    # LI1 ring: encloses LICON fill region with li_enc
    li_inner_hw = ct_inner_hw - li_enc
    li_inner_hh = ct_inner_hh - li_enc
    li_outer_hw = ct_outer_hw + li_enc
    li_outer_hh = ct_outer_hh + li_enc
    cell.add(*_ring_rect(li_outer_hw, li_outer_hh,
                         li_inner_hw, li_inner_hh, L.LI1))

    # MCON fill region (slightly larger margin for MCON enclosure)
    mc_margin = max(ct_margin, DRC.MCON_ENCL_MET1_WIDE)
    mc_inner_hw = tap_inner_hw + mc_margin
    mc_inner_hh = tap_inner_hh + mc_margin
    mc_outer_hw = tap_outer_hw - mc_margin
    mc_outer_hh = tap_outer_hh - mc_margin

    # MET1 ring: encloses MCON fill region with m1_enc
    m1_inner_hw = mc_inner_hw - m1_enc
    m1_inner_hh = mc_inner_hh - m1_enc
    m1_outer_hw = mc_outer_hw + m1_enc
    m1_outer_hh = mc_outer_hh + m1_enc
    cell.add(*_ring_rect(m1_outer_hw, m1_outer_hh,
                         m1_inner_hw, m1_inner_hh, L.MET1))

    # --- Place LICON and MCON contacts in 4 segments (no overlap at corners) ---
    # Segments are defined to NOT share corner regions.
    # Bottom/top have x-ranges inset by MCON_SP at corners where they meet
    # left/right segments, preventing MCON spacing violations at shared edges.
    # Corner inset: MCON_SP + MCON_SZ ensures the closest MCON in a
    # perpendicular segment is at least MCON_SP away (mcon.2 rule).
    corner_inset = DRC.MCON_SP + DRC.MCON_SZ  # 0.19 + 0.17 = 0.36
    segments = [
        # (x0, y0, x1, y1, port_orient)
        (-ct_outer_hw + corner_inset, -ct_outer_hh, ct_outer_hw - corner_inset, -ct_inner_hh, 270.0),   # bottom
        (-ct_outer_hw + corner_inset, ct_inner_hh, ct_outer_hw - corner_inset, ct_outer_hh, 90.0),      # top
        (-ct_outer_hw, -ct_inner_hh + corner_inset, -ct_inner_hw, ct_inner_hh - corner_inset, 180.0),   # left
        (ct_inner_hw, -ct_inner_hh + corner_inset, ct_outer_hw, ct_inner_hh - corner_inset, 0.0),       # right
    ]

    ports = {}
    seg_names = ["bot", "top", "left", "right"]

    for seg_name, (sx0, sy0, sx1, sy1, orient) in zip(seg_names, segments):
        sw = sx1 - sx0
        sh = sy1 - sy0
        if sw < DRC.LICON_SZ or sh < DRC.LICON_SZ:
            continue

        # LICON contacts — use wider pitch (0.60 um) to ensure LI1 spacing
        # between adjacent LI1 pads over LICONs meets li.3 rule (0.17 um min).
        # Standard LICON pitch (0.34) leaves only 0.17 um for LI1 pads of 0.33,
        # which is vulnerable to rounding errors.
        _GR_LICON_SP = 0.43  # pitch = 0.17 + 0.43 = 0.60 um
        via_array(cell, L.LICON, sx0, sy0, sx1, sy1,
                  DRC.LICON_SZ, _GR_LICON_SP)

        # MCON contacts (use same region, _fill_contacts handles centering)
        mcon_array(cell, sx0, sy0, sx1, sy1)

        # Port at segment midpoint on MET1
        px = (sx0 + sx1) / 2
        py = (sy0 + sy1) / 2
        pw = min(sw, sh)
        pkey = f"{port_name}_{seg_name}"
        ports[pkey] = Port(port_name, (px, py), pw, orient, L.MET1)

    # Canonical port at bottom-center
    ring_cy = (-tap_outer_hh + -tap_inner_hh) / 2
    ports[port_name] = Port(port_name, (0.0, ring_cy), ring_w, 270.0, L.MET1)

    return cell, ports


def guard_ring_p(lib: gdstk.Library, name: str,
                 inner_w: float, inner_h: float,
                 ring_w: float = 0.53) -> tuple[gdstk.Cell, dict[str, Port]]:
    """P+ substrate guard ring for NMOS isolation.

    TAP + PSDM + LICON + LI1 + MCON + MET1 ring. No N-well.
    Connects to VSS (substrate).

    Args:
        lib:     gdstk Library.
        name:    Cell name.
        inner_w: Inner opening width (microns).
        inner_h: Inner opening height (microns).
        ring_w:  Ring trace width (default 0.53 um).

    Returns:
        (cell, ports) with "VSS" and per-segment "VSS_bot" etc. ports on MET1.
    """
    return _guard_ring(lib, name, inner_w, inner_h, ring_w,
                       imp_layer=L.PSDM, nwell=False, port_name="VSS")


def guard_ring_n(lib: gdstk.Library, name: str,
                 inner_w: float, inner_h: float,
                 ring_w: float = 0.53) -> tuple[gdstk.Cell, dict[str, Port]]:
    """N+ well-contact guard ring for PMOS isolation.

    NWELL + TAP + NSDM + LICON + LI1 + MCON + MET1 ring.
    Connects to VDD (N-well).

    Args:
        lib:     gdstk Library.
        name:    Cell name.
        inner_w: Inner opening width (microns).
        inner_h: Inner opening height (microns).
        ring_w:  Ring trace width (default 0.53 um).

    Returns:
        (cell, ports) with "VDD" and per-segment "VDD_bot" etc. ports on MET1.
    """
    return _guard_ring(lib, name, inner_w, inner_h, ring_w,
                       imp_layer=L.NSDM, nwell=True, port_name="VDD")
