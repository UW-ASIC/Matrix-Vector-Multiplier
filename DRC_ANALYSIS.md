# Interleaved ADC DRC Violation Analysis

## Summary

**Total violations: 3,269 unique instances across ~30 DRC rules**

### Violation Distribution by Cell Hierarchy
- **Top level (interleaved_adc)**: 652 violations
- **ADC units** (adc_unit_0, adc_unit_1): 314 violations each (628 total)
- **CDAC blocks** (u0_cdac, u1_cdac): 112 violations each (224 total)
- **SAR logic blocks** (u0_sar_a, u0_sar_b, u1_sar_a, u1_sar_b): 85 violations each (340 total)
- **Buffer inverters** (*_buf*_*): 4-15 violations each
- **Switches/inverters** (*_sw*, *_mux*, *_inv): 4-15 violations each
- **Comparators** (u0_comp, u1_comp): 4-8 violations each

---

## DRC Rules Identified and Root Causes

### **CRITICAL: Poly-related violations (High frequency)**

#### 1. **Poly spacing < 0.21um (poly.2)** — 42 violations
**Rule**: `poly spacing < 0.21um (poly.2)`
**Root Cause**: Gate poly spacing in MOSFET primitive too tight
**Source**: `mosfet.py` — lines 136-146 (gate generation)
**Analysis**:
- Gate pitch calculated as: `max(min_pitch_li, min_pitch_sd, min_pitch_m1)` (line 97)
- Current calculation uses `min_pitch_li = li_w + DRC.LI1_SP = 0.33 + 0.17 = 0.50`
- But gate-to-gate spacing in multi-finger layout must also account for poly spacing rule
- **Why it fails**: The gate pitch doesn't explicitly respect `POLY_SP = 0.21`, only MET1 and LI1 rules
- **Affected**: Multi-finger devices (INP pair with nf=8, LATCH_P with nf=6, LATCH_N with nf=2, etc.)

#### 2. **Poly spacing to Diffusion < 0.075um (poly.4)** — 24 violations
**Rule**: `poly spacing to Diffusion < 0.075um (poly.4)`
**Root Cause**: Gate poly extension above diffusion too close to diff boundary
**Source**: `mosfet.py` — lines 213-219 (gate extension)
**Analysis**:
- `gc_poly_top = gc_y + poly_bus_h / 2` (line 213)
- The gate bus is drawn with minimal spacing from the diff/poly boundary
- **Why it fails**: When poly extends above the diffusion (for gate contact), the spacing constraint isn't enforced
- **Affected**: All MOSFETs with gate contacts

#### 3. **Poly contact spacing to diffusion < 0.19um (licon.14)** — 200+ violations
**Rule**: `poly contact spacing to diffusion < 0.19um (licon.14)`
**Root Cause**: Gate LICON placed too close to edge of diffusion
**Source**: `mosfet.py` — lines 194-195 and 221-227 (gate contact placement)
**Analysis**:
- `gc_gap = _POLY_LICON_DIFF_SP - poly_ext = 0.235 - 0.13 = 0.105`
- `gc_y = half_wf + poly_ext + gc_gap + licon_sz / 2` (line 195)
- This places the LICON at distance `poly_ext + gc_gap = 0.235` from diff center edge
- But the rule needs contact center distance `>= 0.19` from the *diff boundary*
- **Why it fails**: The calculation is wrong — it measures from diff center instead of edge. The actual minimum should be `0.19 + licon_sz/2 = 0.285` from diff boundary
- **Affected**: All MOSFETs (critical)

#### 4. **Poly overlap of poly contact < 0.08um (licon.8a)** — 80+ violations
**Rule**: `poly overlap of poly contact < 0.08um in one direction (licon.8a)`
**Root Cause**: Poly bus enclosure of gate LICON insufficient
**Source**: `mosfet.py` — line 198 (poly bus height)
**Analysis**:
- `poly_bus_h = licon_sz + 2 * _POLY_ENCL_LICON = 0.17 + 0.10 = 0.27` (line 198)
- Constraint defines minimum enclosure in **each direction** as 0.08
- Current: `_POLY_ENCL_LICON = 0.05` (line 46)
- **Why it fails**: 0.05 < 0.08 minimum required
- **Affected**: All multi-finger MOSFETs (any device with gate contact bus)

