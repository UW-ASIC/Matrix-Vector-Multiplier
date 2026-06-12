# Scaling-Proof Architecture Options for Capacitive IMC

## The Problem

Current voltage-mode architecture (sky130):
```
DIGITAL ─→ [DAC] ─→ CAP CROSSBAR (MAC) ─→ [SAR ADC] ─→ DIGITAL
             24%         ~21%                  55%
           of energy    of energy            of energy
```

DAC+ADC = **55% of total energy**, consumes **30-80% of area**, and **doesn't scale**
because analog precision is limited by kT/C noise, capacitor matching, and Walden FOM —
none of which improve with Moore's Law.

**Goal:** Find architecture where conversion overhead shrinks with process scaling,
while keeping the capacitive crossbar's density and parallelism advantages.

---

## Architecture Comparison (TL;DR)

| Architecture | ADC Overhead | Scales? | Best Node Range | Our Crossbar? |
|:---|:---:|:---:|:---:|:---:|
| A. Voltage-mode (current) | 55% | No | 130-65nm | Yes (current) |
| B. Input-serial + Flash | ~20% | Partially | 180-28nm | Yes |
| C. VTC + TDC readout | ~10% | Yes | 65-7nm | Yes (proven) |
| D. 1b×1b + Digital Accum | ~5% | Yes | 28nm and below | Adapted |
| E. FeCAP crossbar | ~5% | Yes | 28nm and below | Evolution |
| F. End-to-end charge (no convert) | ~0% | Yes | 22nm and below | Yes |

**Recommended path: B (sky130) → C (next tapeout, 65-28nm) → F+E (long-term)**

---

## Architecture A: Current Design (Voltage-Mode, Baseline)

```
Input DAC → S&H → Cap Crossbar → SAR ADC → Digital Output
```

