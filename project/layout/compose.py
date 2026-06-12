"""Cell composition utilities: Instance placement and abutment.

Provides Instance (a placed cell reference with tracked ports) and helpers
for common placement patterns (abut_x, stack_y).
"""

import math
import gdstk
from .ports import Port, transform_ports


class Instance:
    """A placed cell reference with tracked ports.

    Wraps a gdstk.Cell and its port dictionary so that placement transforms
    are automatically applied to port positions.
    """

    def __init__(self, cell: gdstk.Cell, ports: dict[str, Port], name: str = ""):
        self.cell = cell
        self._orig_ports = dict(ports)
        self.ports = dict(ports)
        self.name = name or cell.name
        self.ref: gdstk.Reference | None = None
        self.origin = (0.0, 0.0)

    def place(self, x: float, y: float, rotation: float = 0,
              mirror_x: bool = False) -> "Instance":
        """Place the instance at (x, y) with optional rotation/mirror.

        Args:
            x, y:      Origin in microns.
            rotation:  Counter-clockwise rotation in degrees.
            mirror_x:  If True, reflect across the X axis before rotation.

        Returns:
            self, for chaining.
        """
        self.origin = (x, y)
        self.ports = transform_ports(self._orig_ports, x, y, rotation, mirror_x)
        self.ref = gdstk.Reference(
            self.cell,
            origin=(x, y),
            rotation=math.radians(rotation),
            x_reflection=mirror_x,
        )
        return self

    def add_to(self, parent: gdstk.Cell) -> "Instance":
        """Add this instance's reference to a parent cell.

        If place() has not been called, adds at the origin with no transform.

        Returns:
            self, for chaining.
        """
        if self.ref is None:
            self.ref = gdstk.Reference(self.cell)
        parent.add(self.ref)
        return self

    def port(self, name: str) -> Port:
        """Look up a port by name. Raises KeyError if not found."""
        return self.ports[name]

    def bbox(self) -> tuple[tuple[float, float], tuple[float, float]]:
        """Return ((x_min, y_min), (x_max, y_max)) bounding box."""
        if self.ref is not None:
            bb = self.ref.bounding_box()
        else:
            bb = self.cell.bounding_box()
        if bb is None:
            return ((0.0, 0.0), (0.0, 0.0))
        return ((float(bb[0][0]), float(bb[0][1])),
                (float(bb[1][0]), float(bb[1][1])))


def abut_x(a: Instance, b: Instance, gap: float = 0) -> float:
    """Place instance *b* immediately to the right of instance *a*.

    Uses bounding boxes: b's left edge aligns with a's right edge + gap.
    b is placed at the same y as a.

    Args:
        a:   Already-placed instance (left).
        b:   Instance to place (right).
        gap: Extra horizontal spacing in microns.

    Returns:
        The x origin assigned to b.
    """
    bb_a = a.bbox()
    bb_b_cell = b.cell.bounding_box()
    if bb_b_cell is None:
        b.place(bb_a[1][0] + gap, a.origin[1])
        return bb_a[1][0] + gap
    x = bb_a[1][0] + gap - float(bb_b_cell[0][0])
    b.place(x, a.origin[1])
    return x


def stack_y(bottom: Instance, top: Instance, gap: float = 0) -> float:
    """Place instance *top* directly above instance *bottom*.

    Uses bounding boxes: top's bottom edge aligns with bottom's top edge + gap.
    top is placed at the same x as bottom.

    Args:
        bottom: Already-placed instance (lower).
        top:    Instance to place (upper).
        gap:    Extra vertical spacing in microns.

    Returns:
        The y origin assigned to top.
    """
    bb_bot = bottom.bbox()
    bb_top_cell = top.cell.bounding_box()
    if bb_top_cell is None:
        top.place(bottom.origin[0], bb_bot[1][1] + gap)
        return bb_bot[1][1] + gap
    y = bb_bot[1][1] + gap - float(bb_top_cell[0][1])
    top.place(bottom.origin[0], y)
    return y