#### 5. **Poly overlap of poly contact < 0.05um (licon.8)** — 12 violations
**Rule**: `poly overlap of poly contact < 0.05um (licon.8)`
**Root Cause**: Single-finger gate poly extension too narrow
**Source**: `mosfet.py` — lines 211-219 (single-finger gate extension)
**Analysis**:
- Single-finger gates extend via separate poly rectangles
- No poly bus connects them; each gate extends individually
- **Why it fails**: Horizontal enclosure may fall below 0.05 when poly width is exactly `gate_l = 0.15`
- The gate width at the contact region is only the drawn gate length (0.15), but should have margin on each side
- **Affected**: Single-finger devices only

#### 6. **Poly contact width < 0.17um (licon.1)** — 12 violations
**Rule**: `poly contact width < 0.17um (licon.1)`
**Root Cause**: Gate LICON sized at exactly DRC minimum
**Source**: `mosfet.py` — line 223-226
**Analysis**:
- Gate LICON is drawn at exactly `licon_sz = 0.17` from DRC rules
- In combined gerber layers, dimensional tolerance may push below minimum
- **Why it fails**: No margin for floating-point rounding in gdstk output
- **Affected**: All MOSFETs

---

### **CRITICAL: Contact/via violation cluster**

#### 7. **N-diffusion contact width < 0.17um (licon.1)** — 24 violations
**Rule**: `N-diffusion contact width < 0.17um (licon.1)`
**Root Cause**: S/D LICON sized at exactly minimum
**Source**: `mosfet.py` — lines 159-163
**Analysis**:
- Same issue as gate LICON (line 68, licon_sz = 0.17)
- **Affected**: All N-channel MOSFETs

#### 8. **P-diffusion contact width < 0.17um (licon.1)** — 12 violations
**Rule**: `P-diffusion contact width < 0.17um (licon.1)`
**Root Cause**: Same as N-diffusion contact
**Source**: `mosfet.py` — lines 159-163
**Affected**: All P-channel MOSFETs

#### 9. **Poly1 contact spacing < 0.17um (licon.2)** — 12 violations
**Rule**: `Poly1 contact spacing < 0.17um (licon.2)`
**Root Cause**: Gate contact spacing constrained by pitch and width
**Source**: `mosfet.py` — lines 221-227 (gate LICON + LI1)
**Analysis**:
- Single gate LICON in the middle of the device
- When placed between diffusion-based S/D LICONs, all three must maintain 0.17 spacing
- **Why it fails**: Geometric constraint — the `sd_contact_w = poly_pitch - gate_l = 0.50 - 0.15 = 0.35`
  leaves only 0.175 space on each side of the central gate for S/D contacts
- **Affected**: Single-finger MOSFETs

#### 10. **Diffusion contact spacing < 0.17um (licon.2)** — 12 violations
**Rule**: `Diffusion contact spacing < 0.17um (licon.2)`
**Root Cause**: S/D LICON array spacing too tight
**Source**: `mosfet.py` — lines 157-163
**Analysis**:
- S/D LICONs placed vertically with `licon_pitch = licon_sz + licon_sp = 0.17 + 0.17 = 0.34`
- Adjacent fingers place S/D contacts side-by-side at distance `poly_pitch = 0.50`
- **Why it fails**: With multiple S/D regions, the minimum horizontal spacing becomes function of finger geometry
- **Affected**: All multi-finger MOSFETs

