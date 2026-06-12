"""Port abstraction for layout cells.

Ports carry a name, physical center, width, orientation, and metal layer.
They are the primary interface for connecting cells during composition.
"""

from dataclasses import dataclass
import math
import gdstk
from .layers import L


@dataclass(frozen=True)
class Port:
    """A named electrical port on a layout cell.

    Attributes:
        name:        Net name (e.g. "S", "D", "G", "VDD").
        center:      (x, y) in microns.
        width:       Port width in microns (used for pin rectangle and route width).
        orientation: Direction the port faces, in degrees.
                     0 = east, 90 = north, 180 = west, 270 = south.
        layer:       Drawing layer as (gds_layer, datatype) tuple.
    """
    name: str
    center: tuple[float, float]
    width: float
    orientation: float
    layer: tuple[int, int]


def transform_port(p: Port, dx: float = 0.0, dy: float = 0.0,
                   rotation: float = 0.0, mirror_x: bool = False) -> Port:
    """Transform a port's position and orientation.

    Args:
        p:        Source port.
        dx, dy:   Translation after rotation/mirror.
        rotation: Counter-clockwise rotation in degrees.
        mirror_x: If True, flip the Y coordinate before rotation.

    Returns:
        A new Port with transformed center and orientation.
    """
    x, y = p.center
    if mirror_x:
        y = -y
    rad = math.radians(rotation)
    cos_r = math.cos(rad)
    sin_r = math.sin(rad)
    rx = x * cos_r - y * sin_r + dx
    ry = x * sin_r + y * cos_r + dy
    orient = ((-p.orientation if mirror_x else p.orientation) + rotation) % 360
    return Port(p.name, (rx, ry), p.width, orient, p.layer)


def transform_ports(ports: dict[str, Port], dx: float = 0.0, dy: float = 0.0,
                    rotation: float = 0.0, mirror_x: bool = False) -> dict[str, Port]:
    """Transform every port in a dictionary."""
    return {k: transform_port(v, dx, dy, rotation, mirror_x) for k, v in ports.items()}


def add_port_label(cell: gdstk.Cell, port: Port) -> None:
    """Add a pin rectangle and text label at a port location.

    The pin and label layers are derived from the port's drawing layer
    using the standard Sky130 datatype mapping (pin=16, label=5).
    """
    try:
        idx = L.METALS.index(port.layer)
    except ValueError:
        raise ValueError(
            f"Port '{port.name}' layer {port.layer} is not in L.METALS; "
            f"cannot determine pin/label layers."
        )
    pin_l = L.PINS[idx]
    lbl_l = L.LABELS[idx]
    hw = port.width / 2
    x, y = port.center
    cell.add(gdstk.rectangle(
        (x - hw, y - hw), (x + hw, y + hw),
        layer=pin_l[0], datatype=pin_l[1],
    ))
    cell.add(gdstk.Label(
        port.name, (x, y),
        anchor="o",
        layer=lbl_l[0], texttype=lbl_l[1],
    ))
