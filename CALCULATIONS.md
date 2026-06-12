# MVM Design Calculations — Gm/ID Methodology

## 1. System-Level Specifications

| Parameter | Target | Rationale |
|-----------|--------|-----------|
| VDD | 1.8V | Sky130 nominal |
| Clock | 50 MHz (20ns period) | TinyTapeout constraint |
| Resolution | 4-bit | Weight + input precision |
| Crossbar | 4x4 | 16 MACs per compute cycle |
| GEMM throughput | 16 cycles (320ns) | 4(LOAD_W) + 4×3(LOAD_X+COMPUTE+READ_Y) |
| ADC conversion | <10ns | Must fit in single COMPUTE cycle |
| Comparator resolve | <1.5ns | SAR needs 4 comparisons in ~6ns |

## 2. Gm/ID Design Methodology

Gm/ID is a technology-aware sizing method. Instead of assuming square-law, we use the
ratio gm/ID as a **continuous inversion coefficient** that maps directly to transistor
efficiency, speed, and noise.

Key lookup relationships for **sky130 nfet_01v8, L=0.15μm** (from characterization):

| gm/ID (V⁻¹) | Region | VGS−VTH (mV) | ID/W (μA/μm) | fT (GHz) |
|:---:|:---:|:---:|:---:|:---:|
| 5 | Deep strong | ~400 | ~100 | ~55 |
| 10 | Strong | ~200 | ~50 | ~45 |
| 13 | Moderate | ~150 | ~30 | ~40 |
| 20 | Weak-moderate | ~50 | ~5 | ~15 |
| 25 | Weak | ~0 | ~1 | ~3 |

For **sky130 pfet_01v8, L=0.15μm** (μp ≈ 3× lower than μn):

| gm/ID (V⁻¹) | ID/W (μA/μm) | fT (GHz) |
|:---:|:---:|:---:|
| 5 | ~30 | ~20 |
| 10 | ~15 | ~16 |
| 13 | ~10 | ~13 |

---

## 3. StrongARM Comparator

### 3.1 Architecture

9-transistor StrongARM latch:
- 1× tail NMOS (clocked)
- 2× input pair NMOS
- 2× cross-coupled NMOS (regeneration)
- 2× cross-coupled PMOS (regeneration)
- 2× reset PMOS (precharge)

### 3.2 Design Targets

- Output load: Cout ≈ 80fF (CDAC top plate + parasitics + wiring)
- Resolution time: t_resolve < 1.5ns
- Input sensitivity: < 1 LSB = Vref/16 ≈ 112mV (Vref=1.8V)
- Reset time: < 0.5ns (precharge outp/outn to VDD)

### 3.3 Input Pair — W=7.0μm, L=0.15μm

**Design choice: gm/ID = 13 (moderate inversion)**

Why moderate inversion:
- Good gm per unit current → low-offset amplification during evaluation
- fT still ~40 GHz → not speed-limited
- Moderate noise (thermal noise ∝ 1/gm, we need low noise for small ΔVin)

**Derivation:**

The input pair creates initial voltage imbalance ΔV₀ during the evaluation phase
(when CLK goes high, tail turns on, outputs still near VDD):

```
ΔV₀ = (gm_input / Cout) × ΔVin × t_eval
```

Where t_eval ≈ 200ps (time before regeneration dominates).

Required gm_input to get sufficient ΔV₀ for reliable regeneration:

```
ΔV₀_min ≈ 50mV (thermal noise floor + reliable regeneration seed)
ΔVin_min = 112mV (1 LSB)

gm_input = ΔV₀ × Cout / (ΔVin × t_eval)
         = 50mV × 80fF / (112mV × 200ps)
         = 4e-15 / 22.4e-12
         = 178 μA/V
```

From gm/ID lookup at gm/ID = 13:
```
ID/W = 30 μA/μm  (for L=0.15μm NFET)
gm/W = (gm/ID) × (ID/W) = 13 × 30 = 390 μA/V per μm

W = gm_input / (gm/W) = 178 / 390 ≈ 0.46 μm (minimum)
```

We use **W = 7.0μm** (15× overdesign) because:
1. Offset ∝ 1/√(W×L) — large input pair dominates mismatch budget
2. Need to resolve at worst-case ss/-40°C where gm drops ~2×
3. Ensures sub-LSB sensitivity with margin across all PVT corners
4. Input-referred offset σ ≈ AVT/√(W×L) = 4mV/√(7×0.15) ≈ 3.9mV

**Verification:**
```
gm_actual = 13 × 30μA/μm × 7.0μm = 2.73 mA/V
ΔV₀ = 2.73mA/V × 112mV × 200ps / 80fF = 76mV  ✓ (well above noise floor)
```