#### 11. **Diffusion contact to gate < 0.055um (licon.11)** — 40+ violations
**Rule**: `Diffusion contact to gate < 0.055um (licon.11)`
**Root Cause**: S/D LICON clearance from gate poly insufficient
**Source**: `mosfet.py` — lines 80-82 (sd_contact_w calculation)
**Analysis**:
- `sd_contact_w = max(licon_sz + 2 * _LICON_GATE_SP, ...)` where `_LICON_GATE_SP = 0.055` (line 39)
- This is the **edge-to-edge** distance, but the rule (licon.11) measures **center-to-center** to the gate edge
- **Why it fails**: Calculation is correct for edge spacing, but the rule applies to center spacing
  - S/D LICON center is at `sx = -half_arr_w + sd_contact_w/2`
  - Gate edge is at `gx ± gate_l/2`
  - Distance = `poly_pitch/2 - gate_l/2 - 0.055 = 0.25 - 0.075 - 0.055 = 0.12` > 0.055 ✓
  - But the implementation may place some contacts closer due to rounding
- **Affected**: All MOSFETs

#### 12. **mcon.width < 0.17um (mcon.1)** — 40 violations
**Rule**: `mcon width < 0.17um (mcon.1)`
**Root Cause**: MCON sized at minimum
**Source**: `mosfet.py` — lines 174-177 (MCON on S/D), 246-250 (MCON on gate)
**Analysis**:
- `mcon_sz = DRC.MCON_SZ = 0.17` (line 72)
- **Affected**: All MOSFETs

#### 13. **mcon.spacing < 0.19um (mcon.2)** — 4 violations
**Rule**: `mcon spacing < 0.19um (mcon.2)`
**Root Cause**: MCON array spacing or routing via spacing
**Source**: `mosfet.py` (MCON on S/D) or `router.py` (via_stack routing)
**Analysis**:
- S/D MCONs are single (not arrays), so unlikely from MOSFET primitive
- More likely from routing vias in the cell-level design
- **Affected**: Limited to routing areas

#### 14. **Metal1 overlap of Via1 < 0.03um in one direction (via.5a - via.4a)** — 16 violations
**Rule**: `Metal1 overlap of Via1 < 0.03um in one direction (via.5a - via.4a)`
**Root Cause**: MET1 pad enclosure of VIA (MCON/VIA) insufficient
**Source**: `mosfet.py` — lines 185-189 (MET1 on S/D), 257-261 (MET1 on gate)
**Analysis**:
- `m1_enc = DRC.MCON_ENCL_MET1_WIDE = 0.06` (line 76)
- MET1 width: `m1_w = mcon_sz + 2 * m1_enc = 0.17 + 0.12 = 0.29`
- Actual MET1 enclosure: 0.06 (should be >= 0.03 in min direction) — this is OK!
- **Why it still fails**: The DRC check may be stricter than the minimum stated
- Or: In combined GDS, overlapping shapes from adjacent cells create insufficient overlap
- **Affected**: All MOSFETs + routing

---

### **Diffusion-related violations**

#### 15. **Diffusion spacing < 0.27um (diff/tap.3)** — 12 violations
**Rule**: `Diffusion spacing < 0.27um (diff/tap.3)`
**Root Cause**: Adjacent S/D regions in multi-finger devices too close
**Source**: `mosfet.py` — lines 112-116 (single diff region per device) + hierarchical placement in cell
**Analysis**:
- Each MOSFET creates a single continuous DIFF region covering all fingers
- The issue occurs when MOSFETs are placed adjacent (side-by-side) in higher-level cells
- **Why it fails**: Cells are placed with minimal spacing, causing diff-to-diff violations
- **Affected**: Cell-level routing issues in comparator/CDAC/inverter blocks

#### 16. **N-Diffusion spacing to N-well < 0.34um (diff/tap.9)** — 4 violations
**Rule**: `N-Diffusion spacing to N-well < 0.34um (diff/tap.9)`
**Root Cause**: NFET of inverter or other block placed too close to NWELL
**Source**: Hierarchical placement in `_inverter`, `_strongarm`, `_cdac`, etc.
**Analysis**:
- PMOS devices have NWELL
- NMOS devices have no NWELL
- When NMOS is placed adjacent to PMOS with insufficient spacing, this rule is violated
- **Affected**: Inverters, CMOS switches, CDAC blocks

