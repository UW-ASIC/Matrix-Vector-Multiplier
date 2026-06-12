"""Routing primitives for Sky130 layout.

Provides straight, L-shaped, U-shaped, and bus routing functions,
plus a ground-shield trace generator. All routes are drawn as
rectangular metal segments (Manhattan geometry).
"""

import gdstk
from ..layers import L, ld
from ..drc import DRC
from ..ports import Port
from ..primitives.contact import via_stack


# ---------------------------------------------------------------------------
# Minimum widths per metal layer (for auto-width)
# ---------------------------------------------------------------------------
_MIN_WIDTH = {
    L.LI1: DRC.LI1_W,
    L.MET1: DRC.MET1_W,
    L.MET2: DRC.MET2_W,
    L.MET3: DRC.MET3_W,
    L.MET4: DRC.MET4_W,
    L.MET5: DRC.MET5_W,
}

# Minimum area per metal layer (um^2).  Layers without an area rule use 0.
_MIN_AREA = {
    L.LI1: 0.0,
    L.MET1: DRC.MET1_AREA,
    L.MET2: DRC.MET2_AREA,
    L.MET3: 0.0,
    L.MET4: 0.0,
    L.MET5: 0.0,
}


def _xy(p) -> tuple[float, float]:
    """Extract (x, y) from a Port or (x, y) tuple."""
    if isinstance(p, Port):
        return p.center
    return (float(p[0]), float(p[1]))


def _layer(p) -> tuple[int, int]:
    """Extract metal layer from a Port, defaulting to MET1."""
    if isinstance(p, Port):
        return p.layer
    return L.MET1


def _resolve_width(p1, p2, width: float | None, layer: tuple[int, int] | None = None) -> float:
    """Determine wire width from explicit value, port, or DRC minimum.

    Ensures the returned width is at least the DRC minimum for the layer.
    """
    if width is not None:
        w = width
    elif isinstance(p1, Port):
        w = p1.width
    elif isinstance(p2, Port):
        w = p2.width
    else:
        w = DRC.MET1_W

    # Enforce minimum width for the target layer
    lay = layer if layer is not None else _resolve_layer(p1, p2)
    min_w = _MIN_WIDTH.get(lay, DRC.MET1_W)
    return max(w, min_w)


def _resolve_layer(p1, p2) -> tuple[int, int]:
    """Determine metal layer from ports (must agree, or use p1)."""
    l1 = _layer(p1)
    l2 = _layer(p2)
    if l1 == l2:
        return l1
    # Different layers: use the lower one for the wire, caller should add via
    return l1


def _draw_wire(cell: gdstk.Cell, x1: float, y1: float,
               x2: float, y2: float, layer: tuple[int, int],
               width: float) -> None:
    """Draw a single rectangular wire segment between two points.

    The wire has the given *width* perpendicular to the direction of travel.
    It spans exactly from (x1,y1) to (x2,y2) with no endpoint extension.
    If the resulting rectangle would violate the minimum-area rule for
    *layer*, it is expanded symmetrically along its length to meet the rule.
    """
    hw = width / 2
    if abs(x1 - x2) < 0.001:
        # Vertical wire
        lo_y = min(y1, y2)
        hi_y = max(y1, y2)
        rect_w = width
        rect_h = hi_y - lo_y
        # Enforce minimum area by expanding length if needed
        min_area = _MIN_AREA.get(layer, 0.0)
        if min_area > 0 and rect_w * rect_h < min_area:
            needed_h = min_area / rect_w
            expand = (needed_h - rect_h) / 2
            lo_y -= expand
            hi_y += expand
        cell.add(gdstk.rectangle(
            (x1 - hw, lo_y),
            (x1 + hw, hi_y),
            **ld(layer),
        ))
    elif abs(y1 - y2) < 0.001:
        # Horizontal wire
        lo_x = min(x1, x2)
        hi_x = max(x1, x2)
        rect_w = hi_x - lo_x
        rect_h = width
        # Enforce minimum area by expanding length if needed
        min_area = _MIN_AREA.get(layer, 0.0)
        if min_area > 0 and rect_w * rect_h < min_area:
            needed_w = min_area / rect_h
            expand = (needed_w - rect_w) / 2
            lo_x -= expand
            hi_x += expand
        cell.add(gdstk.rectangle(
            (lo_x, y1 - hw),
            (hi_x, y1 + hw),
            **ld(layer),
        ))
    else:
        # General (bounding box) — rare, for non-Manhattan
        cell.add(gdstk.rectangle(
            (min(x1, x2) - hw, min(y1, y2) - hw),
            (max(x1, x2) + hw, max(y1, y2) + hw),
            **ld(layer),
        ))


def _draw_bend(cell: gdstk.Cell, cx: float, cy: float,
               layer: tuple[int, int], width: float) -> None:
    """Draw a square metal patch at a bend point to fill the corner.

    Without this, two perpendicular wire segments meeting at a point
    would leave a notch at their junction.
    """
    hw = width / 2
    cell.add(gdstk.rectangle(
        (cx - hw, cy - hw),
        (cx + hw, cy + hw),
        **ld(layer),
    ))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def route_straight(cell: gdstk.Cell, p1, p2,
                   width: float | None = None,
                   layer: tuple[int, int] | None = None) -> None:
    """Draw a straight metal wire between two points.

    Args:
        cell:   Target cell.
        p1, p2: Endpoints -- Port objects or (x, y) tuples.
        width:  Wire width in microns. If None, uses port width or DRC min.
        layer:  Metal layer. If None, inferred from ports.
    """
    x1, y1 = _xy(p1)
    x2, y2 = _xy(p2)
    lay = layer if layer is not None else _resolve_layer(p1, p2)
    w = _resolve_width(p1, p2, width, lay)
    _draw_wire(cell, x1, y1, x2, y2, lay, w)