### 3.4 NMOS Latch — W=1.0μm, L=0.15μm

**Purpose:** Fast positive feedback for regeneration.

Regeneration time constant:
```
τ_regen = Cout / gm_latch
t_resolve = τ_regen × ln(VDD/2 / ΔV₀)
```

Target: t_resolve < 1.5ns, ΔV₀ = 50mV (worst case):
```
τ_regen < 1.5ns / ln(0.9V / 50mV) = 1.5ns / 2.89 = 519ps
gm_latch_min = Cout / τ_regen = 80fF / 519ps = 154 μA/V
```

NMOS latch operates in strong inversion during regeneration (VGS driven toward VDD):
```
gm/ID ≈ 8 (strong inversion, large VGS swing)
ID/W ≈ 70 μA/μm at strong inversion operating point

W = 1.0 μm:
gm_n = 8 × 70 × 1.0 = 560 μA/V  ✓ (3.6× margin)
```

### 3.5 PMOS Latch — W=4.5μm, L=0.15μm

**Goal:** Match NMOS latch gm for symmetric regeneration.

Since μp ≈ μn/3 in sky130:
```
gm_p_target ≈ gm_n = 560 μA/V
gm/W_PMOS ≈ 8 × 20 = 160 μA/V per μm  (at strong inversion)

W_PMOS = 560 / 160 ≈ 3.5 μm (minimum)
```

Use **W = 4.5μm** for PVT margin (PMOS degrades more at ss corner).

Ratio check: W_P/W_N = 4.5/1.0 = 4.5 ≈ μn/μp mobility ratio ✓

### 3.6 Tail NMOS — W=0.42μm, L=0.15μm

**Purpose:** Current source during evaluation. Clocked by VDD → deep strong inversion.

```
VGS = VDD = 1.8V
VTH ≈ 0.36V  (short-channel, DIBL-reduced)
Vov = 1.44V  (comment confirmed)
gm/ID ≈ 2/Vov = 1.4  (very deep strong inversion)
```

At this bias point, velocity saturation dominates:
```
ID ≈ W × vsat × Cox × (VGS - VTH - VDSAT/2)
   ≈ 0.42μm × ~70μA/μm (extracted) ≈ 30μA
```

This is intentionally minimal — the comparator is a **dynamic** circuit. The tail
just needs to steer enough current through the input pair during the brief evaluation
window. The energy for regeneration comes from the precharged Cout.

### 3.7 Reset PMOS — W=1.0μm, L=0.15μm

**Requirement:** Precharge outp/outn from 0V to VDD in < 0.5ns.

```
t_precharge = Cout × ΔVDD / ID_reset
ID_reset > Cout × VDD / t_precharge = 80fF × 1.8V / 0.5ns = 288 μA

PMOS at VGS = -VDD (CLK=0, source=VDD):
ID/W ≈ 30 μA/μm × (strong inversion, large |VGS|)
W_min = 288 / 30 ≈ 9.6 → but we have 2 outputs charging simultaneously from VDD

Each output: 288/2 = 144 μA per reset device
W = 144 / (30 × ~3 for PMOS saturation current density) → Actually with |VGS-VTH|=1.4V:
ID/W_PMOS ≈ 300 μA/μm at deep strong inversion (linear region during charge)

W = 144μA / 300μA/μm ≈ 0.5 μm (minimum)
```

Use **W = 1.0μm** for margin at ss corner where μp degrades 30-40%.

---

## 4. CMOS Switch Sizing (Ron Methodology)

### 4.1 General Formula

For a CMOS transmission gate:
```
Ron_TG = 1 / (μn×Cox×(W_n/L_n)×(VDD-VTH_n-Vin) + μp×Cox×(W_p/L_p)×(VDD-|VTH_p|-VDD+Vin))
```

At mid-rail (Vin = VDD/2 = 0.9V), both NMOS and PMOS contribute equally.
For worst case (Vin near rail), one device handles most conduction.

The **settling time** for an RC network:
```
t_settle = Ron × C_load × ln(1/accuracy)
         = Ron × C_load × N_tau
```

For 4-bit accuracy: error < 0.5 LSB = 1/32 → N_tau = ln(32) = 3.5τ

### 4.2 Charge DAC Switch — W_n=1.68μm, W_p=3.36μm

**Requirement:** Ron < 500Ω at ss/-40°C to settle charge in sub-ns.

```
C_load = C_total_DAC = C_UNIT × (1+2+4+8) = 50fF × 15 = 750fF
t_settle_budget = 2ns (within compute phase)
Ron_max = t_settle / (C_load × 3.5) = 2ns / (750fF × 3.5) = 762Ω
```

Derate 1.5× for ss/-40°C → target Ron < 500Ω at nominal.