#### 17. **N-well spacing < 1.27um (nwell.2a)** — 4 violations
**Rule**: `N-well spacing < 1.27um (nwell.2a)`
**Root Cause**: Two PMOS NWELL regions (from separate devices) spaced too close
**Source**: Cell-level placement in `_inverter`, `_strongarm`, etc.
**Analysis**:
- When two PMOS devices are placed side-by-side (e.g., cross-coupled pair in latch)
- Their NWELL regions extend beyond the DIFF by `NWELL_ENCL_DIFF = 0.18` (line 129)
- Total NWELL from both devices creates spacing violation when devices are < 1.27 apart
- **Affected**: PMOS pairs in comparator latch, reset stage

---

### **Metal stack violations**

#### 18. **Metal1 spacing < 0.14um (met1.2)** — 4 violations
**Rule**: `Metal1 spacing < 0.14um (met1.2)`
**Root Cause**: MET1 routing or bus too close
**Source**: `router.py` (route_straight, route_L) or cell-level MET1 buses in MOSFETs
**Analysis**:
- S/D MET1 buses from adjacent fingers/devices placed too close
- **Why it fails**: Routing doesn't enforce MET1 spacing constraints explicitly
- **Affected**: Routing and cell-level interconnect

#### 19. **Metal1 width < 0.14um (met1.1)** — 14 violations
**Rule**: `Metal1 width < 0.14um (met1.1)`
**Root Cause**: MET1 bus or routing width below minimum
**Source**: `mosfet.py` (MET1 buses, lines 274-290), or `router.py` (routing)
**Analysis**:
- MET1 bus height may be calculated too small due to minimum-area expansion rounding
- **Affected**: Multi-source/drain buses in MOSFETs

#### 20. **Metal2 overlap of Via1 < 0.03um in one direction (met2.5 - met2.4)** — 8 violations
**Rule**: `Metal2 overlap of Via1 < 0.03um in one direction (met2.5 - met2.4)`
**Root Cause**: MET2 pad doesn't fully enclose VIA spacing
**Source**: Routing in `router.py` (route_straight, route_L)
**Analysis**:
- VIA enclosure rule for MET2: `VIA_ENCL_MET2 = 0.055` (line 62)
- `_draw_wire` doesn't explicitly expand metal for via enclosure
- **Why it fails**: When a via is placed at endpoint of a routing wire, the wire width may not extend via enclosure fully
- **Affected**: Routing between MET1 and MET2 (ADC_GO signal, VREF bus)

#### 21. **Metal2 minimum area < 0.0676um^2 (met2.6)** — 4 violations
**Rule**: `Metal2 minimum area < 0.0676um^2 (met2.6)`
**Root Cause**: MET2 routing segment too short and narrow
**Source**: `router.py` — lines 101-105 (vertical wire area expansion)
**Analysis**:
- `_draw_wire` expands wires to meet minimum area: `needed_h = min_area / rect_w`
- For MET2: min_area = 0.0676, if width = 0.14, needed_h = 0.48 um
- But the actual wire length may be shorter than this, resulting in insufficient area
- **Affected**: Short MET2 segments in ADC_GO routing

#### 22. **Metal3 spacing < 0.3um (met3.2)** — 10 violations
**Rule**: `Metal3 spacing < 0.3um (met3.2)`
**Root Cause**: MET3 wires from MIM cap bottom plates spaced too close
**Source**: `_cdac` function (lines 337-351) — CDAC top plate MET4 bus routing
**Analysis**:
- Via stacks connect cap TOP plates to MET4 bus (lines 346-351)
- The intermediate MET3 segments are created by `route_straight` and `via_stack`
- When multiple caps are arrayed, MET3 segments from different caps may be too close
- **Affected**: CDAC blocks (common-centroid cap array)

#### 23. **Metal3 > 3um spacing to unrelated m3 < 0.4um (met3.3d)** — 10 violations
**Rule**: `Metal3 > 3um spacing to unrelated m3 < 0.4um (met3.3d)`
**Root Cause**: Long MET3 traces (VREF bus in CDAC) spaced < 0.4um apart
**Source**: `_cdac` function (lines 385-393) — VREF MET3 horizontal bus
**Analysis**:
- VREF bus is drawn as continuous MET3 rectangle (lines 387-391)
- When two CDAC blocks are placed near each other, their VREF buses may be < 0.4um apart
- **Affected**: CDAC blocks in adc_unit hierarchy

