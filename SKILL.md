# Spout2 Python API Reference

Complete reference for the `spout` Python module — analog place-and-route via constraint-driven layout.

## Table of Contents

- [Overview](#overview)
- [Module Exports](#module-exports)
- [Pdk](#pdk)
- [Component](#component)
  - [Construction](#construction)
  - [SPICE Import](#spice-import)
  - [Device Addition](#device-addition)
  - [Connectivity](#connectivity)
  - [Constraints](#constraints)
  - [Raw Geometry](#raw-geometry)
  - [Layout Pipeline](#layout-pipeline)
  - [Verification](#verification)
  - [Export](#export)
  - [Visualization](#visualization)
  - [State Inspection](#state-inspection)
- [InstanceRef](#instanceref)
- [FingerRef](#fingerref)
- [PortRef](#portref)
- [Length](#length)
- [Point](#point)
- [Rect](#rect)
- [DrcViolation](#drcviolation)
- [LvsResult](#lvsresult)
- [PexResult](#pexresult)
- [PexR and PexC](#pexr-and-pexc)
- [Standalone GDS Functions](#standalone-gds-functions)
- [The @cell Decorator](#the-cell-decorator)
- [Constraint Vocabulary](#constraint-vocabulary)
- [Typestate Flow](#typestate-flow)
- [Units](#units)
- [Full Examples](#full-examples)

---

## Overview

Spout2 is a full Rust analog place-and-route engine exposed to Python via PyO3. The flow:

```
Add devices → Wire nets → Declare constraints → place() → route() → verify → export
```

All positioning is **constraint-driven** — you declare relationships (above, symmetric, aligned) and the solver computes coordinates. No manual XY placement needed (though an escape hatch exists via `add_rect`).

```python
import spout

pdk = spout.Pdk.sky130()
c = spout.Component(pdk)
mn = c.add_nmos(500, 180)
mp = c.add_pmos(1000, 180)
c.above(mp, mn)
# ... wire, constrain, place, route, export
```

---

## Module Exports

```python
import spout

spout.__version__   # str, e.g. "0.9.0"

# Classes
spout.Pdk
spout.Component
spout.InstanceRef
spout.FingerRef
spout.PortRef
spout.Length
spout.Point
spout.Rect
spout.DrcViolation
spout.LvsResult
spout.PexResult
spout.PexR
spout.PexC

# Functions
spout.cell              # @cell decorator
spout.drc_from_gds()    # standalone DRC on GDS files
spout.lvs_from_gds()    # standalone LVS on GDS files
spout.pex_from_gds()    # standalone PEX on GDS files
```

---

## Pdk

Process Design Kit — loads layer definitions, design rules, and device parameters.

### `Pdk.sky130() -> Pdk`

Load the built-in Sky130 PDK preset. This is the primary constructor.

```python
pdk = spout.Pdk.sky130()
```

### `Pdk.from_json(json: str) -> Pdk`

Load a PDK from a JSON string. For custom or experimental PDKs.

```python
pdk = spout.Pdk.from_json('{"name": "custom", "layers": [...], ...}')
```

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `name`   | `str` | PDK name, e.g. `"sky130"` |

```python
pdk = spout.Pdk.sky130()
print(pdk.name)  # "sky130"
print(repr(pdk)) # Pdk(name='sky130')
```

---

## Component

The main circuit-building and layout flow object. Holds all devices, nets, constraints, and drives the place → route → verify → export pipeline.

### Construction

#### `Component(pdk: Pdk) -> Component`

Create a new empty component bound to a PDK. State starts as `"building"`.

```python
pdk = spout.Pdk.sky130()
c = spout.Component(pdk)
print(c.state())  # "building"
```

### SPICE Import

#### `Component.from_spice(path: str, pdk: Pdk) -> Component`

Build a component from a SPICE netlist file. Parses the file, extracts the **last** `.subckt` definition, constructs an unplaced Component with all devices wired. State starts as `"unplaced"`.

```python
c = spout.Component.from_spice("inverter.spice", pdk)
print(c.state())  # "unplaced"
c.place()
c.route()
```

Handles:
- Direct `M`/`R`/`C` device lines
- `X`-instances wrapping primitives (e.g. `xm0 ... nmos`)
- Model name classification (pmos/nmos variants)
- SPICE terminal order `[D, G, S, B]` remapped to Spout order `[G, D, S, B]`

#### `Component.codegen_from_spice(path: str) -> str`

Generate Python source code from a SPICE netlist. Returns a string containing a complete Python script that uses the `spout` API to construct the equivalent component.

```python
code = spout.Component.codegen_from_spice("ota.spice")
print(code)
# Outputs:
# """Auto-generated spout code for ota."""
# import spout
# def build_ota():
#     pdk = spout.Pdk.sky130()
#     c = spout.Component(pdk)
#     ...
```

Use this to bootstrap a layout script from an existing netlist, then add constraints manually.

---

### Device Addition

All dimensions are in **nanometers** (integer). All methods return an `InstanceRef`.

All device addition methods raise `RuntimeError` if called after `place()`.

#### `c.add_nmos(w: int, l: int, nf: int = 1) -> InstanceRef`

Add an NMOS transistor. Returns a reference with 4 terminals: `g` (gate), `d` (drain), `s` (source), `b` (bulk).

```python
mn = c.add_nmos(500, 180)       # W=500nm, L=180nm, 1 finger
mn4 = c.add_nmos(500, 180, 4)   # W=500nm, L=180nm, 4 fingers
```

#### `c.add_pmos(w: int, l: int, nf: int = 1) -> InstanceRef`

Add a PMOS transistor. Same terminal structure as NMOS.

```python
mp = c.add_pmos(1000, 180)
mp8 = c.add_pmos(2400, 180, nf=8)
```

#### `c.add_resistor(w: int, l: int) -> InstanceRef`

Add a resistor. Returns a reference with 2 terminals: `port(0)` = positive, `port(1)` = negative.

```python
r = c.add_resistor(330, 1000)  # W=330nm, L=1000nm
pos = r.port(0)
neg = r.port(1)
```

#### `c.add_capacitor(w: int, l: int) -> InstanceRef`

Add a capacitor. Returns a reference with 2 terminals: `port(0)` = bottom plate, `port(1)` = top plate.

```python
cap = c.add_capacitor(500, 500)  # W=500nm, L=500nm
bot = cap.port(0)
top = cap.port(1)
```

---

### Connectivity

All connectivity methods raise `RuntimeError` if called after `place()`.

#### `c.named_net(name: str) -> int`

Create a named net (e.g. for power rails) without connecting any ports. Returns the net ID (`u32`).

```python
vdd = c.named_net("VDD")
gnd = c.named_net("GND")
```

#### `c.connect(ports: list[PortRef]) -> int`

Connect all listed ports to the same net. If any port already belongs to a named net, all ports join that net. Otherwise a new anonymous net is created. Returns the net ID.

```python
inp = c.connect([mn.g, mp.g])     # gate of mn and mp share "inp" net
out = c.connect([mn.d, mp.d])     # drain of mn and mp share "out" net
```

#### `c.connect_to_net(net_id: int, ports: list[PortRef]) -> None`

Connect additional ports to an existing net (identified by ID from `named_net()` or `connect()`).

```python
c.connect_to_net(gnd, [mn.s, mn.b])  # source and bulk of mn to GND
c.connect_to_net(vdd, [mp.s, mp.b])  # source and bulk of mp to VDD
```

#### `c.add_port(name: str, net_id: int, direction: str) -> None`

Declare a boundary port — exposes a net as an external pin of the component.

`direction` accepts (case-insensitive):
- `"input"` or `"in"`
- `"output"` or `"out"`
- `"inout"`

```python
c.add_port("VDD", vdd, "inout")
c.add_port("GND", gnd, "inout")
c.add_port("IN", inp, "input")
c.add_port("OUT", out, "output")
```

---

### Constraints

Constraints are **declarative** — they register intent, nothing moves until `place()` is called. The constraint solver resolves all constraints simultaneously.

All constraint methods raise `RuntimeError` if called after `place()`.

#### Relative Positioning

##### `c.above(a: InstanceRef, b: InstanceRef) -> None`

Device `a` placed above device `b` (a's bottom edge ≥ b's top edge + routing space).

```python
c.above(mp, mn)  # PMOS above NMOS (standard CMOS layout)
```

##### `c.below(a: InstanceRef, b: InstanceRef) -> None`

Device `a` placed below device `b`. Equivalent to `c.above(b, a)`.

##### `c.left_of(a: InstanceRef, b: InstanceRef) -> None`

Device `a` placed to the left of device `b`.

##### `c.right_of(a: InstanceRef, b: InstanceRef) -> None`

Device `a` placed to the right of device `b`.

```python
c.left_of(m1, m2)   # m1 is left of m2
c.right_of(m3, m2)  # m3 is right of m2
```

#### Alignment

##### `c.align_row(devices: list[InstanceRef]) -> None`

Align all devices horizontally — all devices share the same Y coordinate (horizontal row).

```python
c.align_row([m1, m2, m3])  # all three on the same horizontal line
```

##### `c.align_col(devices: list[InstanceRef]) -> None`

Align all devices vertically — all devices share the same X coordinate (vertical column).

```python
c.align_col([mp, mn])  # PMOS and NMOS centers vertically aligned
```

#### Symmetry

##### `c.symmetric(a: InstanceRef, b: InstanceRef) -> None`

Symmetric pair: `a` and `b` placed mirror-symmetric about an axis.

```python
# Differential pair
mn_p = c.add_nmos(500, 180)
mn_n = c.add_nmos(500, 180)
c.symmetric(mn_p, mn_n)
```

##### `c.self_symmetric(a: InstanceRef) -> None`

Place device on the axis of symmetry itself. Used for tail current sources or bias devices.

```python
m_tail = c.add_nmos(1000, 180, nf=4)
c.self_symmetric(m_tail)
```

##### `c.common_centroid(devices: list[InstanceRef]) -> None`

Common-centroid placement for a group of devices — interleaved ABBA pattern for matching.

```python
c.common_centroid([m1, m2, m3, m4])  # ABBA interleaving
```

##### `c.interdigitate(devices: list[InstanceRef]) -> None`

Interdigitated placement — alternating ABAB pattern.

```python
c.interdigitate([m_a, m_b])
```

#### Matching and Ordering

##### `c.match_devices(a: InstanceRef, b: InstanceRef) -> None`

Force devices to use the same physical template (same orientation, same layout style).

```python
c.match_devices(mn1, mn2)  # identical layout for matching
```

##### `c.min_spacing(a: InstanceRef, b: InstanceRef, dist: int) -> None`

Minimum spacing between two devices. `dist` in nanometers.

```python
c.min_spacing(m_analog, m_digital, 5000)  # at least 5um gap
```

#### Isolation

##### `c.guard_ring(devices: list[InstanceRef], ring_type: str) -> None`

Insert a guard ring around a group of devices.

`ring_type` accepts (case-insensitive):
- `"substrate"`, `"sub"`, `"psub"`
- `"nwell"`, `"n-well"`, `"n_well"`
- `"deepnwell"`, `"deep_nwell"`, `"deep-nwell"`, `"dnw"`

```python
c.guard_ring([mn1, mn2], "substrate")    # p-sub guard ring around NMOS devices
c.guard_ring([mp1, mp2], "nwell")        # n-well guard ring around PMOS devices
c.guard_ring([m_sens], "deepnwell")      # deep n-well isolation
```

#### Net Constraints

##### `c.shield_net(net_id: int) -> None`

Shield a net with ground wires on adjacent routing tracks. For sensitive analog signals.

```python
c.shield_net(out)  # ground shields around output net wires
```

##### `c.match_length(net_a: int, net_b: int, tolerance_nm: int) -> None`

Match the routed wire length of two nets within a tolerance (nanometers).

```python
c.match_length(inp_p, inp_n, 50)  # differential inputs matched within 50nm
```

##### `c.net_class(net_id: int, class: str) -> None`

Assign a routing class to a net. Controls wire width, spacing, and layer selection.

`class` accepts (case-insensitive):
- `"signal"` or `"sig"` — default signal routing
- `"power"` or `"pwr"` or `"vdd"` — wider wires, power routing
- `"ground"` or `"gnd"` or `"vss"` — wider wires, ground routing
- `"clock"` or `"clk"` — shielded clock routing
- `"analog"` — high-quality analog routing

```python
c.net_class(vdd, "power")
c.net_class(gnd, "ground")
c.net_class(clk_net, "clock")
c.net_class(sens_net, "analog")
```

---

### Raw Geometry

Escape hatch for adding custom shapes directly.

#### `c.add_rect(layer: int, x1: int, y1: int, x2: int, y2: int) -> None`

Add a raw rectangle on a given layer. All coordinates in **nanometers**. Internally converted to 100pm units (multiplied by 10).

```python
c.add_rect(4, 0, 0, 1000, 500)  # layer 4, 1um x 0.5um rectangle
```

#### `c.add_rect_raw(layer: int, x1: Length, y1: Length, x2: Length, y2: Length) -> None`

Add a raw rectangle using `Length` objects for sub-nanometer precision.

```python
c.add_rect_raw(
    4,
    spout.Length.nm(0), spout.Length.nm(0),
    spout.Length.nm(1000), spout.Length.nm(500)
)
```

---

### Layout Pipeline

The layout flow is a strict state machine: `building → unplaced → placed → routed`.

#### `c.place() -> None`

Run placement — the constraint solver assigns device positions. Transitions state from `"building"` (or `"unplaced"`) to `"placed"`.

Must be called **after** all devices, connections, and constraints are declared. Cannot add devices or constraints after this call.

```python
c.place()
```

#### `c.route() -> None`

Run routing — the grid router assigns wires and vias for all nets. Transitions from `"placed"` to `"routed"`.

Must call `place()` first. Raises `RuntimeError` otherwise.

```python
c.route()
```

---

### Verification

All verification methods require `"routed"` state. They do **not** consume the component — you can call multiple checks and exports.

#### `c.check_drc() -> list[DrcViolation]`

Run design rule checking. Returns a list of `DrcViolation` objects. Empty list = clean.

```python
violations = c.check_drc()
if violations:
    for v in violations:
        print(f"DRC: {v.rule} on layer {v.layer}: {v.message}")
else:
    print("DRC clean!")
```

#### `c.check_lvs() -> LvsResult`

Run layout-vs-schematic comparison. Checks that routed layout matches the declared netlist.

```python
lvs = c.check_lvs()
print(f"LVS matches: {lvs.matches}")
if not lvs.matches:
    for msg in lvs.mismatch_messages():
        print(f"  Mismatch: {msg}")
```

#### `c.extract() -> PexResult`

Run parasitic extraction. Extracts parasitic R and C from the routed layout.

```python
pex = c.extract()
print(f"Parasitics: {pex.resistor_count} R, {pex.capacitor_count} C")
for r in pex.resistors:
    print(f"  R: {r.node_a} - {r.node_b} = {r.value_mohm} mohm")
for cap in pex.capacitors:
    print(f"  C: {cap.node_a} - {cap.node_b} = {cap.value_af} aF")
```

---

### Export

#### `c.export_gds(path: str) -> None`

Write the routed layout to a GDS-II file. Requires `"routed"` state.

```python
c.export_gds("inverter.gds")
```

#### `c.export_svg(path: str) -> None`

Write the routed layout to an SVG file for visualization. Requires `"routed"` state.

```python
c.export_svg("inverter.svg")
```

---

### Visualization

#### `c.show() -> str`

Render an SVG preview as a string. Works after `place()` **or** `route()`.

```python
svg_str = c.show()
# Write to file or display in notebook
with open("preview.svg", "w") as f:
    f.write(svg_str)
```

---

### State Inspection

#### `c.state() -> str`

Returns the current state as a string:
- `"building"` — devices/constraints being added (from `Component(pdk)`)
- `"unplaced"` — built from SPICE, ready for `place()`
- `"placed"` — placement done, ready for `route()`
- `"routed"` — routing done, ready for verify/export
- `"invalid"` — error state (should not occur)

```python
print(c.state())  # "building", "placed", "routed", etc.
print(repr(c))    # Component(state='building')
```

---

## InstanceRef

Reference to an instantiated device within a Component. Returned by `add_nmos()`, `add_pmos()`, `add_resistor()`, `add_capacitor()`.

### MOSFET Terminal Properties

| Property | Type | Port Index | Description |
|----------|------|------------|-------------|
| `g`      | `PortRef` | 0 | Gate terminal |
| `d`      | `PortRef` | 1 | Drain terminal |
| `s`      | `PortRef` | 2 | Source terminal |
| `b`      | `PortRef` | 3 | Bulk/substrate terminal |

All are Python properties (no parentheses needed):
```python
mn = c.add_nmos(500, 180)
gate_port = mn.g      # PortRef for gate
drain_port = mn.d     # PortRef for drain
```

### Generic Port Access

#### `inst.port(idx: int) -> PortRef`

Access terminal by index. For resistors/capacitors with 2 terminals, or for generic device access.

```python
r = c.add_resistor(330, 1000)
pos = r.port(0)   # positive terminal
neg = r.port(1)   # negative terminal

# For MOSFETs, .port(0) == .g, .port(1) == .d, etc.
```

### Multi-Finger Access

#### `inst.finger(idx: int) -> FingerRef`

Access a specific finger of a multi-finger device. `idx` must be `< inst.nf`. Raises `RuntimeError` if out of bounds.

```python
m8 = c.add_nmos(500, 180, nf=8)
f0 = m8.finger(0)  # first finger
f7 = m8.finger(7)  # last finger
```

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `num_terminals` | `int` | Number of terminals (4 for MOSFET, 2 for R/C) |
| `nf` | `int` | Number of fingers |
| `device_id` | `int` | Internal device ID (u32) |

```python
mn = c.add_nmos(500, 180, nf=4)
print(mn.num_terminals)  # 4
print(mn.nf)             # 4
print(mn.device_id)      # 0 (first device added)
print(repr(mn))          # InstanceRef(device_id=0, terminals=4, nf=4)
```

---

## FingerRef

Reference to a specific finger of a multi-finger device. Obtained from `InstanceRef.finger(idx)`.

### Terminal Properties

| Property | Type | Description |
|----------|------|-------------|
| `g`      | `PortRef` | Gate of this finger (shared with device gate) |
| `d`      | `PortRef` | Drain of this finger (shared with device drain) |
| `s`      | `PortRef` | Source of this finger (shared with device source) |

### Other Properties

| Property | Type | Description |
|----------|------|-------------|
| `device_id` | `int` | Parent device ID |
| `finger_idx` | `int` | Finger index within the device |

```python
m = c.add_nmos(500, 180, nf=4)
f2 = m.finger(2)
print(f2.device_id)    # same as m.device_id
print(f2.finger_idx)   # 2
print(repr(f2))        # FingerRef(device_id=0, finger_idx=2)
```

Note: In the current implementation, per-finger terminals map to the same device-level terminals. The finger distinction is handled during physical layout generation, not connectivity.

---

## PortRef

Reference to a specific port (terminal) of a device instance. Used in `connect()` and `connect_to_net()`.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `device_id` | `int` | Device this port belongs to |
| `port_idx`  | `int` | Terminal index within the device |

### Equality and Hashing

`PortRef` supports `==` and `hash()` — safe to use in sets and as dict keys.

```python
mn = c.add_nmos(500, 180)
p1 = mn.g
p2 = mn.g
print(p1 == p2)      # True
print(p1 == mn.d)    # False

# Usable in sets
ports = {mn.g, mn.d, mn.s, mn.b}
print(len(ports))    # 4
```

---

## Length

A length/distance value in Spout's internal 100pm units. Used with `add_rect_raw()` for sub-nanometer precision.

### Constructors

All constructors are static methods:

#### `Length.nm(val: int) -> Length`

Construct from nanometers. `1 nm = 10 internal units`.

```python
l = spout.Length.nm(180)
print(l.raw())   # 1800
```

#### `Length.um(val: float) -> Length`

Construct from micrometers. `1 um = 10000 internal units`.

```python
l = spout.Length.um(0.18)
print(l.raw())   # 1800
```

#### `Length.pm(val: int) -> Length`

Construct from picometers. `100 pm = 1 internal unit`.

```python
l = spout.Length.pm(700)
print(l.raw())   # 7
```

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `raw()` | `int` | Backing value in 100pm units |

### Equality and Hashing

Supports `==` and `hash()`.

```python
a = spout.Length.nm(180)
b = spout.Length.um(0.18)
print(a == b)  # True
```

---

## Point

A 2D point in global coordinates. Internal units are 100pm.

### Constructors

#### `Point(x: int, y: int) -> Point`

Create from raw 100pm coordinates.

```python
p = spout.Point(1800, 5000)
```

#### `Point.from_nm(x: int, y: int) -> Point`

Create from nanometer coordinates (multiplied by 10 internally).

```python
p = spout.Point.from_nm(180, 500)
print(p.x)  # 1800
print(p.y)  # 5000
```

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `x` | `int` | X coordinate in 100pm units |
| `y` | `int` | Y coordinate in 100pm units |

### Equality and Hashing

Supports `==` and `hash()`.

---

## Rect

An axis-aligned rectangle in global coordinates. Automatically normalized so `lo <= hi`.

### Constructor

#### `Rect(x1: int, y1: int, x2: int, y2: int) -> Rect`

Create from raw 100pm coordinates. Normalizes automatically.

```python
r = spout.Rect(0, 0, 1000, 2000)
# Also works with reversed corners:
r2 = spout.Rect(1000, 2000, 0, 0)  # normalized to same as above
```

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `x1` | `int` | Lower-left X (100pm units) |
| `y1` | `int` | Lower-left Y (100pm units) |
| `x2` | `int` | Upper-right X (100pm units) |
| `y2` | `int` | Upper-right Y (100pm units) |
| `width` | `int` | Width in 100pm units |
| `height` | `int` | Height in 100pm units |

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `area()` | `int` | Area in units² (i64 to avoid overflow) |
| `center()` | `Point` | Center point of rectangle |

```python
r = spout.Rect(0, 0, 100, 200)
print(r.width)    # 100
print(r.height)   # 200
print(r.area())   # 20000
c = r.center()
print(c.x, c.y)   # 50, 100
```

---

## DrcViolation

A single design rule check violation.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `rule` | `str` | Name of the violated rule |
| `message` | `str` | Human-readable violation description |
| `layer` | `int` | Layer number where violation occurs |
| `shape_a` | `int` | First shape index involved |
| `shape_b` | `int` | Second shape index involved |
| `location` | `tuple[int,int,int,int]` | Bounding box `(x1, y1, x2, y2)` |

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `to_json()` | `str` | Serialize violation to JSON |

```python
violations = c.check_drc()
for v in violations:
    print(f"Rule: {v.rule}")
    print(f"Message: {v.message}")
    print(f"Layer: {v.layer}")
    print(f"Location: {v.location}")
    print(f"JSON: {v.to_json()}")
```

---

## LvsResult

Result of layout-vs-schematic comparison.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `matches` | `bool` | `True` if layout matches schematic |
| `device_count` | `int` | Number of extracted devices |
| `net_count` | `int` | Number of extracted nets |
| `mismatch_count` | `int` | Number of mismatches found |

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `mismatch_messages()` | `list[str]` | Human-readable mismatch descriptions |
| `to_json()` | `str` | Serialize result to JSON |

```python
lvs = c.check_lvs()
if lvs.matches:
    print(f"LVS clean: {lvs.device_count} devices, {lvs.net_count} nets")
else:
    print(f"{lvs.mismatch_count} mismatches:")
    for msg in lvs.mismatch_messages():
        print(f"  - {msg}")
```

---

## PexResult

Result of parasitic extraction.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `resistor_count` | `int` | Number of extracted parasitic resistors |
| `capacitor_count` | `int` | Number of extracted parasitic capacitors |
| `resistors` | `list[PexR]` | Extracted parasitic resistor elements |
| `capacitors` | `list[PexC]` | Extracted parasitic capacitor elements |

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `to_json()` | `str` | Serialize result to JSON |

---

## PexR and PexC

Individual parasitic elements from extraction.

### PexR (Parasitic Resistor)

| Property | Type | Description |
|----------|------|-------------|
| `node_a` | `str` | First node name |
| `node_b` | `str` | Second node name |
| `value_mohm` | `int` | Resistance in milli-ohms |

### PexC (Parasitic Capacitor)

| Property | Type | Description |
|----------|------|-------------|
| `node_a` | `str` | First node name |
| `node_b` | `str` | Second node name |
| `value_af` | `int` | Capacitance in atto-farads |

```python
pex = c.extract()
for r in pex.resistors:
    print(f"R({r.node_a}, {r.node_b}) = {r.value_mohm} mohm")
for cap in pex.capacitors:
    print(f"C({cap.node_a}, {cap.node_b}) = {cap.value_af} aF")
```

---

## Standalone GDS Functions

Run DRC/LVS/PEX directly on existing GDS files without going through the Component flow. Net connectivity is inferred via union-find on shape overlaps.

### `spout.drc_from_gds(path: str, pdk: Pdk | None = None) -> list[DrcViolation]`

Run DRC on a GDS file. Uses Sky130 PDK if `pdk` is not provided.

```python
violations = spout.drc_from_gds("layout.gds")
violations = spout.drc_from_gds("layout.gds", pdk=spout.Pdk.sky130())
```

### `spout.lvs_from_gds(path: str, pdk: Pdk | None = None) -> LvsResult`

Run connectivity extraction on a GDS file. Since standalone GDS has no schematic, the result reports what was extracted from layout geometry.

```python
result = spout.lvs_from_gds("layout.gds")
print(f"Extracted {result.net_count} nets, {result.device_count} devices")
```

### `spout.pex_from_gds(path: str, pdk: Pdk | None = None) -> PexResult`

Run parasitic extraction on a GDS file.

```python
pex = spout.pex_from_gds("layout.gds")
print(f"Found {pex.resistor_count} parasitic R, {pex.capacitor_count} parasitic C")
```

---

## The @cell Decorator

```python
@spout.cell
def inverter(pdk):
    c = spout.Component(pdk)
    mn = c.add_nmos(500, 180)
    mp = c.add_pmos(1000, 180)
    # ...
    return c
```

Currently a pass-through marker. In the future, will add caching by parameter hash for cell reuse across a chip.

---

## Constraint Vocabulary

The full constraint system has **24 constraint types** across 5 families. The Python API exposes the most essential subset.

### Exposed in Python API

| Method | Constraint Type | Family |
|--------|----------------|--------|
| `symmetric(a, b)` | `SymmetricPair` | Symmetry |
| `self_symmetric(a)` | `SelfSymmetric` | Symmetry |
| `common_centroid([...])` | `CommonCentroid` | Symmetry |
| `interdigitate([...])` | `Interdigitate` | Symmetry |
| `match_devices(a, b)` | `SameTemplate` | Ordering |
| `align_row([...])` | `Align(Horizontal)` | Ordering |
| `align_col([...])` | `Align(Vertical)` | Ordering |
| `above(a, b)` | `Order(Vertical)` | Ordering |
| `below(a, b)` | `Order(Vertical)` | Ordering |
| `left_of(a, b)` | `Order(Horizontal)` | Ordering |
| `right_of(a, b)` | `Order(Horizontal)` | Ordering |
| `min_spacing(a, b, d)` | `Distance` | Ordering |
| `guard_ring([...], type)` | `GuardRing` | Isolation |
| `shield_net(net)` | `NetShield` | Net/Routing |
| `match_length(a, b, tol)` | `NetMatch` | Net/Routing |
| `net_class(net, cls)` | `NetClass` | Net/Routing |

### Not Yet Exposed (Rust-only)

These exist in the constraint IR but don't have Python wrappers yet:

| Constraint | Family | Description |
|------------|--------|-------------|
| `SymmetricGroup` | Symmetry | Multiple symmetric pairs sharing an axis |
| `Order(devices, axis)` | Ordering | Order N devices along axis (Python has `above`/`below`/`left_of`/`right_of` for pairs) |
| `AspectRatio` | Boundary | Cell width/height ratio bounds |
| `Boundary` | Boundary | Fixed cell size |
| `FixPosition` | Boundary | Pin device to absolute coordinates |
| `Group` | Boundary | Cluster devices together |
| `SignalFlow` | Boundary | Signal-flow ordering |
| `PlaceOnGrid` | Isolation | Snap to manufacturing grid |
| `PlaceOnBoundary` | Isolation | Place on cell edge |
| `PortLocation` | Net/Routing | Route port to specific boundary edge |
| `MultiWire` | Net/Routing | Route net with parallel wires |
| `DoNotRoute` | Net/Routing | Exclude net from routing |
| `ChargeFlow` | Net/Routing | Electromigration annotation |
| `NetRoutingParams` | Net/Routing | Per-net routing parameter overrides |

---

## Typestate Flow

The Component transitions through strict states. Calling methods in the wrong state raises `RuntimeError`.

```
Component(pdk)          →  "building"
  ├── add_nmos/pmos/...
  ├── connect/named_net/add_port
  ├── symmetric/above/...
  └── place()           →  "placed"
       ├── show()
       └── route()      →  "routed"
            ├── show()
            ├── check_drc()
            ├── check_lvs()
            ├── extract()
            ├── export_gds()
            └── export_svg()

Component.from_spice()  →  "unplaced"
  └── place()           →  "placed"
       └── ...
```

**Valid calls per state:**

| Method | building | unplaced | placed | routed |
|--------|----------|----------|--------|--------|
| `add_nmos/pmos/...` | yes | no | no | no |
| `connect/connect_to_net` | yes | no | no | no |
| `named_net/add_port` | yes | no | no | no |
| All constraints | yes | no | no | no |
| `add_rect/add_rect_raw` | yes | no | no | no |
| `place()` | yes | yes | no | no |
| `route()` | no | no | yes | no |
| `show()` | no | no | yes | yes |
| `check_drc()` | no | no | no | yes |
| `check_lvs()` | no | no | no | yes |
| `extract()` | no | no | no | yes |
| `export_gds()` | no | no | no | yes |
| `export_svg()` | no | no | no | yes |
| `state()` | yes | yes | yes | yes |

---

## Units

Spout uses **100 picometers** as the internal unit. All public Python APIs accept **nanometers** (integer) unless noted.

| Context | Input Unit | Internal Conversion |
|---------|-----------|-------------------|
| `add_nmos(w, l)` | nm | `× 10` → 100pm |
| `add_rect(layer, x1, y1, x2, y2)` | nm | `× 10` → 100pm |
| `min_spacing(a, b, dist)` | nm | `× 10` → 100pm |
| `match_length(a, b, tol)` | nm | `× 10` → 100pm |
| `Length.nm(v)` | nm | `× 10` → 100pm |
| `Length.um(v)` | um | `× 10000` → 100pm |
| `Length.pm(v)` | pm | `÷ 100` → 100pm |
| `Point(x, y)` | 100pm (raw) | direct |
| `Point.from_nm(x, y)` | nm | `× 10` → 100pm |
| `Rect(x1, y1, x2, y2)` | 100pm (raw) | direct |

---

## Full Examples

### CMOS Inverter

```python
import spout

pdk = spout.Pdk.sky130()
c = spout.Component(pdk)

# Devices
mn = c.add_nmos(500, 180)
mp = c.add_pmos(1000, 180)

# Nets
vdd = c.named_net("VDD")
gnd = c.named_net("GND")
inp = c.connect([mn.g, mp.g])
out = c.connect([mn.d, mp.d])
c.connect_to_net(gnd, [mn.s, mn.b])
c.connect_to_net(vdd, [mp.s, mp.b])

# Ports
c.add_port("VDD", vdd, "inout")
c.add_port("GND", gnd, "inout")
c.add_port("IN", inp, "input")
c.add_port("OUT", out, "output")

# Constraints
c.above(mp, mn)
c.align_col([mp, mn])
c.net_class(vdd, "power")
c.net_class(gnd, "ground")

# Execute
c.place()
c.route()

# Verify
violations = c.check_drc()
lvs = c.check_lvs()
print(f"DRC: {len(violations)} violations")
print(f"LVS: {'clean' if lvs.matches else 'FAIL'}")

# Export
c.export_gds("inverter.gds")
c.export_svg("inverter.svg")
```

### Differential Pair

```python
import spout

pdk = spout.Pdk.sky130()
c = spout.Component(pdk)

# Differential input pair
mn_p = c.add_nmos(500, 180, nf=2)
mn_n = c.add_nmos(500, 180, nf=2)

# Tail current source
m_tail = c.add_nmos(1000, 180, nf=4)

# Active loads
mp_p = c.add_pmos(1000, 180, nf=2)
mp_n = c.add_pmos(1000, 180, nf=2)

# Nets
vdd = c.named_net("VDD")
gnd = c.named_net("GND")
inp = c.connect([mn_p.g])
inn = c.connect([mn_n.g])
out_p = c.connect([mn_p.d, mp_p.d])
out_n = c.connect([mn_n.d, mp_n.d])
tail = c.connect([mn_p.s, mn_n.s, m_tail.d])
bias = c.connect([m_tail.g])
c.connect_to_net(gnd, [m_tail.s, m_tail.b, mn_p.b, mn_n.b])
c.connect_to_net(vdd, [mp_p.s, mp_p.b, mp_n.s, mp_n.b])
mirror = c.connect([mp_p.g, mp_n.g])

# Ports
c.add_port("VDD", vdd, "inout")
c.add_port("GND", gnd, "inout")
c.add_port("INP", inp, "input")
c.add_port("INN", inn, "input")
c.add_port("OUTP", out_p, "output")
c.add_port("OUTN", out_n, "output")
c.add_port("BIAS", bias, "input")

# Constraints — symmetry and matching
c.symmetric(mn_p, mn_n)          # input pair symmetric
c.symmetric(mp_p, mp_n)          # load pair symmetric
c.self_symmetric(m_tail)         # tail on axis
c.match_devices(mn_p, mn_n)      # identical templates
c.match_devices(mp_p, mp_n)
c.above(mp_p, mn_p)              # PMOS above NMOS
c.above(mp_n, mn_n)
c.below(m_tail, mn_p)            # tail below diff pair
c.match_length(inp, inn, 50)     # matched input routing
c.net_class(vdd, "power")
c.net_class(gnd, "ground")
c.guard_ring([mn_p, mn_n, m_tail], "substrate")

# Execute
c.place()
c.route()
c.export_gds("diffpair.gds")
```

### From SPICE Netlist

```python
import spout

pdk = spout.Pdk.sky130()

# Direct import — auto-parses and builds
c = spout.Component.from_spice("ota.spice", pdk)
c.place()
c.route()
c.export_gds("ota.gds")
```

### Codegen Workflow

```python
import spout

# Generate editable Python from SPICE
code = spout.Component.codegen_from_spice("ota.spice")
with open("ota_layout.py", "w") as f:
    f.write(code)

# Now edit ota_layout.py to add constraints,
# then run it to produce the layout.
```

### Standalone GDS Verification

```python
import spout

# Run DRC on an existing GDS (e.g. from another tool)
violations = spout.drc_from_gds("external_layout.gds")
print(f"DRC: {len(violations)} violations")

# Run PEX
pex = spout.pex_from_gds("external_layout.gds")
print(f"Extracted: {pex.resistor_count} R, {pex.capacitor_count} C")
```

### Multi-Finger Devices

```python
import spout

pdk = spout.Pdk.sky130()
c = spout.Component(pdk)

# 8-finger NMOS
m = c.add_nmos(500, 180, nf=8)
print(f"Fingers: {m.nf}")          # 8
print(f"Terminals: {m.num_terminals}")  # 4

# Access individual fingers
for i in range(m.nf):
    f = m.finger(i)
    print(f"  Finger {f.finger_idx}: gate={f.g}, drain={f.d}, source={f.s}")
```

### Resistor Layout

```python
import spout

pdk = spout.Pdk.sky130()
c = spout.Component(pdk)

r1 = c.add_resistor(330, 10000)   # 330nm wide, 10um long
r2 = c.add_resistor(330, 10000)

net_a = c.connect([r1.port(0)])
net_mid = c.connect([r1.port(1), r2.port(0)])  # series connection
net_b = c.connect([r2.port(1)])

c.add_port("A", net_a, "inout")
c.add_port("MID", net_mid, "inout")
c.add_port("B", net_b, "inout")

c.symmetric(r1, r2)
c.match_devices(r1, r2)
c.align_row([r1, r2])

c.place()
c.route()
c.export_gds("resistors.gds")
```