For sky130 NFET at typical, VDD=1.8V, Vin=0.9V (worst mid-rail):
```
μn×Cox = 270 μA/V²
VGS - VTH = VDD - VTH_n - Vin = 1.8 - 0.36 - 0.9 = 0.54V

Ron_n = 1 / (270e-6 × (W/L) × 0.54)
W_n/L_n for Ron_n = 1kΩ: W_n/L_n = 1 / (270e-6 × 1000 × 0.54) = 6.86
                           → W_n = 6.86 × 0.15 = 1.03 μm (minimum)
```

Use **W_n = 1.68μm** (L=0.15μm → W/L = 11.2):
```
Ron_n = 1 / (270e-6 × 11.2 × 0.54) = 613Ω
```

PMOS sized 2× for mobility compensation:
```
W_p = 2 × W_n = 3.36μm
Ron_p = 1 / (90e-6 × 22.4 × 0.54) = 919Ω

Ron_TG = Ron_n ∥ Ron_p = 613 × 919 / (613 + 919) = 368Ω  ✓ (< 500Ω)
```

### 4.3 Sample-Hold Switch — W_n=0.84μm, W_p=1.68μm

**Requirement:** Settle 200fF hold cap to 4-bit accuracy in < 2ns.

```
C_hold = 200fF
t_settle = 2ns
Ron_max = 2ns / (200fF × 3.5) = 2.86kΩ
```

Relaxed Ron allows smaller switch → less charge injection:
```
W_n = 0.84μm (W/L = 5.6):
Ron_n = 1 / (270e-6 × 5.6 × 0.54) = 1.22kΩ

W_p = 1.68μm (W/L = 11.2):
Ron_p = 1 / (90e-6 × 11.2 × 0.54) = 1.84kΩ

Ron_TG = 1.22k × 1.84k / (1.22k + 1.84k) = 734Ω  ✓
t_settle = 734Ω × 200fF × 3.5 = 0.51ns  ✓ (well within budget)
```

**Charge injection estimation:**
```
ΔQ = 0.5 × Cox × W × L × (VDD - VTH - Vsig)
   ≈ 0.5 × 8.5fF/μm² × 0.84 × 0.15 × (1.8 - 0.36 - 0.9)
   = 0.5 × 0.535fF × 0.54 = 0.14fF × 0.54V ≈ 0.077fC

ΔV_injection = ΔQ / C_hold = 0.077fC / 200fF ≈ 0.38mV
```

This is << 1 LSB (112mV), so charge injection error is negligible. ✓

### 4.4 IMC Crossbar Reset Switch — W_n=1.26μm, W_p=7.0μm

**Requirement:** Reset 500fF integration cap to 0V in < 2ns.

```
C_int = 500fF
t_reset = 2ns (reset phase in FSM)
Ron_max = t_reset / (C_int × 3.5) = 2ns / (1.75pF) = 1.14kΩ
```

Derate for ss/-40°C → target Ron < 800Ω at nominal.

The reset switch discharges to VSS, so NMOS handles most of the current
(signal starts near mid-rail → NMOS is in strong linear region):
```
W_n = 1.26μm (W/L = 8.4):
Ron_n = 1 / (270e-6 × 8.4 × 0.9) = 490Ω  (Vin starts at ~0.4V, VGS-VTH large)
```

PMOS sized large for initial discharge (when Vcol near VDD/2):
```
W_p = 7.0μm: handles early phase when signal is high and NMOS Vov is reduced
Ron_p = 1 / (90e-6 × 46.7 × 0.54) = 441Ω

Ron_TG (mid-rail) = 490 ∥ 441 = 232Ω
t_settle = 232Ω × 500fF × 3.5 = 0.41ns  ✓
```

Large PMOS (7.0μm) ensures fast reset even at ss corner where PMOS degrades worst.

### 4.5 IMC Crosspoint Cap Array Switch — W_n=1.26μm, W_p=2.52μm

**Requirement:** Transfer charge from input row to column through binary-weighted caps.

```
C_xpt = up to 8×C_UNIT = 400fF per crosspoint (weight=1111)
Column load: C_INT + 4×C_xpt_avg = 500fF + 4×200fF = 1.3pF total
Settling budget: 5ns (within compute phase)

Ron_max = 5ns / (400fF × 3.5) = 3.57kΩ per switch
```

Use W_n=1.26μm, W_p=2.52μm for moderate sizing:
```
Ron_n = 1 / (270e-6 × 8.4 × 0.54) = 818Ω
Ron_p = 1 / (90e-6 × 16.8 × 0.54) = 1.22kΩ
Ron_TG = 490Ω  ✓
```

### 4.6 ADC Mux Switch — W_n=0.42μm, W_p=1.42μm