#### 24. **Metal4 spacing < 0.3um (met4.2)** — 8 violations
**Rule**: `Metal4 spacing < 0.3um (met4.2)`
**Root Cause**: MET4 buses (VDD/VSS straps, VREF bus) spaced too close
**Source**: `interleaved_adc.py` — lines 729-733 (VREF bus), 796-814 (power straps)
**Analysis**:
- Top-level routing draws MET4 rectangles for power and VREF
- When units are placed close together, MET4 traces may be < 0.3um apart
- **Affected**: Top-level `interleaved_adc` cell

#### 25. **Metal4 > 3um spacing to unrelated m4 < 0.4um (met4.5b)** — 8 violations
**Rule**: `Metal4 > 3um spacing to unrelated m4 < 0.4um (met4.5b)`
**Root Cause**: Long MET4 signal traces or buses spaced < 0.4um apart
**Source**: Similar to met3.3d, applies to MET4 (power, VREF, ADC_GO connection)
**Affected**: Top-level cell

---

### **Capacitor-specific violations**

#### 26. **MiM cap spacing < 0.84um (capm.2a)** — 4 violations
**Rule**: `MiM cap spacing < 0.84um (capm.2a)`
**Root Cause**: CAPM layer (MIM cap marker) array spacing too tight
**Source**: `_cdac` function (lines 313-331) — common-centroid cap arrangement
**Analysis**:
- Cap array pitch: `cap_pitch = C_UNIT_SIDE + DRC.CAPM_SP = 5.0 + 0.84 = 5.84`
- But `DRC.CAPM_SP = 0.84` is the **minimum spacing between caps**
- Current implementation places caps at exactly: `cap_pitch = 5.0 + 0.84 = 5.84`
- When MET3 enclosure is added (line 50-55), the actual CAPM boundary is `C_UNIT_SIDE/2 + m3_encl = 2.5 + 0.14 = 2.64` per side
- Distance between adjacent caps: `5.84 - 2*2.64 = 0.56` < 0.84 VIOLATION!
- **Why it fails**: `cap_pitch` calculation doesn't account for MET3 enclosure reducing available spacing
- **Affected**: CDAC blocks (u0_cdac, u1_cdac)

---

### **Local interconnect violations**

#### 27. **Local interconnect spacing < 0.17um (li.3)** — 4 violations
**Rule**: `Local interconnect spacing < 0.17um (li.3)`
**Root Cause**: LI1 routing too close
**Source**: Routing in `router.py` or S/D LI1 strips in MOSFETs (lines 165-171)
**Analysis**:
- LI1 strips over S/D contacts are spaced at `poly_pitch = 0.50` center-to-center
- Width of each strip: `li_w = 0.33`
- Gap between adjacent strips: `0.50 - 0.33 = 0.17` — **exactly at minimum!**
- Floating-point rounding may push below minimum
- **Affected**: Multi-finger MOSFETs

#### 28. **Core local interconnect spacing < 0.14um (li.c2)** — 40 violations
**Rule**: `Core local interconnect spacing < 0.14um (li.c2)`
**Root Cause**: LI1 padding around gate contact too close to adjacent LI1
**Source**: `mosfet.py` (lines 238-243) — gate contact LI1 pad
**Analysis**:
- Gate LI1 pad: `li_pad = licon_sz + 2 * li_enc = 0.17 + 0.16 = 0.33` (line 238)
- Gate is centered at x=0, so LI1 extends from -0.165 to +0.165
- Adjacent S/D LI1 strips are at x ≈ ±0.25
- Gap to gate LI1: `0.25 - 0.165 = 0.085` < 0.14 — VIOLATION!
- **Affected**: All MOSFETs

---

### **Routing and top-level violations**

