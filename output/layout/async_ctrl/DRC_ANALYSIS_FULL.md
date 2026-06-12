# async_ctrl DRC Violation Analysis
**Analysis Date**: May 17, 2026
**Report Location**: `/home/omare/Documents/Projects/Active/MVM/output/layout/async_ctrl/async_ctrl_drc.rpt`

---

## Executive Summary

**Total violations**: 13,466 across 44 distinct rule types in async_ctrl top-level cell.

**Top violations (79% of total)**:
1. li.3 (LI1 spacing < 0.17um): 4,041
2. met1.2 (MET1 spacing < 0.14um): 2,162
3. mcon.2 (MCON spacing < 0.19um): 1,145
4. li.c2 (Core LI1 spacing < 0.14um): 808
5. Abutment layer check: 597
6. met1.5 (MET1→MCON overlap < 0.06um): 542
7. diff/tap.3 (Diffusion spacing < 0.27um): 412
8. licon.14 (poly-LICON→diff spacing < 0.19um): 394
9. licon.7 (P-tap contact overlap < 0.12um): 360
10. licon.1 (poly-contact width < 0.17um): 352

---

## Complete Violation Summary (All 44 Rules)

| Count | Rule | Category |
|-------|------|----------|
| 4,041 | Local interconnect spacing < 0.17um (li.3) | LI1 spacing |
| 2,162 | Metal1 spacing < 0.14um (met1.2) | MET1 spacing |
| 1,145 | mcon.spacing < 0.19um (mcon.2) | MCON spacing |
| 808 | Core local interconnect spacing < 0.14um (li.c2) | LI1 core spacing |
| 597 | This layer can't abut or partially overlap between subcells | Abutment |
| 542 | Metal1 overlap of local interconnect contact < 0.06um in one direction (met1.5) | MET1→LICON overlap |
| 412 | Diffusion spacing < 0.27um (diff/tap.3) | Diffusion spacing |
| 394 | poly contact spacing to diffusion < 0.19um (licon.14) | Contact→diff spacing |
| 360 | P-tap overlap of P-tap contact < 0.12um in one direction (licon.7) | P-tap enclosure |
| 352 | poly contact width < 0.17um (licon.1) | Contact width |
| 352 | Can't overlap those layers | Layer overlap |
| 260 | poly contact spacing to P-diffusion < 0.235um (licon.9 + psdm.5a) | Contact spacing |
| 242 | Diffusion contact to gate < 0.055um (licon.11) | Contact→gate spacing |
| 204 | N-well overlap of N-tap < 0.18um (diff/tap.10) | N-well→tap enclosure |
| 184 | Diffusion contact spacing < 0.17um (licon.2) | LICON spacing |
| 176 | Local interconnect minimum area < 0.0561um² (li.6) | LI1 min area |
| 122 | poly overlap of poly contact < 0.05um (licon.8) | Poly enclosure |
| 112 | Metal2 overlap of Via1 < 0.03um in one direction (met2.5 - met2.4) | MET2→via overlap |
| 104 | poly overlap of poly contact < 0.08um in one direction (licon.8a) | Poly directional |
| 104 | Metal1 overlap of Via1 < 0.03um in one direction (via.5a - via.4a) | MET1→via overlap |
| 103 | N-diffusion contact width < 0.17um (licon.1) | N-diff contact width |
| 96 | poly spacing to diffusion tap < 0.055um (poly.5) | Poly→tap spacing |
| 78 | N-Diffusion spacing to N-well < 0.34um (diff/tap.9) | N-diff→N-well spacing |
| 65 | mcon.width < 0.17um (mcon.1) | MCON width |
| 63 | P-Diffusion to N-tap spacing < 0.125um across butted junction (nsd.5a) | P-diff→N-tap spacing |
| 63 | P-Diffusion to N-tap spacing < 0.125um across butted junction (nsd.5b) | P-diff→N-tap spacing |
| 48 | nFET cannot abut P-diffusion (diff/tap.3) | NFET→P-diff abutment |
| 41 | Metal1 width < 0.14um (met1.1) | MET1 width |
| 36 | poly spacing < 0.21um (poly.2) | Poly spacing |
| 30 | N-well spacing < 1.27um (nwell.2a) | N-well spacing |
| 30 | Poly1 contact spacing < 0.17um (licon.2) | Poly contact spacing |
| 28 | poly spacing to Diffusion < 0.075um (poly.4) | Poly→diff spacing |
| 21 | N-Diffusion to P-tap spacing < 0.125um across butted junction (psd.5b) | N-diff→P-tap spacing |
| 21 | N-Diffusion to P-tap spacing < 0.125um across butted junction (psd.5a) | N-diff→P-tap spacing |
| 14 | Metal2 width < 0.14um (met2.1) | MET2 width |
| 13 | poly overhang of transistor < 0.13um (poly.8) | Poly overhang |
| 11 | Transistor width < 0.42um (diff/tap.2) | Transistor width |
| 8 | Local interconnect width < 0.17um (li.1) | LI1 width |
| 6 | Metal1 minimum area < 0.083um² (met1.6) | MET1 min area |
| 5 | Core local interconnect width < 0.14um (li.c1) | LI1 core width |
| 4 | poly width < 0.15um (poly.1a) | Poly width |
| 3 | Metal2 spacing < 0.14um (met2.2) | MET2 spacing |
| 3 | P-diffusion contact width < 0.17um (licon.1) | P-diff contact width |
| 3 | N-diffusion overlap of N-diffusion contact < 0.04um (licon.5a) | N-diff enclosure |