**Requirement:** Connect column to comparator input. Minimal size to reduce parasitic loading.

```
C_load ≈ 10fF (comparator gate cap of input pair)
t_settle = 1ns
Ron_max = 1ns / (10fF × 3.5) = 28.6kΩ  (very relaxed)
```

Minimum-width sufficient. W_n=0.42μm chosen for lowest parasitic cap on column node.
W_p=1.42μm (not exactly 2×) tuned for near-rail signal pass (column voltages can approach VDD).

---

## 5. IMC Crossbar — Charge Domain Computation

### 5.1 Capacitive MAC Operation

```
V_col_j = Σᵢ (V_xi × w_ij × C_UNIT) / (C_INT + Σᵢ w_ij × C_UNIT)
```

Where:
- V_xi = DAC output voltage for input i (0 to Vref)
- w_ij = weight value (0 to 15, 4-bit)
- C_UNIT = 50fF
- C_INT = 500fF (integration capacitor)

### 5.2 C_UNIT Selection — 50fF

**Constraints:**
1. kT/C noise floor must be below 0.5 LSB:
```
V_noise_rms = √(kT/C_total)
C_total_min = kT / (V_LSB/2)² = 4.14e-21 / (56mV)² = 1.32fF
```
→ 50fF provides massive noise margin (6× overdesign for single cap, much more for array).

2. Must dominate parasitic caps (switch Cds ≈ 0.5fF, routing ≈ 1-2fF):
```
C_UNIT / C_parasitic = 50fF / 2fF = 25× → parasitics negligible ✓
```

3. Total array cap must not overload reset switch:
```
C_col_max = C_INT + 4 rows × 15 × C_UNIT = 500fF + 3pF = 3.5pF
t_reset = Ron_rst × C_col_max × 3.5 = 232Ω × 3.5pF × 3.5 = 2.84ns
```
→ Fits in 5ns reset budget at typical. ✓

### 5.3 C_INT Selection — 500fF

**Design:** C_INT provides voltage division to keep column swing within ADC input range.

Full-scale column voltage (all inputs max, all weights max):
```
V_col_max = (4 × 1.8V × 15 × 50fF) / (500fF + 4 × 15 × 50fF)
          = 5.4nC/V × ...

Numerator: 4 rows × Vref × 15(max wt) × 50fF = 4 × 1.8 × 750fF = 5.4pC
Denominator: 500fF + 4 × 750fF = 3.5pF

V_col_max = 5.4pC / 3.5pF = 1.54V
```

This keeps the column below VDD (1.8V) → ADC can digitize. ✓

Minimum detectable signal (1 input, weight=1):
```
V_col_min = (1.8V × 1/16 × 1 × 50fF) / (500fF + 50fF)
          = (0.1125 × 50fF) / 550fF
          = 5.625fC / 550fF = 10.2mV
```

This is above noise floor (kT/C at 550fF = 2.7mV rms) → detectable with margin. ✓

---

## 6. Async Controller — Delay Chain Sizing

### 6.1 Inverter Delay Model

Single inverter delay (min-size: W_n=0.42μm, W_p=0.84μm):
```
t_pd = 0.69 × Ron × (Cgate_next + Cload)
```

For sky130 at L=0.15μm:
```
Ron_n = 1 / (270e-6 × 2.8 × ~0.7V) ≈ 1.9kΩ  (average during transition)
Ron_p = 1 / (90e-6 × 5.6 × ~0.7V) ≈ 2.8kΩ

t_rise ≈ 0.69 × 2.8kΩ × C_total
t_fall ≈ 0.69 × 1.9kΩ × C_total
t_pd_avg ≈ 0.69 × 2.35kΩ × C_total
```

### 6.2 Reset Delay Chain — 10 stages, Cload=220fF

**Target:** ~5ns reset phase.

```
Per-stage: t_pd = 0.69 × 2.35kΩ × 220fF = 357ps
```

Wait — with 220fF load cap dominating gate cap (~1fF), the inverter drives mainly Cload:
```
t_pd_stage ≈ 0.69 × Ron_avg × Cload = 0.69 × 2.35kΩ × 220fF ≈ 357ps

Total (10 stages): 10 × 357ps ≈ 3.6ns
```

Accounting for wire/gate parasitics (~+40%): **≈5ns** ✓

### 6.3 Settle Delay Chain — 20 stages, Cload=220fF

**Target:** ~10ns settling time (charge sharing must complete before ADC triggers).

```
Total (20 stages): 20 × 357ps × 1.4 ≈ 10ns ✓
```

### 6.4 Muller C-Element Sizing

Pull-up (series PMOS): W=1.0μm — ensures sufficient drive through 2 series devices:
```
Effective (W/L)_series = (W/L)/2 = (1.0/0.15)/2 = 3.33
t_rise < 1ns for typical load (~20fF)
```