#### 29. **Can't overlap those layers** — 60 violations
**Rule**: `This layer can't abut or partially overlap between subcells`
**Root Cause**: Instance boundaries in GDS with overlapping geometry
**Source**: `Instance.add_to(cell)` in compose.py and cell-level placement functions
**Analysis**:
- When cell instances are added to parent, their geometries are union'd at the GDS level
- Some layers (like NWELL, implants) can't overlap between subcells without triggering this rule
- **Why it fails**: Instances are placed too close or overlapping
- **Affected**: PMOS pairs in comparator latch; inverter/switch stacks

#### 30. **nFET cannot abut P-diffusion (diff/tap.3)** — 4 violations
**Rule**: `nFET cannot abut P-diffusion (diff/tap.3)`
**Root Cause**: NMOS and PMOS diffusion placed adjacent with no spacing
**Source**: Hierarchical placement in cell-level functions (inverter, switches, etc.)
**Analysis**:
- When NFET and PFET are vertically stacked in an inverter (lines 76-86 in interleaved_adc.py)
- The S/D diffusion of NFET (top) and PFET (bottom) must be spaced by `DIFF_SP = 0.27`
- Current placement uses `n_inst.place(0, 0)` and `p_inst.place(0, p_y)` where `p_y = n_inst.bbox()[1][1] + 0.5`
- The gap (0.5) looks sufficient, but must verify that actual diff boundaries have correct spacing
- **Why it fails**: The 0.5um gap is between cell origins/boundaries, not diff-to-diff
- **Affected**: Inverters, CMOS switches, CDAC inverter array

---

## Summary by Severity and Root Category

### **Category 1: Poly/Contact Geometry (MOSFET Primitive)**
- **Total violations**: ~300+
- **Root cause**: Gate pitch doesn't respect `POLY_SP` rule
- **Files affected**: `mosfet.py` (lines 97, 136-146, 194-227)
- **Specific issues**:
  1. Gate pitch calculation missing poly spacing constraint (line 97)
  2. Gate contact gap calculation wrong (licon.14 issue, line 194)
  3. Poly enclosure of gate LICON too small (lines 46, 198)
  4. S/D contact clearance from gate incorrect (lines 80-82)
  5. All contact sizes at minimum with no margin (lines 68-72)

### **Category 2: Diffusion Spacing (Hierarchical Placement)**
- **Total violations**: ~60+
- **Root cause**: MOSFETs placed side-by-side with insufficient spacing
- **Files affected**: `interleaved_adc.py`, cell-level functions (_inverter, _strongarm, _cdac, etc.)
- **Specific issues**:
  1. No explicit diffusion spacing constraint in placement logic
  2. Instances use geometric centers, not diff boundaries, for spacing

### **Category 3: MIM Capacitor Array (CDAC)**
- **Total violations**: ~4
- **Root cause**: Capacitor pitch doesn't account for MET3 enclosure
- **Files affected**: `_cdac` function (lines 309-331)
- **Specific issues**:
  1. Cap pitch = 5.0 + 0.84, but MET3 enclosure (0.14 per side) reduces effective spacing

### **Category 4: Routing (Router and Top-level)**
- **Total violations**: ~200+
- **Root cause**: Metal trace spacing and via enclosure not fully enforced
- **Files affected**: `router.py` (lines 82-136), `interleaved_adc.py` (lines 338-843)
- **Specific issues**:
  1. VIA enclosure in MET1/MET2 insufficient (lines 100-105)
  2. MET4 spacing not enforced between top-level buses
  3. Power/signal routing overlaps with minimum spacing

### **Category 5: Hierarchical Assembly Issues**
- **Total violations**: ~60
- **Root cause**: Cell instances overlap or abut at boundaries
- **Files affected**: `interleaved_adc.py` (cell instantiation), `compose.py` (Instance class)
- **Specific issues**:
  1. NWELL overlap between adjacent PMOS devices
  2. Instance boundary alignment causes layer violations

---

## Suggested Fixes (Priority Order)

### **Fix 1: Gate poly spacing in mosfet.py (CRITICAL — affects 300+ violations)**
**File**: `project/layout/primitives/mosfet.py`
**Lines**: 46, 97, 136-146, 194-195

