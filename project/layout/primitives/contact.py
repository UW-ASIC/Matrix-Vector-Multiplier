"""Contact and via array generators for Sky130.

Provides functions to fill rectangular regions with contacts/vias,
and a via_stack builder that creates the full interconnect between
any two metals in the stack (LI1 through MET5).
"""

import math
import gdstk
from ..layers import L, ld
from ..drc import DRC


# ---------------------------------------------------------------------------
# Metal stack descriptor
# ---------------------------------------------------------------------------
# Each entry describes one metal level and the via connecting it to adjacent
# levels.  The list is ordered LI1 (idx 0) through MET5 (idx 5).
#
# Keys:
#   metal       - drawing layer tuple
#   via_above   - via layer connecting this metal to the one above
#   via_above_sz/sp - via size and spacing for via_above
#   encl_above  - this metal's minimum enclosure of via_above
#   via_below   - via layer connecting this metal to the one below
#   via_below_sz/sp - via size and spacing for via_below
#   encl_below  - this metal's minimum enclosure of via_below
# ---------------------------------------------------------------------------

_STACK = [
    # idx 0: LI1
    {
        "metal": L.LI1,
        "via_above": L.MCON,
        "via_above_sz": DRC.MCON_SZ,
        "via_above_sp": DRC.MCON_SP,
        "encl_above": DRC.LI1_ENCL_LICON,
    },
    # idx 1: MET1
    {
        "metal": L.MET1,
        "via_below": L.MCON,
        "via_below_sz": DRC.MCON_SZ,
        "via_below_sp": DRC.MCON_SP,
        "encl_below": DRC.MCON_ENCL_MET1_WIDE,
        "via_above": L.VIA,
        "via_above_sz": DRC.VIA_SZ,
        "via_above_sp": DRC.VIA_SP,
        "encl_above": DRC.VIA_ENCL_MET1,
    },
    # idx 2: MET2
    {
        "metal": L.MET2,
        "via_below": L.VIA,
        "via_below_sz": DRC.VIA_SZ,
        "via_below_sp": DRC.VIA_SP,
        "encl_below": DRC.VIA_ENCL_MET2,
        "via_above": L.VIA2,
        "via_above_sz": DRC.VIA2_SZ,
        "via_above_sp": DRC.VIA2_SP,
        "encl_above": DRC.VIA2_ENCL_MET2,
    },
    # idx 3: MET3
    {
        "metal": L.MET3,
        "via_below": L.VIA2,
        "via_below_sz": DRC.VIA2_SZ,
        "via_below_sp": DRC.VIA2_SP,
        "encl_below": DRC.VIA2_ENCL_MET3,
        "via_above": L.VIA3,
        "via_above_sz": DRC.VIA3_SZ,
        "via_above_sp": DRC.VIA3_SP,
        "encl_above": DRC.VIA3_ENCL_MET3,
    },
    # idx 4: MET4
    {
        "metal": L.MET4,
        "via_below": L.VIA3,
        "via_below_sz": DRC.VIA3_SZ,
        "via_below_sp": DRC.VIA3_SP,
        "encl_below": DRC.VIA3_ENCL_MET4,
        "via_above": L.VIA4,
        "via_above_sz": DRC.VIA4_SZ,
        "via_above_sp": DRC.VIA4_SP,
        "encl_above": DRC.VIA4_ENCL_MET4,
    },
    # idx 5: MET5
    {
        "metal": L.MET5,
        "via_below": L.VIA4,
        "via_below_sz": DRC.VIA4_SZ,
        "via_below_sp": DRC.VIA4_SP,
        "encl_below": DRC.VIA4_ENCL_MET5,
    },
]

# Map drawing-layer tuple to stack index for fast lookup.
_METAL_IDX = {entry["metal"]: i for i, entry in enumerate(_STACK)}


# ---------------------------------------------------------------------------
# Internal: fill a rectangle with contacts
# ---------------------------------------------------------------------------

def _fill_contacts(cell: gdstk.Cell, x0: float, y0: float, x1: float, y1: float,
                   via_layer: tuple[int, int], via_sz: float, via_sp: float) -> int:
    """Fill a rectangular region with square contacts/vias, centered.

    Returns the number of contacts placed.
    """
    rx0, rx1 = min(x0, x1), max(x0, x1)
    ry0, ry1 = min(y0, y1), max(y0, y1)
    region_w = rx1 - rx0
    region_h = ry1 - ry0

    if region_w < via_sz or region_h < via_sz:
        return 0

    pitch = via_sz + via_sp
    nx = max(1, int(math.floor((region_w - via_sz) / pitch)) + 1)
    ny = max(1, int(math.floor((region_h - via_sz) / pitch)) + 1)

    array_w = (nx - 1) * pitch + via_sz
    array_h = (ny - 1) * pitch + via_sz

    # Center the array in the region
    ox = rx0 + (region_w - array_w) / 2
    oy = ry0 + (region_h - array_h) / 2

    count = 0
    for ix in range(nx):
        for iy in range(ny):
            cx = ox + ix * pitch
            cy = oy + iy * pitch
            cell.add(gdstk.rectangle(
                (cx, cy), (cx + via_sz, cy + via_sz),
                **ld(via_layer),
            ))
            count += 1
    return count