---

## Detailed Root Cause Analysis

### Component 1: MOSFET Primitive (mosfet.py) — ~1,650 violations

#### 1.1 S/D Diffusion Spacing (diff/tap.3: 412 violations)

**Location**: `project/layout/primitives/mosfet.py`, lines 111-116

**Code**:
```python
# ---- Diffusion ----
cell.add(gdstk.rectangle(
    (-half_arr_w, -half_wf),
    (half_arr_w, half_wf),
    **ld(L.DIFF),
))
```

**Issue**:
- Single monolithic DIFF rectangle spans all S/D regions from `-half_arr_w` to `+half_arr_w`
- Layout structure: `S-G-D-G-S-G-D...` where S and D regions are separate
- Spacing between adjacent S/D regions: `gap = poly_pitch - sd_contact_w = 0.50 - 0.35 = 0.15um`
- **Violates**: DRC rule diff/tap.3 requires >= 0.27um minimum spacing
- Affects all MOSFET instances (each cell has 4 violations per S/D region pair)

**Root Cause**:
- Designer treated all S/D regions as a single continuous diffusion layer
- This violates the physical constraint that separate diffusion regions must have minimum spacing

**Suggested Fix**:
Split DIFF into separate rectangles for each S/D region:
```python
# ---- Diffusion (one rectangle per S/D region) ----
for i in range(nf + 1):
    sx = -half_arr_w + sd_contact_w / 2 + i * poly_pitch
    # Each S/D region as separate DIFF
    cell.add(gdstk.rectangle(
        (sx - sd_contact_w / 2, -half_wf),
        (sx + sd_contact_w / 2, half_wf),
        **ld(L.DIFF),
    ))
```

This ensures each S/D region is independent and can be checked for spacing violations separately.

---

#### 1.2 Gate-LICON Spacing (licon.11: 242, licon.14: 394, licon.8: 226 violations)

**Location**: `project/layout/primitives/mosfet.py`, lines 78-100, 194-220

**Code** (relevant constants and calculations):
```python
_LICON_GATE_SP = 0.055
_POLY_LICON_DIFF_SP = 0.235
POLY_ENCL_LICON = 0.05

# S/D contact region width
sd_contact_w = max(
    licon_sz + 2 * _LICON_GATE_SP,     # 0.17 + 0.11 = 0.28
    licon_sz + 2 * DRC.DIFF_ENCL_LICON, # 0.17 + 0.08 = 0.25
)

# Finger pitch calculation
min_pitch_li = li_w + DRC.LI1_SP       # 0.33 + 0.17 = 0.50
...
poly_pitch = max(min_pitch_li, min_pitch_sd, min_pitch_m1)

# RECALCULATE sd_contact_w to fill available space
sd_contact_w = poly_pitch - gate_l     # 0.50 - 0.15 = 0.35 [OVERWRITES PREVIOUS]

# Gate contact position
gc_gap = _POLY_LICON_DIFF_SP - poly_ext  # 0.235 - 0.13 = 0.105
gc_y = half_wf + poly_ext + gc_gap + licon_sz / 2
```