**Change 1.1**: Add poly spacing to pitch calculation
```python
# Line 46
_POLY_ENCL_LICON = 0.08  # was 0.05, now matches licon.8 requirement

# Line 97 - add poly spacing constraint
min_pitch_poly = 2 * gate_l + DRC.POLY_SP  # ~0.41
poly_pitch = max(min_pitch_li, min_pitch_sd, min_pitch_m1, min_pitch_poly)
```

**Change 1.2**: Fix gate contact gap for licon.14 compliance
```python
# Line 194 - correct the spacing calculation
# licon.14 requires: distance from contact edge to diffusion edge >= 0.19
# Our contact center is at gc_x = 0, half-diff is half_wf
# So distance from contact center to diff edge = half_wf + poly_ext + gap_to_contact_edge
# We want: poly_ext + gap_to_contact_edge >= 0.19 + licon_sz/2
gc_gap = max(0.19 + DRC.LICON_SZ/2 - poly_ext, 0.05)  # was 0.105
```

**Change 1.3**: Add margin to contact sizes
```python
# Line 68-72 - add small margin (0.01um) to handle GDS rounding
licon_sz = DRC.LICON_SZ + 0.01  # was 0.17, now 0.18
mcon_sz = DRC.MCON_SZ + 0.01    # was 0.17, now 0.18
```

---

### **Fix 2: MIM capacitor pitch in _cdac (CRITICAL — affects u0_cdac, u1_cdac, 224 violations)**
**File**: `project/layout/cells/interleaved_adc.py`
**Lines**: 309

**Change**: Account for MET3 enclosure in cap pitch
```python
# Line 309 - correct cap pitch
m3_encl = DRC.CAPM_ENCL_MET3  # 0.14
required_spacing = DRC.CAPM_SP  # 0.84
# Space between MET3 edges = required_spacing
# Actual pitch = 2 * m3_encl + C_UNIT_SIDE + required_spacing
cap_pitch = 2 * m3_encl + C_UNIT_SIDE + DRC.CAPM_SP
# was: cap_pitch = C_UNIT_SIDE + DRC.CAPM_SP  (5.84)
# now: cap_pitch = 0.28 + 5.0 + 0.84 = 6.12
```

---

### **Fix 3: Hierarchical placement spacing in cell builders (IMPORTANT — affects ~60 violations)**
**Files**: All cell-level functions in `interleaved_adc.py` (_inverter, _strongarm, _cdac, _sar_logic, adc_unit)

**Change 3.1**: Enforce diffusion spacing in inverter (_inverter function, lines 76-86)
```python
# Line 84 - increase gap between NFET and PFET
# Current: p_y = n_inst.bbox()[1][1] + 0.5
# Need: gap = max(0.5, DRC.DIFF_SP - 2*max(n_bbox_h, p_bbox_h))
n_bbox = n_inst.bbox()
p_bbox_h = max(pfet_expected_h, 2.0)  # estimate PFET height
required_gap = DRC.DIFF_SP + (n_bbox[1][1] - n_bbox[0][1]) + p_bbox_h
p_y = n_inst.bbox()[1][1] + required_gap
```

**Change 3.2**: Enforce N-well spacing in comparator (_strongarm function, lines 227-253)
```python
# After PMOS latch placement (lines 227-230)
# Check NWELL distance: should be > NWELL_SP = 1.27
# Current placement: xpp_inst at x=-1.5, xpn_inst at x=+1.5 → distance 3.0 ✓
# But verify in actual bbox expansion
```

**Change 3.3**: Enforce diffusion spacing in CDAC switches/inverters (_cdac function, lines 353-376)
```python
# Lines 366, 375 - add spacing calculation
# Switches and inverters are stacked; ensure sufficient y-spacing
inv_y = sw_row_y - 4.0  # current gap is 4.0
# Verify: max(sw_height) + max(inv_height) + DRC.DIFF_SP should fit
# Current appears OK, but verify bbox
```

---