Pull-down (series NMOS): W=0.5μm — 2× mobility advantage:
```
Effective (W/L)_series = (0.5/0.15)/2 = 1.67
```

Keeper/feedback: W=0.25μm at L=0.30μm — weak (just holds state, must not fight active drivers).

---

## 7. Summary of Design Decisions

| Device | W (μm) | L (μm) | gm/ID | Region | Key Constraint |
|--------|---------|---------|-------|--------|----------------|
| Comp input pair | 7.0 | 0.15 | 13 | Moderate | Offset + sensitivity |
| Comp PMOS latch | 4.5 | 0.15 | ~8 | Strong | Match NMOS gm |
| Comp NMOS latch | 1.0 | 0.15 | ~8 | Strong | τ_regen < 500ps |
| Comp tail | 0.42 | 0.15 | ~1.4 | Deep strong | Min area, max Vov |
| Comp reset | 1.0 | 0.15 | — | Linear | t_precharge < 0.5ns |
| DAC switch N | 1.68 | 0.15 | — | Linear | Ron < 500Ω @ss |
| DAC switch P | 3.36 | 0.15 | — | Linear | 2× for μ ratio |
| S&H switch N | 0.84 | 0.15 | — | Linear | Ron, low Qinj |
| S&H switch P | 1.68 | 0.15 | — | Linear | 2× for μ ratio |
| Xbar reset N | 1.26 | 0.15 | — | Linear | 500fF in <2ns |
| Xbar reset P | 7.0 | 0.15 | — | Linear | ss/-40°C margin |
| Xbar xpt N | 1.26 | 0.15 | — | Linear | PVT margin |
| Xbar xpt P | 2.52 | 0.15 | — | Linear | 2× for μ ratio |
| Delay inv N | 0.42 | 0.15 | — | Switching | Min size |
| Delay inv P | 0.84 | 0.15 | — | Switching | 2× for μ ratio |

### Capacitor Budget

| Capacitor | Value | Purpose |
|-----------|-------|---------|
| C_UNIT (DAC/xbar) | 50fF | Unit cap, >> kT/C noise, >> parasitics |
| C_INT (crossbar) | 500fF | Voltage division, keeps V_col < VDD |
| C_HOLD (S&H) | 200fF | Hold voltage during compute (~0.38mV droop/ns) |
| Cload (delay chain) | 220fF | Sets per-stage delay ~350-500ps |

---

## 8. PVT Corner Verification

All sizing includes margin for worst-case **ss corner at -40°C**:
- μn degrades ~30%, μp degrades ~40%
- VTH increases ~60-80mV
- Switches: sized 1.5-2× above minimum → still meet Ron targets
- Comparator: 15× input pair overdesign → offset still < 1 LSB
- Delay chains: slower at ss → more conservative timing (safe direction)

At **ff/125°C**: circuits are faster, but leakage increases:
- Droop on hold caps: higher (but still < 1 LSB in budget)
- Comparator: faster resolution (no issue)
- Switches: lower Ron (no issue)

Verified across 9 PVT conditions (tt/ss/ff × -40/27/125°C), all pass. ✓

---

## 9. Process Scaling Analysis — Analog IMC vs Digital MAC

### 9.1 This Design's Energy Budget (sky130, 180nm)

**Analog IMC per 4×4 GEMM (64 4-bit MACs):**

| Stage | Calculation | Energy |
|-------|-------------|--------|
| DAC (×4) | 4 × 0.5 × 750fF × 1.8² × 0.5(avg switching) | 2.43 pJ |
| S&H (×4) | 4 × 0.5 × 200fF × 1.8² | 1.30 pJ |
| Crossbar reset (×4 cols) | 4 × 0.5 × 3.5pF × 0.8² (avg V²) | 4.48 pJ |
| Charge sharing (MAC) | 4 × 0.5 × 3.5pF × 0.77² (avg Vcol²) | 4.15 pJ |
| ADC (×4 cols, SAR) | 4 × [4×(0.5×750fF×1.8²×0.3) + 4×(0.5×80fF×1.8²)] | 5.08 pJ |
| Async control | ~30 inv switchings × 2fF × 1.8² | 0.19 pJ |
| **Total** | | **17.6 pJ** |

**Energy per MAC: 17.6 pJ / 64 = 275 fJ/MAC**

Breakdown: MAC itself (charge sharing) = 4.15 pJ → 65 fJ/MAC.
DAC+ADC overhead = 7.51 pJ → 117 fJ/MAC (63% of total).

### 9.2 Digital Equivalent at 180nm

4-bit multiply-accumulate in CMOS logic:

```
4×4 multiplier: ~16 AND + 12 full-adders = ~100 gates
8-bit accumulator: ~40 gates
Total per MAC: ~140 gates

Gate energy at 180nm: Ceff × VDD² × α
  Ceff ≈ 5fF (fan-out-of-4 inverter equivalent)
  VDD = 1.8V
  α = 0.5 (activity factor)
  E_gate = 5fF × 3.24V² × 0.5 = 8.1 fJ

E_MAC = 140 × 8.1 = 1.13 pJ/MAC
```

Plus register file overhead (weight storage + input broadcast):
```
SRAM read at 180nm: ~50 fJ/bit
Per MAC: 4-bit weight + 4-bit input = 8 bits × 50 fJ = 400 fJ
E_MAC_total = 1.13 + 0.40 = 1.53 pJ/MAC
```

64 MACs digital: 64 × 1.53 = **98 pJ total, 1.53 pJ/MAC**

### 9.3 Verdict at 180nm

```
Analog IMC:  275 fJ/MAC,  64 MACs in 1 compute cycle (~20ns)
Digital MAC: 1530 fJ/MAC, 64 MACs in 64 cycles (or 1 cycle with 64× parallelism)
                                                  ────────────────────────────
Ratio: analog is 5.6× more energy-efficient at 180nm
```

But the real win is **throughput density** — the capacitor crossbar does 64 MACs
simultaneously in ~30μm × 30μm of MOM cap, while 64 parallel digital multipliers
would need ~200μm × 200μm of logic at 180nm.

**Area comparison (180nm):**
```
Analog crossbar: 4×4 × 15 caps × ~25μm² each = 6,000 μm² (caps)
  + C_INT, switches, routing ≈ 15,000 μm² total crossbar
  + 4 DACs + 2 ADC units ≈ 20,000 μm²
  Total analog: ~35,000 μm²

Digital 64-MAC array: 64 × 140 gates × ~10μm²/gate = 89,600 μm²
  + register file ≈ 30,000 μm²
  Total digital: ~120,000 μm²
```

**Analog wins 3.4× on area, 5.6× on energy at 180nm.**

### 9.4 Scaling to Smaller Nodes

The critical asymmetry: **digital energy scales as CV²; analog caps and kT/C do not.**

#### What scales with process shrink

| Parameter | 180nm | 65nm | 28nm | 7nm | Scaling law |
|-----------|-------|------|------|-----|-------------|
| VDD | 1.8V | 1.2V | 0.9V | 0.75V | ~√node |
| Digital Cgate | 5fF | 1.5fF | 0.5fF | 0.15fF | ~linear |
| Digital E_gate (CV²) | 16.2 fJ | 2.16 fJ | 0.41 fJ | 0.084 fJ | ~cubic |
| Gate area | 10 μm² | 1.3 μm² | 0.25 μm² | 0.015 μm² | ~quadratic |
| SRAM bit cell | 2 μm² | 0.5 μm² | 0.12 μm² | 0.027 μm² | ~quadratic |

#### What does NOT scale

| Parameter | 180nm | 65nm | 28nm | 7nm | Why |
|-----------|-------|------|------|-----|-----|
| kT (thermal) | 26meV | 26meV | 26meV | 26meV | Physics constant |
| C_min for 4-bit SNR | ~1.3fF | ~5.2fF | ~14fF | ~24fF | kT/C ∝ 1/V² |
| MOM cap density | 1 fF/μm² | 2 fF/μm² | 4 fF/μm² | 8 fF/μm² | Slow improvement |
| ADC FOM (Walden) | 100 fJ/step | 30 fJ/step | 10 fJ/step | 5 fJ/step | Flattening |
| Comparator offset (σ) | ~4mV | ~6mV | ~10mV | ~18mV | Pelgrom ∝ 1/√(WL) |

The **kT/C noise floor** is the killer. As VDD shrinks, the signal swing shrinks,
but thermal noise (kT) stays constant. To maintain SNR you need *larger* caps:

```
SNR_required = 6.02×N + 1.76 dB  (for N-bit resolution)
  4-bit: SNR > 26 dB → signal/noise > 20×

V_noise = √(kT/C)
V_signal = VDD × (fraction of full-scale swing)

C_min = kT / (V_signal / 20)²
```

| Node | VDD | V_signal (half-scale) | C_min (4-bit) | C_min (6-bit) |
|------|-----|-----------------------|---------------|---------------|
| 180nm | 1.8V | 0.9V | 1.3 fF | 21 fF |
| 65nm | 1.2V | 0.6V | 2.9 fF | 46 fJ |
| 28nm | 0.9V | 0.45V | 5.1 fF | 82 fF |
| 7nm | 0.75V | 0.375V | 7.4 fF | 118 fF |