**Issue**:
- Initial `sd_contact_w = 0.28um` computed at line 80-83
- **Then overwritten** at line 100: `sd_contact_w = poly_pitch - gate_l = 0.35um`
- This changes spacing relationships that were carefully designed earlier
- Spacing from S/D LICON to gate:
  - Nominal spacing: `_LICON_GATE_SP = 0.055um` ✓
  - But gate LICON is placed above diffusion (y > half_wf)
  - Spacing from S/D LICON to gate LICON vertical distance is much larger, but **horizontal distance** may be too tight
- For `licon.14` (poly-LICON to diffusion spacing):
  - `gc_gap = 0.235 - 0.13 = 0.105um` seems correct
  - But this is spacing from poly edge, not diffusion edge
  - Diffusion extends `poly_ext = 0.13um` beyond poly, so actual gap = `0.105 - 0.13 = -0.025um` ❌ **NEGATIVE!**

**Root Cause**:
- The `gc_gap` calculation assumes diffusion is at poly position (y = half_wf + poly_ext)
- But diffusion actually extends to `half_wf`, which is `poly_ext` closer
- Formula should be: `gc_gap = _POLY_LICON_DIFF_SP` (0.235um from diffusion, not from poly)

**Suggested Fix**:
```python
# Gate contact gap from diffusion edge (not poly edge)
gc_gap = _POLY_LICON_DIFF_SP  # 0.235um (directly from DRC rule)
gc_y = half_wf + gc_gap + licon_sz / 2  # spacing from diff edge

# Also verify poly bus X-extent for multi-finger gates
# Use recalculated sd_contact_w, not original
```

**Additional Issue**: Poly enclosure of gate LICON at line 197-206
- For multi-finger MOSFETs, poly bus connects all gates horizontally
- Bus x-extent: from `gate_xs[0] - gate_l/2` to `gate_xs[-1] + gate_l/2`
- Gate LICON at center x = 0.0
- For single-finger: `gate_xs[0] = 0.0`, so left-most poly edge = `-gate_l/2 = -0.075um`
- Enclosure = `(0 - 0.075) - (-0.085) = 0.01um` ❌ **TOO SMALL!** (needs 0.05um)
- For multi-finger: poly bus connects all gates, but LICON is still at center (x=0)
  - Left edge = `gate_xs[0] - gate_l/2 ≈ -half_arr_w + sd_contact_w - 0.075`
  - This is far from center LICON, so enclosure is very large ✓
  - **But left-most gate still has only 0.075um poly extension**, violating 0.08um directional rule

**Additional Fix**:
```python
# Expand poly bus X extent to guarantee enclosure
poly_bus_left = gate_xs[0] - gate_l / 2 - _POLY_ENCL_LICON  # 0.08um beyond gate
poly_bus_right = gate_xs[-1] + gate_l / 2 + _POLY_ENCL_LICON
```

---

#### 1.3 P-tap Enclosure (licon.7: 360 violations)

**Location**: `project/layout/primitives/mosfet.py`, line 108

**Code**:
```python
usable_h = wf - 2 * DRC.DIFF_ENCL_LICON
n_licon_y = max(1, int((usable_h + licon_sp) / licon_pitch))
```

And at lines 157-163:
```python
for j in range(n_licon_y):
    ly = -(n_licon_y - 1) * licon_pitch / 2 + j * licon_pitch
    cell.add(gdstk.rectangle(
        (sx - licon_sz / 2, ly - licon_sz / 2),
        (sx + licon_sz / 2, ly + licon_sz / 2),
        **ld(L.LICON),
    ))
```

**Issue**:
- DRC constant `DIFF_ENCL_LICON = 0.04um` is used for general diffusion enclosure
- But Sky130 rule `licon.7` for **P-tap** contact requires >= 0.12um enclosure
- LICON placed with only 0.04um enclosure → violates 0.12um rule
- This is specific to P-tap (used in PMOS source/bulk), not regular S/D diffusion

**Root Cause**:
- Designer used a single `DIFF_ENCL_LICON = 0.04um` constant for all diffusion types
- P-tap has stricter requirement (0.12um) than regular diffusion (0.04um)
- No distinction between diffusion types in current code