# ---------------------------------------------------------------------------
# Public API: specific contact types
# ---------------------------------------------------------------------------

def licon_array(cell: gdstk.Cell, x0: float, y0: float,
                x1: float, y1: float) -> int:
    """Fill a region with LICON contacts (0.17 x 0.17 um, 0.17 um spacing).

    Args:
        cell:       Target cell.
        x0, y0:     One corner of the fill region.
        x1, y1:     Opposite corner.

    Returns:
        Number of contacts placed.
    """
    return _fill_contacts(cell, x0, y0, x1, y1, L.LICON, DRC.LICON_SZ, DRC.LICON_SP)


def mcon_array(cell: gdstk.Cell, x0: float, y0: float,
               x1: float, y1: float) -> int:
    """Fill a region with MCON contacts (0.17 x 0.17 um, 0.19 um spacing).

    Args:
        cell:       Target cell.
        x0, y0:     One corner of the fill region.
        x1, y1:     Opposite corner.

    Returns:
        Number of contacts placed.
    """
    return _fill_contacts(cell, x0, y0, x1, y1, L.MCON, DRC.MCON_SZ, DRC.MCON_SP)


def via_array(cell: gdstk.Cell, via_layer: tuple[int, int],
              x0: float, y0: float, x1: float, y1: float,
              via_sz: float, via_sp: float) -> int:
    """Fill a rectangular region with vias of arbitrary layer/size/spacing.

    This is the generic form. For LICON and MCON use the dedicated helpers.

    Returns:
        Number of vias placed.
    """
    return _fill_contacts(cell, x0, y0, x1, y1, via_layer, via_sz, via_sp)


# ---------------------------------------------------------------------------
# Via stack builder
# ---------------------------------------------------------------------------

def via_stack(cell: gdstk.Cell, center: tuple[float, float],
              from_metal: tuple[int, int], to_metal: tuple[int, int],
              width: float | None = None) -> None:
    """Build a complete via stack between two metal layers.

    Creates all intermediate vias and their required landing pads from
    *from_metal* up (or down) to *to_metal*.  Handles the full LI1-to-MET5
    range.

    Args:
        cell:       Target gdstk.Cell.
        center:     (x, y) center of the stack in microns.
        from_metal: Lower metal layer, e.g. L.LI1.
        to_metal:   Upper metal layer, e.g. L.MET2.
        width:      Landing-pad width.  If None, auto-sized to minimum
                    enclosure around a single via at each transition.
    """
    idx_lo = _METAL_IDX.get(from_metal)
    idx_hi = _METAL_IDX.get(to_metal)
    if idx_lo is None:
        raise ValueError(f"from_metal {from_metal} is not in the metal stack")
    if idx_hi is None:
        raise ValueError(f"to_metal {to_metal} is not in the metal stack")
    if idx_lo == idx_hi:
        return
    if idx_lo > idx_hi:
        idx_lo, idx_hi = idx_hi, idx_lo

    cx, cy = center

    for i in range(idx_lo, idx_hi):
        lower = _STACK[i]
        upper = _STACK[i + 1]

        via_layer = upper["via_below"]
        via_sz = upper["via_below_sz"]

        # Each metal has an enclosure requirement for this via
        encl_lo = lower.get("encl_above", 0.0)
        encl_hi = upper["encl_below"]
        max_encl = max(encl_lo, encl_hi)

        # Minimum pad size to enclose one via
        min_pad = via_sz + 2 * max_encl
        pad = max(min_pad, width) if width is not None else min_pad

        half_pad = pad / 2
        half_via = via_sz / 2

        # Lower metal landing pad
        cell.add(gdstk.rectangle(
            (cx - half_pad, cy - half_pad),
            (cx + half_pad, cy + half_pad),
            **ld(lower["metal"]),
        ))

        # Via cut
        cell.add(gdstk.rectangle(
            (cx - half_via, cy - half_via),
            (cx + half_via, cy + half_via),
            **ld(via_layer),
        ))

        # Upper metal landing pad
        cell.add(gdstk.rectangle(
            (cx - half_pad, cy - half_pad),
            (cx + half_pad, cy + half_pad),
            **ld(upper["metal"]),
        ))