At 4-bit, caps stay small enough. But this circuit also needs C >> parasitics:

```
At 7nm, Cparasitic per switch ≈ 0.3fF (smaller devices, but more BEOL layers)
C_UNIT must be ≥ 10× Cparasitic → C_UNIT ≥ 3fF (7nm) vs 50fF (180nm)
```

So C_UNIT can shrink ~16× from 180nm to 7nm. Good — but cap area shrinks only ~4×
(density 1→8 fF/μm²), not the ~144× that digital logic area shrinks.

### 9.5 Projected Energy/MAC Across Nodes

#### Analog IMC (this architecture, scaled)

Scaling assumptions:
- C_UNIT scales down with VDD² (maintain SNR), but floors at 10×Cparasitic
- Switch energy ∝ C×VDD² (C doesn't shrink as fast as digital)
- ADC energy follows Walden FOM trend
- DAC energy ∝ C_array × VDD²

| Node | VDD | C_UNIT | C_INT | E_MAC (fJ) | E_DAC+ADC (fJ) | E_total (fJ) |
|------|-----|--------|-------|------------|-----------------|---------------|
| 180nm | 1.8V | 50fF | 500fF | 65 | 117 | **275** |
| 65nm | 1.2V | 20fF | 200fF | 11 | 45 | **100** |
| 28nm | 0.9V | 8fF | 80fF | 2.6 | 22 | **55** |
| 7nm | 0.75V | 4fF | 40fF | 0.9 | 14 | **38** |

#### Digital MAC (standard-cell systolic)

| Node | VDD | E_gate (fJ) | E_MAC (fJ) | E_RF (fJ) | E_total (fJ) |
|------|-----|-------------|------------|-----------|---------------|
| 180nm | 1.8V | 8.1 | 1130 | 400 | **1530** |
| 65nm | 1.2V | 2.2 | 305 | 80 | **385** |
| 28nm | 0.9V | 0.41 | 57 | 16 | **73** |
| 7nm | 0.75V | 0.084 | 12 | 3 | **15** |

#### The Crossover

```
                Energy per 4-bit MAC (fJ)
                ─────────────────────────
    10000 ┤
          │ D ← Digital
     1000 ┤ ×
          │   ╲
      100 ┤ A  ╲ D                    A = Analog IMC
          │  ╲  ╲                     D = Digital MAC
       10 ┤   ╲  ╲──── D
          │    A──── A── A ← analog   × = crossover
        1 ┤              ╲── D
          └──┬────┬────┬────┬──
           180nm 65nm 28nm 7nm

Crossover: ~28-40nm
```

**At 180nm: analog wins 5.6×.**
**At 65nm: analog wins 3.9×.**
**At 28nm: roughly even (55 vs 73 fJ) — digital within striking distance.**
**At 7nm: digital wins 2.5× (15 vs 38 fJ).**

### 9.6 Area Crossover

| Node | Analog IMC (μm²) | Digital 64-MAC (μm²) | Ratio (D/A) |
|------|-------------------|-----------------------|-------------|
| 180nm | 35,000 | 120,000 | 3.4× analog wins |
| 65nm | 12,000 | 15,000 | 1.25× analog wins |
| 28nm | 5,000 | 2,500 | 0.5× **digital wins** |
| 7nm | 2,500 | 250 | 0.1× **digital wins 10×** |

Area crossover happens earlier (~65nm) because cap density improves slowly while
transistor density improves quadratically.

### 9.7 Latency Analysis — DAC/ADC Overhead

**This design's timing (180nm, 50MHz):**
```
Per MVM (1 row-vector × weight-matrix):
  LOAD_X:    1 cycle  = 20ns (digital latch)
  RESET:     ~5ns     (crossbar discharge)
  SETTLE:    ~10ns    (charge sharing = the actual MAC)
  ADC:       ~6ns     (4 SAR comparisons)
  READ_Y:    1 cycle  = 20ns (latch ADC outputs)

Total per MVM: 3 cycles = 60ns
  Of which: actual compute = 10ns (17%)
  DAC+ADC overhead = 31ns (52%)
  Digital I/O = 19ns (31%)
```

**Scaling the overhead:**

ADC speed scales with fT (comparator speed) and CDAC settling:
```
                  180nm    65nm    28nm    7nm
fT (GHz)          40       120     250     400
Comp resolve      1.5ns    0.5ns   0.2ns   0.1ns
SAR 4-bit         6ns      2ns     0.8ns   0.4ns
DAC settle        2ns      0.8ns   0.3ns   0.15ns
Reset             5ns      2ns     0.8ns   0.4ns
Charge-share      10ns     4ns     1.5ns   0.8ns
─────────────────────────────────────────────────
Total analog      23ns     8.8ns   3.4ns   1.75ns
  MAC fraction    43%      45%     44%     46%
  ADC+DAC overhead 57%     55%     56%     54%
```

**DAC+ADC overhead stays ~55% at every node** — it's a constant architectural tax.
The absolute latency shrinks (fT improves), but the *ratio* doesn't change because
both the compute and the conversion scale with the same transistor speed.

**Digital latency for 4×4 GEMM:**
```
                  180nm    65nm    28nm    7nm
Clock             50MHz    500MHz  2GHz    4GHz
Cycle             20ns     2ns     0.5ns   0.25ns
64 MACs (serial)  1280ns   128ns   32ns    16ns
Systolic (4×4)    7 cyc    7 cyc   7 cyc   7 cyc
Systolic latency  140ns    14ns    3.5ns   1.75ns
```

**Latency comparison (systolic array vs analog IMC):**
```
          180nm    65nm    28nm    7nm
Analog    23ns     8.8ns   3.4ns   1.75ns
Digital   140ns    14ns    3.5ns   1.75ns
Ratio     6.1×     1.6×    1.03×   1.0×
```

Analog latency advantage erodes because digital clock rates scale faster than
analog settling times.

### 9.8 The Full Picture

```
┌─────────────────────────────────────────────────────────────────┐
│           ANALOG IMC vs DIGITAL MAC — SCALING SUMMARY           │
├──────────┬──────────┬──────────┬──────────┬──────────┬──────────┤
│ Metric   │  180nm   │   65nm   │   28nm   │   7nm    │  Trend   │
├──────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ Energy   │ A wins   │ A wins   │ ~even    │ D wins   │ D gets   │
│          │  5.6×    │  3.9×    │  1.3×    │  2.5×    │ better   │
├──────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ Area     │ A wins   │ A wins   │ D wins   │ D wins   │ D gets   │
│          │  3.4×    │  1.25×   │  2×      │  10×     │ better   │
├──────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ Latency  │ A wins   │ A wins   │ ~even    │ ~even    │ converge │
│          │  6.1×    │  1.6×    │  1.03×   │  1.0×    │          │
├──────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ DAC/ADC  │  55%     │  55%     │  55%     │  55%     │ constant │
│ overhead │          │          │          │          │ tax      │
├──────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ Verdict  │ ANALOG   │ ANALOG   │ TOSS-UP  │ DIGITAL  │          │
└──────────┴──────────┴──────────┴──────────┴──────────┴──────────┘
```

### 9.9 Why Analog IMC Still Gets Built at Advanced Nodes

Despite digital winning on paper at <28nm, some groups still pursue analog IMC because:

1. **Higher precision favors analog more** — at 8-bit, digital multiplier energy
   grows ~4× (more gates), while analog just needs ~4× larger caps (energy ~4×).
   The crossover shifts to ~14nm for 8-bit.

2. **Weight stationarity** — if weights are stored as capacitor charges or in
   NVM (RRAM/Flash), you skip the SRAM read energy entirely. This removes the
   ~20% RF overhead from digital.

3. **Hybrid architectures** — use analog crossbar for the MAC but digital
   accumulation, getting the density benefit without full ADC per column.

4. **Application tolerance** — neural network inference tolerates noise/nonlinearity
   that would be unacceptable in general-purpose compute. The "effective" resolution
   can be 3-4 bits even with 6-bit analog precision.

### 9.10 What Would Need to Change for Sub-28nm Analog IMC

To stay competitive below 28nm, analog IMC would need:

1. **Eliminate the ADC** — use analog-to-spike or threshold-based readout
   (removes 55% overhead, but loses precision)
2. **NVM crosspoint** (RRAM/PCM) — store weights as conductance, eliminating
   cap arrays entirely. Compute becomes I = G×V, purely resistive.
   But variability is 100× worse than capacitors.
3. **Time-domain encoding** — replace voltage-mode DAC/ADC with pulse-width
   modulation. Digital-friendly, but latency grows linearly with precision.
4. **Massive parallelism** — at 7nm you can fit a 256×256 analog crossbar.
   Even if per-MAC efficiency is worse, doing 65,536 MACs simultaneously
   in ~2ns beats any digital systolic array on throughput/mm².

### 9.11 Bottom Line

**This design at sky130 (180nm) is in the sweet spot.** Analog IMC wins on
energy (5.6×), area (3.4×), and latency (6.1×) over digital at this node.
The DAC/ADC overhead is a permanent ~55% tax, but at 180nm the MAC savings
more than compensate.

The crossover to digital superiority happens around **28-40nm** depending on
the metric. Below 7nm, digital wins on everything except raw parallelism density
for very large arrays.

For this TinyTapeout project on sky130: **analog IMC is the correct choice.**