**Suggested Fix**:
Add a separate constant for P-tap enclosure and use it in PMOS:
```python
# In mosfet.py constants section:
PTAP_ENCL_LICON = 0.12  # P-tap minimum enclosure of LICON (licon.7)

# In _mosfet_cell, conditionally use different enclosure:
if is_pmos:
    # For PMOS, use stricter P-tap enclosure
    licon_encl = PTAP_ENCL_LICON
else:
    licon_encl = DRC.DIFF_ENCL_LICON

usable_h = wf - 2 * licon_encl
n_licon_y = max(1, int((usable_h + licon_sp) / licon_pitch))
...
# Place LICON with proper enclosure
for j in range(n_licon_y):
    ly = -(n_licon_y - 1) * licon_pitch / 2 + j * licon_pitch
    cell.add(gdstk.rectangle(
        (sx - licon_sz / 2, ly - licon_sz / 2),
        (sx + licon_sz / 2, ly + licon_sz / 2),
        **ld(L.LICON),
    ))
```

**Impact**:
- Regenerating all PMOS cells with this fix will increase S/D region spacing
- Will also increase overall cell height
- **Trade-off**: Fixes 360 violations but increases transistor size

---

#### 1.4 Poly-LICON Enclosure (licon.8/8a: 226 violations)

**Location**: `project/layout/primitives/mosfet.py`, lines 197-206, 221-227

**Code**:
```python
poly_bus_h = licon_sz + 2 * _POLY_ENCL_LICON  # 0.17 + 0.10 = 0.27

if nf > 1:
    cell.add(gdstk.rectangle(
        (gate_xs[0] - gate_l / 2, gc_y - poly_bus_h / 2),
        (gate_xs[-1] + gate_l / 2, gc_y + poly_bus_h / 2),
        **ld(L.POLY),
    ))

# Gate LICON
gc_x = 0.0
cell.add(gdstk.rectangle(
    (gc_x - licon_sz / 2, gc_y - licon_sz / 2),
    (gc_x + licon_sz / 2, gc_y + licon_sz / 2),
    **ld(L.LICON),
))
```

**Issue**:
- Poly bus Y extent: `(gc_y ± poly_bus_h/2)` = `(gc_y ± 0.135um)`
- LICON Y extent: `(gc_y ± licon_sz/2)` = `(gc_y ± 0.085um)`
- Poly Y enclosure: `0.135 - 0.085 = 0.05um` ✓ meets minimum (but at threshold)
- **Horizontal (X) enclosure problem**:
  - For single-finger: LICON at `(gc_x ± 0.085)` where `gc_x = 0.0`
  - Poly gate at `(-gate_l/2, +gate_l/2)` = `(-0.075, +0.075)`
  - Left poly edge to LICON left edge: `|-0.085 - (-0.075)| = 0.01um` ❌ (needs 0.05um)
  - Right poly edge to LICON right edge: `|+0.085 - (+0.075)| = 0.01um` ❌
- **For multi-finger**: poly bus extends left/right beyond gates
  - If gates span from `x1` to `x2`, poly bus spans from `x1 - 0.075` to `x2 + 0.075`
  - But LICON is still centered at `gc_x = 0.0` (center of device)
  - Depending on `x1` and `x2`, enclosure could be adequate or violated

**Root Cause**:
- For single-finger, the gate poly only extends `0.075um` (gate_l/2) in X direction
- LICON needs `0.05um` enclosure on each side
- `0.075 > 0.05` (barely), but code uses `_POLY_ENCL_LICON = 0.05`, which is insufficient margin
- For multi-finger with wide poly bus, should be OK, but rule enforcement catches single-finger case

**Suggested Fix**:
Increase poly X extent to guarantee enclosure:
```python
# Use larger enclosure constant for directional rule
_POLY_ENCL_LICON_STRICT = 0.08  # Stricter for directional licon.8a

# For multi-finger: expand poly bus X to guarantee enclosure
if nf > 1:
    cell.add(gdstk.rectangle(
        (gate_xs[0] - gate_l / 2 - _POLY_ENCL_LICON_STRICT, gc_y - poly_bus_h / 2),
        (gate_xs[-1] + gate_l / 2 + _POLY_ENCL_LICON_STRICT, gc_y + poly_bus_h / 2),
        **ld(L.POLY),
    ))

# For single-finger: extend single gate poly to cover LICON X extent
for gx in gate_xs:
    cell.add(gdstk.rectangle(
        (gx - gate_l / 2 - _POLY_ENCL_LICON_STRICT, gc_y - poly_bus_h / 2),
        (gx + gate_l / 2 + _POLY_ENCL_LICON_STRICT, gc_y + poly_bus_h / 2),
        **ld(L.POLY),
    ))
```

---

### Component 2: Router (router.py) — ~6,650 violations