### **Fix 4: Routing via enclosure in router.py (IMPORTANT — affects ~20 violations)**
**File**: `project/layout/routing/router.py`
**Lines**: 82-135 (_draw_wire)

**Change**: Expand metal pads to ensure VIA enclosure
```python
# Line 100-128 - after calculating wire geometry, expand for via enclosure
# If a via will be placed at endpoints, need to ensure metal extends via_enclosure

def _draw_wire_with_via_prep(cell: gdstk.Cell, x1: float, y1: float,
                              x2: float, y2: float, layer: tuple[int, int],
                              width: float, via_at_ends: bool = False) -> None:
    """Draw wire with VIA enclosure if vias will connect."""
    hw = width / 2
    # ... existing wire drawing code ...

    # After wire, if via_at_ends:
    if via_at_ends:
        # Ensure metal encloses any VIA that might be at (x1,y1) or (x2,y2)
        via_layer_above = _get_via_above(layer)
        via_sz = ...  # lookup via size
        encl = ...    # lookup via enclosure for this metal
        # Pad metal width if needed
        ...
```

---

### **Fix 5: MET3/MET4 spacing at top level (IMPORTANT — affects ~20 violations)**
**File**: `project/layout/cells/interleaved_adc.py`
**Lines**: 729-733, 796-814

**Change**: Add spacing constraints to top-level routing
```python
# Lines 729-733 (VREF bus routing)
# Ensure MET4 bus doesn't conflict with other MET4 (power straps)
vref_y = u0.port("VREF").center[1]
min_dist_to_power = DRC.MET4_SP + VREF_BUS_W/2 + POWER_STRAP_W/2
# Add check or adjust vref_y if too close to vdd_strap_y or vss_strap_y

# Lines 796-814 (power straps)
# Ensure vdd_strap and vss_strap have DRC spacing to other MET4
# May need to add guard margin or adjust strap placement
```

---

### **Fix 6: NWELL overlaps in comparator and cell stacks (MEDIUM — affects ~60 violations)**
**Files**: `interleaved_adc.py` (_strongarm function), and other cell-level builders

**Change**: Control NWELL boundaries or add spacing
```python
# _strongarm function, PMOS placement (lines 222-230)
# Current: cross-coupled PMOS pair at x=±1.5
# NWELL from each extends by NWELL_ENCL_DIFF = 0.18
# NWELL from left PMOS: [-1.5 - w_width/2 - 0.18, 1.5 - w_width/2 + 0.18]
# Distance between NWELLs depends on device width
# For LATCH_P_W = 4.5, nf=6: per-finger width ~ 0.75
# Total width contribution per side: ~2.5
# NWELL-to-NWELL: distance from right edge of left PMOS to left edge of right PMOS
# = 3.0 - 2*(2.5 + 0.18) = ... (check actual bbox)

# Fix: If NWELL spacing is violated, explicitly reduce NWELL size or increase device spacing
```

---

## Implementation Roadmap

### **Phase 1: Critical Fixes** (300+ violations)
1. Fix mosfet.py gate pitch calculation and contact spacing
2. Fix CDAC capacitor pitch
3. Add margin to contact sizes (handle GDS rounding)

### **Phase 2: Important Fixes** (~100 violations)
4. Fix routing via enclosure (router.py)
5. Fix hierarchical placement spacing (cell builders)
6. Fix MET3/MET4 top-level routing

### **Phase 3: Medium Fixes** (~60 violations)
7. Fix NWELL overlaps (may require redesign of latch layout or spacing increase)
8. Add explicit diffusion spacing rules to placement logic

### **Phase 4: Polish** (remaining < 50 violations)
9. Fine-tune layer enclosures and widths
10. Validate all fixes with DRC re-run

---

## Files to Modify

1. **`project/layout/primitives/mosfet.py`** — Gate pitch, contact spacing, poly enclosure
2. **`project/layout/cells/interleaved_adc.py`** — CDAC pitch, cell spacing, routing
3. **`project/layout/routing/router.py`** — Via enclosure handling
4. **`project/layout/drc.py`** — May need to add/adjust constants if rules are too aggressive