def route_L(cell: gdstk.Cell, p1, p2,
            width: float | None = None,
            h_first: bool = True,
            layer: tuple[int, int] | None = None) -> None:
    """Draw an L-shaped (one-bend Manhattan) route between two points.

    Args:
        cell:     Target cell.
        p1, p2:   Endpoints.
        width:    Wire width.
        h_first:  If True, goes horizontal first then vertical.
                  If False, vertical first then horizontal.
        layer:    Metal layer. If None, inferred from ports.
    """
    x1, y1 = _xy(p1)
    x2, y2 = _xy(p2)
    lay = layer if layer is not None else _resolve_layer(p1, p2)
    w = _resolve_width(p1, p2, width, lay)

    if h_first:
        bend_x, bend_y = x2, y1
        _draw_wire(cell, x1, y1, x2, y1, lay, w)
        _draw_wire(cell, x2, y1, x2, y2, lay, w)
    else:
        bend_x, bend_y = x1, y2
        _draw_wire(cell, x1, y1, x1, y2, lay, w)
        _draw_wire(cell, x1, y2, x2, y2, lay, w)

    # Fill the corner at the bend so there is no notch
    _draw_bend(cell, bend_x, bend_y, lay, w)

    # If ports are on different metal layers, insert a via at the bend
    l1 = _layer(p1)
    l2 = _layer(p2)
    if l1 != l2:
        # Draw both metal landing pads sized for via enclosure
        via_stack(cell, (bend_x, bend_y), l1, l2, width=w)
        # Also draw the second-layer wire segment from bend to endpoint
        if h_first:
            _draw_wire(cell, bend_x, bend_y, x2, y2, l2, w)
        else:
            _draw_wire(cell, bend_x, bend_y, x2, y2, l2, w)


def route_U(cell: gdstk.Cell, p1, p2,
            width: float | None = None,
            offset: float = 0,
            layer: tuple[int, int] | None = None) -> None:
    """Draw a U-shaped (two-bend) route between two points.

    The route extends beyond both endpoints by *offset* before connecting.
    Useful for routing around obstacles.

    If both ports face the same direction (e.g. both south), the U goes
    in that direction. The offset is added in the port-facing direction.

    Args:
        cell:   Target cell.
        p1, p2: Endpoints.
        width:  Wire width.
        offset: How far the U extends beyond the ports (microns).
        layer:  Metal layer.
    """
    x1, y1 = _xy(p1)
    x2, y2 = _xy(p2)
    lay = layer if layer is not None else _resolve_layer(p1, p2)
    w = _resolve_width(p1, p2, width, lay)

    # Determine the U direction from port orientations
    orient = 270.0  # default: U goes south
    if isinstance(p1, Port):
        orient = p1.orientation

    if orient == 270.0 or orient == 90.0:
        # Vertical U: extend in y, connect horizontally
        if orient == 270.0:
            ext_y = min(y1, y2) - offset - w
        else:
            ext_y = max(y1, y2) + offset + w
        _draw_wire(cell, x1, y1, x1, ext_y, lay, w)
        _draw_wire(cell, x1, ext_y, x2, ext_y, lay, w)
        _draw_wire(cell, x2, ext_y, x2, y2, lay, w)
        # Fill both bend corners
        _draw_bend(cell, x1, ext_y, lay, w)
        _draw_bend(cell, x2, ext_y, lay, w)
    else:
        # Horizontal U: extend in x, connect vertically
        if orient == 180.0:
            ext_x = min(x1, x2) - offset - w
        else:
            ext_x = max(x1, x2) + offset + w
        _draw_wire(cell, x1, y1, ext_x, y1, lay, w)
        _draw_wire(cell, ext_x, y1, ext_x, y2, lay, w)
        _draw_wire(cell, ext_x, y2, x2, y2, lay, w)
        # Fill both bend corners
        _draw_bend(cell, ext_x, y1, lay, w)
        _draw_bend(cell, ext_x, y2, lay, w)


def route_bus(cell: gdstk.Cell, ports_a: list, ports_b: list,
              width: float | None = None,
              layer: tuple[int, int] | None = None) -> None:
    """Route parallel L-shaped connections between two port lists.

    ports_a[i] is connected to ports_b[i] for each i. Both lists must
    have the same length.

    Args:
        cell:     Target cell.
        ports_a:  Source ports (or (x,y) tuples).
        ports_b:  Destination ports (or (x,y) tuples).
        width:    Wire width (same for all routes).
        layer:    Metal layer (same for all routes).
    """
    if len(ports_a) != len(ports_b):
        raise ValueError(
            f"Port lists must have equal length: {len(ports_a)} vs {len(ports_b)}"
        )
    for pa, pb in zip(ports_a, ports_b):
        route_L(cell, pa, pb, width=width, layer=layer)


def add_shield(cell: gdstk.Cell, y: float, x0: float, x1: float,
               layer: tuple[int, int] = L.MET2,
               width: float = 0.30) -> None:
    """Add a horizontal grounded shield trace.

    Draws a horizontal metal wire at y from x0 to x1. Typically used
    between sensitive analog signals to reduce coupling.

    Args:
        cell:   Target cell.
        y:      Y coordinate of the shield trace center.
        x0:     Left x coordinate.
        x1:     Right x coordinate.
        layer:  Metal layer for the shield (default MET2).
        width:  Trace width in microns (default 0.30).
    """
    # Enforce minimum width for the shield layer
    min_w = _MIN_WIDTH.get(layer, DRC.MET1_W)
    w = max(width, min_w)
    hw = w / 2
    cell.add(gdstk.rectangle(
        (min(x0, x1), y - hw),
        (max(x0, x1), y + hw),
        **ld(layer),
    ))