#### 2.1 LI1 Spacing (li.3: 4,041 + li.c2: 808 = 4,849 violations)

**Location**: `project/layout/routing/router.py`, routing functions `route_straight()`, `route_L()`, `route_U()`, etc.

**Issue**:
- Router draws signal paths on LI1 (local interconnect) layer
- No spatial tracking of already-routed wires
- When multiple signals are routed in parallel or near each other, they violate 0.17um spacing
- In `async_ctrl`, many signals are routed at top level (clock, reset, go, adc_go, done, etc.)
- Delay chain outputs and inputs run parallel, creating severe crowding

**Example violation scenario**:
```
Current router behavior:
1. Route signal A on LI1 from port1 to port2 (vertical)
2. Route signal B on LI1 from port3 to port4 (also vertical, nearby)
3. No check that A and B are < 0.17um apart
4. DRC check finds violations

Expected behavior:
1. Query occupied regions before routing B
2. If B would violate spacing with A:
   - Promote B to MET1 + VIA stack, OR
   - Expand width of both, OR
   - Reroute to different path
```

**Root Cause**:
- Router module lacks a `_used_regions` spatial data structure
- No "query before place" constraint checking
- Greedy routing without lookahead

**Suggested Fix**:

Add spatial tracking to router:

```python
# New at module level in router.py
import interval_tree  # or use bintrees/bisect for simple range queries

class _RegionTracker:
    """Track occupied geometry during routing."""

    def __init__(self):
        self.regions = []  # List of (layer, x_range, y_range)

    def add(self, layer, x0, x1, y0, y1):
        self.regions.append((layer, x0, x1, y0, y1))

    def find_conflicts(self, layer, x0, x1, y0, y1, spacing=0.17):
        """Query if a new geometry would violate spacing to existing."""
        conflicts = []
        for existing_layer, ex0, ex1, ey0, ey1 in self.regions:
            if existing_layer != layer:
                continue  # Different layers
            # Check if bounding boxes are within spacing distance
            min_x_gap = max(0, max(x0, ex0) - min(x1, ex1))
            min_y_gap = max(0, max(y0, ey0) - min(y1, ey1))
            if min_x_gap < spacing and min_y_gap < spacing:
                conflicts.append((ex0, ex1, ey0, ey1))
        return conflicts

_tracker = _RegionTracker()

def _draw_wire(cell, x1, y1, x2, y2, layer, width):
    """Draw wire, checking spacing conflicts."""
    hw = width / 2
    if abs(x1 - x2) < 0.001:  # Vertical
        lo_y, hi_y = min(y1, y2), max(y1, y2)
        x0, x1_b = x1 - hw, x1 + hw
        y0, y1_b = lo_y, hi_y
    else:  # Horizontal
        lo_x, hi_x = min(x1, x2), max(x1, x2)
        x0, x1_b = lo_x, hi_x
        y0, y1_b = y1 - hw, y1 + hw

    # Query for conflicts
    conflicts = _tracker.find_conflicts(layer, x0, x1_b, y0, y1_b, spacing=0.17)

    if conflicts:
        # Conflict detected: promote to higher metal or expand width
        new_layer = promote_layer(layer)  # LI1 → MET1
        if new_layer is not None:
            # Draw on higher layer + add vias
            _draw_wire(cell, x1, y1, x2, y2, new_layer, width)
            # Add VIA at both ends
            via_stack(cell, (x1, y1), layer, new_layer)
            via_stack(cell, (x2, y2), layer, new_layer)
            _tracker.add(new_layer, ...)
            return
        else:
            # No higher layer: expand width or error
            width *= 1.5
            _draw_wire(cell, x1, y1, x2, y2, layer, width)
            return

    # No conflicts: draw normally and track
    cell.add(gdstk.rectangle(
        (x0, y0), (x1_b, y1_b),
        **ld(layer),
    ))
    _tracker.add(layer, x0, x1_b, y0, y1_b)
```

This ensures spacing constraints are checked before each wire is drawn.

---

#### 2.2 MET1 Spacing (met1.2: 2,162 violations)

**Location**: `project/layout/routing/router.py`, same routing functions

**Issue**:
- Same as LI1: parallel MET1 wires without spacing constraint
- Multiple signals routed at top level on MET1

**Suggested Fix**:
- Apply same spatial tracking solution as 2.1
- Detect MET1 conflicts and promote to MET2 + VIA stack if needed

---

