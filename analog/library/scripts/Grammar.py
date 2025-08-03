from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Union

class ObjectType(Enum):
    VERSION = 'Version'
    LINE = 'Line'
    RECTANGLE = 'Rectangle'
    ARC = 'Arc'
    TEXT = 'Text'
    POLYGON = 'Polygon'
    WIRE = 'Wire'
    COMPONENT = 'Component'
    SPICE = 'Spice'
    VERILOG = 'Verilog'
    VHDL = 'VHDL'
    TEDAX = 'TEDAx'
    GLOBAL_PROPERTIES = 'GlobalProperties'
    EMBEDDED_SYMBOL = 'EmbeddedSymbol'

@dataclass
class CoordinatePair:
    """Coordinate pair for polygons"""
    x: float
    y: float

@dataclass
class XSchemObject:
    """Base class for all XSchem objects"""
    # Note: Not all objects have properties according to the PEG
    pass

@dataclass
class Version(XSchemObject):
    """Version object containing XSchem version info"""
    version: str = ""
    fileVersion: str = ""
    license: str = ""
    type: str = field(default="Version", init=False)

@dataclass
class Line(XSchemObject):
    """Line object: L layer x1 y1 x2 y2 properties"""
    layer: int = 0
    x1: float = 0.0
    y1: float = 0.0
    x2: float = 0.0
    y2: float = 0.0
    properties: Dict[str, str] = field(default_factory=dict)
    type: str = field(default="Line", init=False)

@dataclass
class Rectangle(XSchemObject):
    """Rectangle object: B layer x1 y1 x2 y2 properties"""
    layer: int = 0
    x1: float = 0.0
    y1: float = 0.0
    x2: float = 0.0
    y2: float = 0.0
    properties: Dict[str, str] = field(default_factory=dict)
    type: str = field(default="Rectangle", init=False)

@dataclass
class Arc(XSchemObject):
    """Arc object: A layer centerX centerY radius startAngle sweepAngle properties"""
    layer: int = 0
    centerX: float = 0.0
    centerY: float = 0.0
    radius: float = 0.0
    startAngle: float = 0.0
    sweepAngle: float = 0.0
    properties: Dict[str, str] = field(default_factory=dict)
    type: str = field(default="Arc", init=False)

@dataclass
class Polygon(XSchemObject):
    """Polygon object: P layer pointCount points properties"""
    layer: int = 0
    # Note: pointCount is derived from len(points) according to PEG
    points: List[CoordinatePair] = field(default_factory=list)
    properties: Dict[str, str] = field(default_factory=dict)
    type: str = field(default="Polygon", init=False)
    
    @property
    def pointCount(self) -> int:
        """Point count is derived from the points list"""
        return len(self.points)

@dataclass
class Text(XSchemObject):
    """Text object: T {text} x y rotation mirror hSize vSize properties"""
    text: str = ""
    x: float = 0.0
    y: float = 0.0
    rotation: int = 0
    mirror: int = 0
    hSize: float = 1.0
    vSize: float = 1.0
    properties: Dict[str, str] = field(default_factory=dict)
    type: str = field(default="Text", init=False)

@dataclass
class Wire(XSchemObject):
    """Wire object: N x1 y1 x2 y2 properties"""
    x1: float = 0.0
    y1: float = 0.0
    x2: float = 0.0
    y2: float = 0.0
    properties: Dict[str, str] = field(default_factory=dict)
    type: str = field(default="Wire", init=False)

@dataclass
class Component(XSchemObject):
    """Component object: C {reference} x y rotation flip properties"""
    symbolReference: str = ""
    x: float = 0.0
    y: float = 0.0
    rotation: int = 0
    flip: int = 0
    properties: Dict[str, str] = field(default_factory=dict)
    type: str = field(default="Component", init=False)

@dataclass
class Spice(XSchemObject):
    """SPICE global content: S {content}"""
    content: str = ""
    type: str = field(default="Spice", init=False)

@dataclass
class Verilog(XSchemObject):
    """Verilog global content: V {content}"""
    content: str = ""
    type: str = field(default="Verilog", init=False)

@dataclass
class VHDL(XSchemObject):
    """VHDL global content: G {content}"""
    content: str = ""
    type: str = field(default="VHDL", init=False)

@dataclass
class TEDAx(XSchemObject):
    """TEDAx global content: E {content}"""
    content: str = ""
    type: str = field(default="TEDAx", init=False)

@dataclass
class GlobalProperties(XSchemObject):
    """Global properties: K properties"""
    properties: Dict[str, str] = field(default_factory=dict)
    type: str = field(default="GlobalProperties", init=False)

@dataclass
class EmbeddedSymbol(XSchemObject):
    """Embedded symbol: [ symbol ]"""
    symbol: List[XSchemObject] = field(default_factory=list)
    type: str = field(default="EmbeddedSymbol", init=False)

# Type alias for any XSchem object
XSchemObjectType = Union[
    Version, Line, Rectangle, Arc, Polygon, Text, Wire, 
    Component, Spice, Verilog, VHDL, TEDAx, GlobalProperties, EmbeddedSymbol
]