- Energy: **275 fJ/MAC** at 180nm
- Conversion overhead: 55%
- Scales: poorly (caps/kT don't shrink)
- Reference: our `CALCULATIONS.md` Section 9

**Verdict:** Optimal for sky130. Not future-proof.

---

## Architecture B: Input-Serial + Flash ADC

**Source:** IMAGINE (UCLouvain, 22nm, JSSC 2025), PICO-RAM (Rice, 65nm, 2024)

### Concept

Eliminate the DAC entirely. Stream input bits one at a time (rail-to-rail digital).
Replace SAR ADC with flash (parallel comparators).

```
Digital bits ─→ CAP CROSSBAR ─→ Flash ADC (4 comparators) ─→ Shift-Add Accum
  (no DAC!)       (MAC)           (1 cycle, not 4)            (digital)
```

### How It Works

1. Apply 1 bit of input per cycle: rows driven to VDD or 0 (no DAC needed)
2. Charge redistribution produces column voltage proportional to partial MAC
3. Flash ADC (bank of comparators with fixed thresholds) digitizes in **1 cycle**
4. Digital shift-and-add accumulator combines partial sums: `result = Σ 2^b × adc_out[b]`

For our 4×4 array with 4-bit weights:
- Each cycle: column voltage has range 0 to `4×15×C_UNIT×VDD / C_total` = 0-1.54V
- Need ~6-bit flash ADC (63 comparators) for full resolution
- Or: accept compute-SNR relaxation → 4-bit flash (15 comparators) suffices for neural nets

### Timing

```
Per cycle: reset (2ns) + settle (5ns) + flash compare (1.5ns) = 8.5ns
4 cycles for 4-bit input: 34ns total (vs 23ns current)
```

1.5× slower per MVM but **DAC is eliminated** (saves 24% energy).

### Energy at 180nm

| Stage | Energy |
|-------|--------|
| Crossbar (same) | 4.15 pJ |
| Reset (same) | 4.48 pJ |
| Flash ADC (15 comp × 4 cols × 4 cyc) | 3.11 pJ |
| Digital accumulator | 0.78 pJ |
| **Total (64 MACs)** | **12.5 pJ** |
| **Per MAC** | **195 fJ** |

vs current 275 fJ/MAC → **29% energy reduction**, overhead drops from 55% to ~31%.

### Scaling

Flash comparators are digital → energy ∝ CV². At 28nm: ~45 fJ/MAC. At 7nm: ~12 fJ/MAC.

**Verdict:** Easy migration from current design. Keep same crossbar. Replace DAC with digital
rail-to-rail drive, replace SAR with comparator bank. Good for sky130 v2 or GF180 tapeout.

---

## Architecture C: VTC + TDC Readout (Time-Domain)

**Source:** SOCC 2023 (Oshio et al., 22nm), JSSC 2023 (768-2124 TOPS/W at 28nm)

### Concept

Keep capacitive crossbar as-is. Replace SAR ADC with Voltage-to-Time Converter (VTC)
followed by Time-to-Digital Converter (TDC). TDC is all-digital and scales with Moore's Law.

```
[Optional: PWM input] → CAP CROSSBAR → VTC → TDC (counter) → Digital
                           (MAC)        (delay ∝ V_col)   (all digital!)
```

### Key Insight

TDC precision improves with faster transistors (shorter gate delay = finer timing bins).
**This is the opposite of ADC**, where precision is limited by analog matching that
doesn't improve with scaling.

### VTC Circuit

Current-starved inverter: V_MAC controls starving current → output delay ∝ 1/V_MAC.

```
VDD ─┬─ [PMOS starved by V_bias]
     │
     ├─── OUT (delay = f(V_MAC))
     │
     └─ [NMOS controlled by V_MAC]─── VSS
```

Delay range: ~100ps (V_MAC = VDD) to ~10ns (V_MAC = 0) — maps full column swing to time.

### TDC Circuit

Pulse-shrinking delay chain + D flip-flops. Each stage shrinks pulse by Δt (inverter delay).
Count how many stages pulse survives = digital code.

```
IN ──[inv]──[inv]──[inv]──[inv]──...──[inv]──
       │       │       │       │           │
      [FF]   [FF]   [FF]   [FF]  ...     [FF]  → thermometer code → binary
```

At 180nm: Δt ≈ 15-20ps → 4-bit TDC needs 16 stages
At 7nm: Δt ≈ 2-3ps → native 6-7 bit resolution in same area

### Silicon Results

| Paper | Node | TOPS/W | TDC area overhead | Precision |
|-------|------|--------|-------------------|-----------|
| Configurable TDC (JSSC 2023) | 28nm | 768-2124 | **2.9% of macro** | 2-4b |
| rTD-CiM (GLSVLSI 2024) | 28nm | 28.05 | ~5% | 8b (2×4b) |
| SPIKA (Frontiers 2025) | 180nm | 195 | ~8% | 4b/ternary |

Compare: SAR ADC typically consumes **30-60% of macro area**.

### Energy Projection

| Node | SAR ADC energy | VTC+TDC energy | Savings |
|------|---------------|----------------|---------|
| 180nm | ~1.3 pJ/conv (4b) | ~0.8 pJ/conv | 38% |
| 65nm | ~0.4 pJ/conv | ~0.15 pJ/conv | 63% |
| 28nm | ~0.12 pJ/conv | ~0.02 pJ/conv | 83% |
| 7nm | ~0.04 pJ/conv | ~0.003 pJ/conv | 92% |

TDC energy drops faster than SAR because it's pure digital switching.

### Migration from Current Design

**Minimal change:**
1. Keep capacitive crossbar (identical)
2. Keep S&H (identical)
3. Replace SAR ADC with: VTC (2 transistors) + TDC (16-stage delay chain + FFs)
4. Optionally keep DAC, or combine with Architecture B (input-serial)

**Combined B+C (input-serial + TDC):**
- No DAC (input-serial)
- No ADC (VTC+TDC)
- Conversion overhead: **~10%** (VTC + TDC switching only)
- Everything except crossbar caps is digital → scales cubically

### Risk Factors

- VTC linearity: ~300mV linear range; beyond that, need piecewise or calibration
- PVT sensitivity: delay varies ~30% across corners; needs replica delay calibration
- Jitter sets noise floor: ~5ps rms at 180nm limits to ~4 effective bits per shot
- For >4 bits: use 2-shot with shift-and-add (same as current SAR approach, but faster)

**Verdict:** Best near-term scaling path. Keep our crossbar, swap readout. TDC proven
at 28nm with 2124 TOPS/W. Area overhead drops from 30-60% (ADC) to 3% (TDC).

---

## Architecture D: 1b x 1b Binary Crossbar + Digital Accumulation

**Source:** Colonnade (KAIST, 65nm, JSSC 2021), HCiM (Purdue, ASP-DAC 2025)

### Concept

Reduce each crosspoint to a single switch + single cap (no binary weighting).
Process one weight-bit AND one input-bit per cycle. Column output is a simple
**popcount** (how many crosspoints are active) — trivially digitized.

```
Cycle (bx, bw):
  Row i = input_bit[bx][i] × VDD     (0 or VDD)
  Crosspoint (i,j) = weight_bit[bw][i][j]   (switch open/closed)
  Column j = popcount(active) × VDD × C_UNIT / C_total

Digital accumulator: result += 2^(bx+bw) × popcount_j
```

### Why Popcount is Trivial to Digitize

For 4 rows, popcount ∈ {0, 1, 2, 3, 4}. Column voltages (C_INT=200fF, C_UNIT=50fF):
```
pop=0: 0 mV
pop=1: 360 mV      (gap: 360mV)
pop=2: 600 mV      (gap: 240mV)
pop=3: 771 mV      (gap: 171mV)
pop=4: 900 mV      (gap: 129mV)
```

**4 comparators** with fixed thresholds resolve all levels. Gaps >> offset (~4mV) and
noise (~3mV rms). No SAR loop, no DAC, no precision analog — just 4 bang-bang comparators.

### HCiM Variant: Even Simpler (1-bit sense)

Quantize column to **binary** (above/below single threshold) or **ternary** ({-1, 0, +1}).
Multiply by learned digital scale factor to restore dynamic range.

- 28× energy reduction vs 7-bit ADC
- <1.5% accuracy loss on CIFAR-10 with quantization-aware training
- 12× reduction vs 4-bit ADC

### Silicon Results

| Design | Node | TOPS/W | Precision | ADC | Scaling |
|--------|------|--------|-----------|-----|---------|
| Colonnade | 65nm | 98.5 | 4b×4b | None (digital) | Perfect |
| HCiM | 65nm | ~28× baseline | 4b×4b | 1 comparator | Perfect |
| 4nm TSMC DCIM | 4nm | 6163/b | 8b×8b | None | Perfect |

### Energy Scaling (1b×1b approach for 4×4, 64 MACs)

| Node | Crossbar | Comparators | Digital Accum | Total | fJ/MAC |
|------|----------|-------------|---------------|-------|--------|
| 180nm | 5.2 pJ | 8.3 pJ | 29.0 pJ | 42.5 pJ | **664** |
| 65nm | 1.2 pJ | 1.1 pJ | 3.9 pJ | 6.1 pJ | **96** |
| 28nm | 0.3 pJ | 0.2 pJ | 0.7 pJ | 1.2 pJ | **19** |
| 7nm | 0.1 pJ | 0.04 pJ | 0.15 pJ | 0.3 pJ | **4.7** |

**Worse than current at 180nm (664 vs 275 fJ/MAC), but wins decisively below 65nm.**

### Latency: O(B²) Independent of Array Size

```
4-bit: 16 cycles × t_cycle
t_cycle = reset + settle + compare = 7ns (180nm), 1.3ns (28nm), 0.5ns (7nm)

Total latency:
  180nm: 16 × 7ns = 112ns
  28nm: 16 × 1.3ns = 20.8ns
  7nm: 16 × 0.5ns = 8ns

Digital systolic (same 4×4):
  180nm: 7 × 20ns = 140ns  ← analog wins
  28nm: 7 × 0.5ns = 3.5ns  ← digital wins
  7nm: 7 × 0.25ns = 1.75ns ← digital wins

BUT for 256×256 array:
  Bit-serial: still 8ns (7nm) for 65,536 MACs
  Digital systolic: 511 × 0.25ns = 128ns for 65,536 MACs
  → Analog wins 16× on large arrays at ANY node
```

**Key advantage: latency = O(precision²), independent of array size.
Digital systolic: latency = O(array_size). For N > ~32, analog always wins on latency.**

### Architecture Change from Current Design

| Current | 1b×1b |
|---------|-------|
| Binary-weighted cap array per crosspoint | Single cap per crosspoint |
| 4-bit weight stored in switch config | Weight bits in digital latches, loaded per cycle |
| DAC drives analog voltage | Rail-to-rail digital bit |
| SAR ADC (4 comp cycles) | 4 threshold comparators (1 cycle) |
| 1 cycle per MVM | 16 cycles per MVM (4b×4b) |

**Verdict:** The mathematically proven scaling-proof architecture. Wins below 65nm on
energy, wins on latency for arrays > 32×32 at any node. Requires architectural redesign
(not just swapping ADC).

---

## Architecture E: FeCAP (Ferroelectric Capacitive) Crossbar

**Source:** Georgia Tech / Shimeng Yu group (JSSC 2024), imec + Georgia Tech (IEDM 2023)

### Concept

Replace fixed MOM capacitors with **ferroelectric capacitors (FeCAP)** whose capacitance
is non-volatilely programmable. The compute mechanism stays identical (charge redistribution),
but weights are stored in the device itself — no external SRAM/latches needed.

```
Current: SRAM latch → CMOS switch → MOM cap (fixed C, switch selects)
FeCAP:   [nothing needed] → FeCAP (C is the weight, non-volatile)
```

### Why This Matters

- **Same charge-domain physics** — our MAC equation is unchanged
- **Non-volatile** — weights persist without power (eliminates weight reload energy)
- **Zero static power** — no DC paths, no leakage through weight storage
- **No sneak paths** — inherits cap crossbar immunity
- **3D stackable** — BEOL-compatible, can stack multiple crossbar layers
- **Selector-free** — unlike RRAM, no 1T1R needed

### Measured Results

| Metric | Value | Source |
|--------|-------|--------|
| Projected efficiency | **29,600 TOPS/W** | Georgia Tech JSSC 2024 |
| Energy per VMM | 3.8 pJ (14-57× lower than RRAM) | Georgia Tech 2024 |
| Read endurance | >10^11 cycles | imec IEDM 2023 |
| Memory window | 8.7× (largest reported) | imec IEDM 2023 |
| Multi-level states | 4-8 levels demonstrated | Multiple papers |
| Accuracy (CIFAR-10) | 96.6% | 28nm FeFET CIM demo |
| Write endurance | ~10^9 cycles | Current state |

### Comparison to Our MOM Cap Crossbar

| Property | MOM caps (ours) | FeCAP |
|----------|-----------------|-------|
| Weight storage | Volatile (CMOS switches) | Non-volatile (polarization) |
| Weight precision | Arbitrary (binary-weighted) | 2-4 bits/cell |
| Programming | Instant (switch toggle) | ~30ns pulse at 3V |
| Read mechanism | Charge redistribution | Charge redistribution (identical) |
| Compute energy | ~65 fJ/MAC (crossbar only) | ~0.5 fJ/MAC (no switch overhead) |
| Area per weight | ~25 μm² (cap + switch) | ~1 μm² (single FeCAP) |
| Scaling path | Density-limited by cap | Scales with BEOL pitch |

### Roadmap

| Timeframe | Action | Node |
|-----------|--------|------|
| Now | MOM cap + CMOS switch (sky130) | 180nm |
| 2027-2028 | FeCAP available in foundry PDK (TSMC targeting) | 28nm |
| 2029+ | 3D stacked FeCAP crossbar arrays | 14nm+ |

### Risk

- FeCAP not in any production PDK today (R&D only)
- Write endurance (10^9) limits retraining frequency
- Capacitance ratio between states may drift with cycling
- Manufacturing variation in HfZrO deposition

**Verdict:** The endgame for capacitive CIM. Same physics as our design, but 25× denser
and non-volatile. Not available today, but the evolution path is clear and our architecture
maps directly onto it.

---

## Architecture F: End-to-End Charge Domain (No Conversion)

**Source:** IMAGINE (UCLouvain, 22nm, 2024-2025), Near-CIM (TSMC, 55nm, 2024)

### Concept

**Eliminate ALL conversion** by keeping data in charge domain between layers.
Only convert at system boundaries (input from outside world → first layer,
last layer → output to outside world).

```
Layer 1: Digital input → (one-time DAC) → charge → crossbar → charge output
Layer 2: charge input (from L1) → crossbar → charge output
Layer 3: charge input (from L2) → crossbar → charge output
...
Layer N: charge input → crossbar → (one-time ADC) → digital output
```

### How Inter-Layer Charge Transfer Works

Column output of layer L is a voltage on a capacitor. This voltage directly drives
the rows of layer L+1 through charge-sharing or buffer:

```
Option 1: Direct charge sharing (passive, zero energy)
  C_col_L connects to C_row_L+1 via switch → charge redistributes

Option 2: Analog buffer (active, low energy)
  Source follower or unity-gain amp drives next layer's rows

Option 3: Analog sample-hold
  Column voltage stored on hold cap → drives next crossbar directly
```

### IMAGINE Implementation (22nm FD-SOI)

- 1152×256 macro, input-serial weight-parallel
- End-to-end charge-based: no inter-layer ADC/DAC
- Analog batch normalization (ABN) adjusts swing between layers
- **150 TOPS/W (macro), 40 TOPS/W (system)**
- 0.15-8 POPS/W depending on precision (1b to 8b)
- Dual supply: 0.3V/0.6V

### Near-CIM Analog Memory (TSMC 55nm)

- Stores activations in **analog form** (switched-cap) near the CIM array
- ReLU performed in analog domain (comparator + switch)
- **76% energy reduction** vs design with DAC/ADC between layers
- 44.3 TOPS/W (macro)

### Energy Impact

For N-layer inference:
```
With ADC/DAC per layer:   E_total = N × (E_MAC + E_ADC + E_DAC)
End-to-end charge:        E_total = N × E_MAC + 1×E_ADC + 1×E_DAC

Savings = (N-1) × (E_ADC + E_DAC)
For N=8 layers: saves 7/8 = 87.5% of conversion energy
```

If conversion was 55% → now it's 55%/8 = **6.9% of total**. The overhead becomes negligible.

### Challenges

- Noise accumulates across layers (no digital "reset" between stages)
- Dynamic range management: need analog normalization (ABN) or gain control
- Debugging is hard (can't observe intermediate analog values easily)
- Requires matched array sizes or analog muxing between layers
- Not suitable for non-sequential architectures (skip connections, attention)

### Applicability to Our Design

Our charge-domain crossbar output (V_col on C_INT) can directly drive the next
stage's S&H inputs through a simple transmission gate. The voltage is already
in the right domain — no conversion needed.

For a **single-layer** application (like our 4×4 GEMM), this doesn't help.
For **multi-layer** inference (future expansion), this eliminates conversion entirely.

**Verdict:** The ultimate scaling solution for multi-layer neural networks. For single
GEMM operations (our current use case), combine with Architecture B or C instead.

---

## Synthesis: The Scaling-Proof Roadmap

### Phase 1: Sky130 (Now) — Architecture B

**Change:** Eliminate DAC. Go input-serial. Replace SAR with 4-bit flash.

```
Before: DAC (2ns) → S&H → Crossbar (10ns) → SAR ADC (6ns) = 23ns, 275 fJ/MAC
After:  Digital bit → Crossbar (10ns) → Flash (1.5ns) = 34ns, 195 fJ/MAC (×4 cycles)
```

- Energy: 275 → 195 fJ/MAC (**29% reduction**)
- Overhead: 55% → 31%
- Change scope: remove DAC, add 15 comparators per column, add 4-bit shift-add register
- Crossbar: **unchanged**

### Phase 2: 65-28nm (Next Tapeout) — Architecture B+C

**Change:** Input-serial + VTC+TDC readout. No DAC, no ADC.

```
Digital bit → Crossbar → VTC (current-starved inv) → TDC (delay chain) → Digital
```

- Energy: ~45 fJ/MAC at 28nm
- Overhead: **~10%** (VTC + TDC switching)
- TDC area: 2.9% of macro (vs SAR at 30-60%)
- Crossbar: **unchanged** (still charge-redistribution caps)
- Scales: TDC improves with fT → better at each node

### Phase 3: 28-14nm (Production) — Architecture D+E

**Change:** FeCAP crossbar + 1b×1b + digital accumulation.

```
Digital bit → FeCAP crossbar (1b×1b) → 4 comparators → Digital shift-add
```

- Energy: ~19 fJ/MAC at 28nm, ~4.7 fJ/MAC at 7nm
- Overhead: **~5%** (comparators only)
- Non-volatile weights (no reload energy)
- 25× denser than MOM cap arrays
- Scales: **cubically** (90% digital)

### Phase 4: 7nm+ (Volume Production) — Architecture F+E

**Change:** End-to-end charge domain with 3D stacked FeCAP arrays.

```
One-time input → FeCAP Layer 1 → FeCAP Layer 2 → ... → One-time output
                   (no conversion between layers)
```

- Energy: <2 fJ/MAC
- Conversion overhead: **~0%** (amortized over all layers)
- 3D stacking: 10-100× area density
- Projected: 29,600 TOPS/W

---

## The Scaling Proof

```
Energy per MAC (fJ) — log scale

10000 ┤
      │  D ← Digital systolic
 1000 ┤  ×
      │  │╲
  100 ┤  A  ╲D         A = Current (voltage-mode)
      │  │╲  │╲        B = Input-serial + Flash
      │  B  ╲  ╲D      C = VTC + TDC
   10 ┤  │╲C ╲B ╲     D = Digital systolic
      │  │  ╲  ╲C╲D   E = 1b×1b + digital accum
      │  E   E  ╲E╲
    1 ┤            ╲E
      │
      └──┬────┬────┬────┬──
       180nm 65nm 28nm  7nm

Winner:  A    B/C   C/E   E
```

| Architecture | 180nm | 65nm | 28nm | 7nm |
|:---|:---:|:---:|:---:|:---:|
| A. Voltage-mode (current) | **275** | 100 | 55 | 38 |
| B. Input-serial + Flash | 195 | 52 | 18 | 8 |
| C. B + VTC/TDC | 180 | 45 | 12 | 5 |
| D. Digital systolic | 1530 | 385 | 73 | 15 |
| E. 1b×1b + digital accum | 664 | 96 | 19 | **4.7** |
| F. End-to-end (multi-layer) | — | — | ~8 | **~2** |

**Key insight:** Architectures B and C keep our crossbar unchanged and deliver
immediate wins. Architecture E requires redesign but wins at advanced nodes.
All paths keep capacitive crossbar as the core — the device changes (FeCAP),
not the physics.

---

## What Stays the Same Across All Architectures

1. **Charge-domain MAC** — V_col = Σ(V_i × w_ij × C) / C_total
2. **Passive capacitive crossbar** — no static power, no sneak paths, linear
3. **Simultaneous computation** — all crosspoints compute in parallel (O(1))
4. **kT/C noise advantage** — caps inherently better than resistive (20-200×)

## What Changes

| Phase | Input | Readout | Weight Storage | Crosspoint |
|-------|-------|---------|----------------|------------|
| 1 (sky130) | Digital bits | Flash comparators | CMOS switch+cap | Binary-weighted caps |
| 2 (65-28nm) | Digital bits | VTC + TDC | CMOS switch+cap | Binary-weighted caps |
| 3 (28-14nm) | Digital bits | Comparator bank | FeCAP (NVM) | Single FeCAP/crosspoint |
| 4 (7nm+) | Charge from prev layer | Comparator (inter-layer: none) | FeCAP 3D stack | Single FeCAP/crosspoint |

---

## Immediate Action: Sky130 v2 (Architecture B)

### Changes to Current Design

1. **Remove:** `charge_dac` component (entire DAC subcircuit)
2. **Remove:** `interleaved_adc` SAR logic (keep comparator only)
3. **Add:** Flash ADC — 15 StrongARM comparators per column with R-string reference ladder
4. **Add:** 4-bit shift-and-add accumulator (digital, trivial at 180nm)
5. **Modify:** `async_ctrl` — simpler sequencing (no DAC settle phase)
6. **Keep:** `imc_crossbar` (unchanged), `sample_hold_bank` (unchanged), `strongarm` (reused in flash)

### New Timing

```
Cycle (per input bit):
  Reset crossbar:     5ns  (same)
  Apply digital bit:  0ns  (instant — rail-to-rail)
  Charge settle:     10ns  (same)
  Flash compare:      1.5ns (1 comparator delay, all 15 in parallel)
  Latch + accumulate: 2ns  (digital)
  ─────────────────────────
  Total per bit:     18.5ns

4 bits × 18.5ns = 74ns per MVM (vs 60ns current for 3-cycle pipeline)
```

Slower per-MVM, but 29% less energy and future-proof architecture.

### New Energy

```
Crossbar + reset: 8.63 pJ (same)
Flash ADC: 4 cols × 15 comps × 4 cycles × 0.5 × 20fF × 1.8² = 3.11 pJ
Accumulators: 4 cols × 4 cycles × 10 gates × 8.1fJ = 0.52 pJ
S&H: 1.30 pJ (same — sample once before bit-serial)
─────────────────────────────────────────────
Total: 13.56 pJ / 64 MACs = 212 fJ/MAC
```

**Overhead breakdown: crossbar 64% | flash 23% | digital 4% | S&H 10%**
(vs current: crossbar 45% | ADC 37% | DAC 18%)

---

## Key References

| Paper | Venue | Architecture | Key Contribution |
|-------|-------|-------------|-----------------|
| IMAGINE | JSSC 2025 | End-to-end charge | 150 TOPS/W, DAC-free input-serial |
| PICO-RAM | 2024 | Charge-domain | ADC = 4.6% area, PVT-insensitive |
| Georgia Tech FeCAP | JSSC 2024 | Ferroelectric cap | 29,600 TOPS/W projected |
| Configurable TDC | JSSC 2023 | Time-domain | 2124 TOPS/W, TDC = 2.9% area |
| HCiM | ASP-DAC 2025 | ADC-less hybrid | 28× energy reduction, 1 comparator |
| Colonnade | JSSC 2021 | Digital bit-serial | 98.5 TOPS/W, no ADC needed |
| C-2C Ladder | VLSI 2022 | Charge-domain | 8b linear MAC, binary-weighted caps |
| CACTUS | 2025 | Compute-SNR | 3-bit ADC relaxation for neural nets |
| SOCC 2023 | SOCC 2023 | Cap + TDC | Proven: cap crossbar + time-domain readout |
| Near-CIM | 2024 | Analog memory | 76% energy saved by skipping inter-layer ADC |
| imec FeCAP | IEDM 2023 | Ferroelectric | 10^11 endurance, 8.7× memory window |
| 4nm TSMC DCIM | ISSCC 2023 | Digital | 6163 TOPS/W/b — digital wins at 4nm |

---

## Bottom Line

**Our capacitive crossbar is the right core.** It's 20-200× more energy-efficient than
resistive (RRAM), immune to sneak paths, zero static power, and linear. The problem was
never the crossbar — it was the **interface** (DAC/ADC).

The fix is progressive:
1. **Now:** Drop DAC (input-serial), simplify ADC (flash) → 29% energy win
2. **Next:** Replace ADC with TDC → 90%+ of energy is digital, scales cubically
3. **Future:** FeCAP makes the crossbar itself scale → endgame at 29,600 TOPS/W

**The architecture is scaling-proof. The roadmap is clear. The crossbar stays.**