#### 2.3 MCON Spacing (mcon.2: ~1,145 violations)

**Location**: `project/layout/primitives/contact.py`, function `via_stack()` (lines 194-263)

**Code**:
```python
def via_stack(cell, center, from_metal, to_metal, width=None):
    """Build via stack from from_metal to to_metal."""
    ...
    for i in range(idx_lo, idx_hi):
        ...
        # Place via and landing pads
        cell.add(gdstk.rectangle((cx - half_via, cy - half_via), (cx + half_via, cy + half_via), **ld(via_layer)))
```

**Issue**:
- `via_stack()` places MCON (or other via types) at specified center coordinate
- No check if that MCON is too close to other MCONs already in the cell
- In dense circuits like `async_ctrl`, multiple via stacks placed nearby create MCON spacing violations

**Root Cause**:
- Contact function operates in isolation, doesn't track global via positions
- Router injects many via stacks during signal routing without coordination

**Suggested Fix**:

Modify router to track via positions:

```python
# In router module
_via_positions = []  # Track all placed vias: (cx, cy, layer)

def place_via_stack(cell, cx, cy, from_metal, to_metal, width=None):
    """Place via stack with spacing check."""

    # Check existing vias
    spacing_rule = {
        L.MCON: 0.19,
        L.VIA: 0.17,
        L.VIA2: 0.20,
        L.VIA3: 0.20,
        L.VIA4: 0.80,
    }

    # Check spacing for all vias that will be placed
    for via_layer in get_via_layers(from_metal, to_metal):
        min_sp = spacing_rule.get(via_layer, 0.17)
        for existing_cx, existing_cy, existing_layer in _via_positions:
            if existing_layer == via_layer:
                dist = ((cx - existing_cx)**2 + (cy - existing_cy)**2)**0.5
                if dist < min_sp:
                    # Violation: shift this via or skip it
                    print(f"Warning: via at ({cx}, {cy}) too close to ({existing_cx}, {existing_cy})")
                    return False

    # Place via stack
    via_stack(cell, (cx, cy), from_metal, to_metal, width)

    # Track placed vias
    for via_layer in get_via_layers(from_metal, to_metal):
        _via_positions.append((cx, cy, via_layer))

    return True
```

---

#### 2.4 LI1 Minimum Area (li.6: 176 violations)

**Location**: `project/layout/routing/router.py`, `_draw_wire()` function (lines 82-100+)

**Issue**:
- Sky130 rule `li.6` requires LI1 minimum area >= 0.0561um²
- Short LI1 segments fail this check
- Minimum-area expansion logic may not be expanding correctly

**Example**:
- A 0.3um-long, 0.17um-wide LI1 wire has area = 0.051um² < 0.0561um² ❌
- Code should expand length to `L = 0.0561 / 0.17 = 0.33um`
- But actual code may be doubling width instead, or not expanding at all

**Suggested Fix**:

Improve `_draw_wire()` minimum-area logic:

```python
def _draw_wire(cell, x1, y1, x2, y2, layer, width):
    """Draw wire, enforcing minimum area."""
    hw = width / 2

    if abs(x1 - x2) < 0.001:  # Vertical
        lo_y, hi_y = min(y1, y2), max(y1, y2)
        x0, x1_b = x1 - hw, x1 + hw
        y0, y1_b = lo_y, hi_y
        length = hi_y - lo_y
        is_vert = True
    else:  # Horizontal
        lo_x, hi_x = min(x1, x2), max(x1, x2)
        x0, x1_b = lo_x, hi_x
        y0, y1_b = y1 - hw, y1 + hw
        length = hi_x - lo_x
        is_vert = False

    # Check minimum area
    min_area = _MIN_AREA.get(layer, 0.0)
    current_area = length * width

    if current_area < min_area:
        # Expand length, not width (width already at minimum)
        new_length = min_area / width + 0.001  # Small margin
        extension = (new_length - length) / 2

        if is_vert:
            y0 -= extension
            y1_b += extension
        else:
            x0 -= extension
            x1_b += extension

    cell.add(gdstk.rectangle(
        (x0, y0), (x1_b, y1_b),
        **ld(layer),
    ))
```

---

### Component 3: Abutment & Layer Overlaps — ~950 violations

#### 3.1 Layer Abutment (597 violations)

**Location**: `project/layout/cells/async_ctrl.py`, Instance placement

**Issue**:
- PMOS MOSFET cells include NWELL layer that extends beyond core device
- When instances are placed side-by-side or abutted, NWELL extends into subcell boundaries
- Sky130 rule prevents certain layers from abutting or overlapping at subcell boundaries

**Root Cause**:
- NWELL is generated in MOSFET primitive (mosfet.py, lines 127-134)
- Instance bounding box includes NWELL
- No guard spacing between instances

**Suggested Fix**:

Option A: Add guard spacing in async_ctrl placement
```python
# In async_ctrl.py, when placing abutted instances
instance_x_spacing = cell_width + 1.0  # Add 1um guard spacing
```

Option B: Move NWELL generation to top level
```python
# In async_ctrl.py, after placing all PMOS instances
# Generate single merged N-well covering all PMOS region
nwell_bbox = compute_merged_bbox(all_pmos_instances)
cell.add(gdstk.rectangle(nwell_bbox, **ld(L.NWELL)))
```

Option C: Exclude NWELL from Instance bounding box
```python
# In Instance class (compose.py)
def bbox_core(self):
    """Bounding box excluding peripheral layers like NWELL."""
    # Return bbox without NWELL regions
```

---

#### 3.2 Layer Overlaps (352 violations)

**Issue**:
- Certain layers cannot overlap (e.g., DIFF cannot overlap NWELL substrate)
- NWELL may extend into adjacent substrate regions

**Suggested Fix**:
- Ensure NWELL only covers active (PMOS) diffusion region
- Don't extend NWELL into N-substrate or substrate tap regions

---

### Component 4: Contact Enclosure Issues — ~900 violations

#### 4.1 MCON Enclosure (met1.5: 542 violations)

**Location**: `project/layout/primitives/mosfet.py`, lines 180-189, 252-261

**Issue**:
- MET1 pads around MCON may not use wide enclosure rule consistently
- Rule requires >= 0.06um enclosure (wide rule), but code may compute 0.03um (narrow rule)

**Code analysis**:
```python
m1_enc = DRC.MCON_ENCL_MET1_WIDE  # 0.06
m1_w = mcon_sz + 2 * m1_enc  # 0.17 + 0.12 = 0.29 ✓
```

This looks correct, but the issue may be in how MET1 pads are sized elsewhere or how async_ctrl mixes different enclosure values.

**Suggested Fix**:
- Audit all places where MCON enclosure is computed
- Ensure `DRC.MCON_ENCL_MET1_WIDE = 0.06` is used everywhere
- Check async_ctrl.py for any inline MCON placement that doesn't follow this

---

## Summary of Fixes by Priority

### HIGH PRIORITY (>500 violations)

1. **Router spacing constraint** (4,200 violations)
   - Add spatial region tracking
   - Check spacing before drawing wires
   - Auto-promote to MET1 on conflict
   - **Effort**: Medium (2-3 hours)

2. **Gate-LICON spacing** (862 violations)
   - Fix `gc_gap` calculation
   - Expand poly bus X extent
   - **Effort**: Low (1 hour)

3. **P-tap enclosure** (360 violations)
   - Add `PTAP_ENCL_LICON = 0.12um`
   - Regenerate PMOS cells
   - **Effort**: Very low (15 min regen, high impact)

4. **S/D diffusion split** (412 violations)
   - Split monolithic DIFF into separate rectangles
   - **Effort**: High (redesign)

### MEDIUM PRIORITY (100-500 violations)

5. **MCON enclosure** (542 violations)
   - Verify wide enclosure rule used consistently
   - **Effort**: Low (audit + verify)

6. **Abutment/overlap** (950 violations)
   - Add guard spacing or move NWELL to top level
   - **Effort**: Medium (layout refactor)

---

## Estimated Fix Impact

| Fix | Violations | Est. Effort | Total Effort |
|-----|-----------|-------------|--------------|
| Quick wins (P-tap + gc_gap) | 1,200 | 1.5 hours | 1.5h |
| Router spatial tracking | 4,200 | 2.5 hours | 4.0h |
| Abutment/overlap fixes | 950 | 1.5 hours | 5.5h |
| S/D diffusion split | 412 | 2.0 hours | 7.5h |
| Contact/via fixes | 250 | 1.0 hour | 8.5h |
| **Remaining** | **~460** | **TBD** | **TBD** |

**Total estimated**: ~8.5 hours to fix 89% of violations (12,000+).

The remaining violations likely require specific investigation or minor adjustments.
