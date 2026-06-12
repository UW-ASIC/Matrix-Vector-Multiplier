"""Gm/Id Sizing for MVM Tapeout — Sky130 nfet_01v8 / pfet_01v8.

Computes W/L for each block using Gm/Id methodology.
Targets: TT corner, 27°C, VDD=1.8V.

Usage: PYTHONPATH=project python project/sizing/gm_id_sizing.py
"""

import math

# ============================================================
# Sky130 Device Parameters (level-1 approximation)
# ============================================================
# nfet_01v8
MU_N_COX = 270e-6   # μn·Cox [A/V²]  (kp in level-1)
VT_N = 0.36          # Vt0 [V] (typical TT)
LAMBDA_N = 0.05      # channel-length modulation [1/V]

# pfet_01v8
MU_P_COX = 55e-6    # μp·Cox [A/V²] (actual sky130, NOT the 90e-6 from level-1 testbench)
VT_P = 0.42          # |Vt0| [V] (typical TT)
LAMBDA_P = 0.05

VDD = 1.8
VREF = VDD / 2       # 0.9V
L_MIN = 0.15e-6      # minimum L [m]

# ============================================================
# Helper Functions
# ============================================================

def gm_over_id(vov):
    """Gm/Id in strong inversion (square-law). Valid for Vov > ~100mV."""
    return 2.0 / vov


def id_sat(mu_cox, w, l, vov):
    """Saturation current Id = (μCox/2)·(W/L)·Vov²."""
    return (mu_cox / 2) * (w / l) * vov**2


def gm_sat(mu_cox, w, l, vov):
    """Transconductance gm = μCox·(W/L)·Vov."""
    return mu_cox * (w / l) * vov


def w_for_id(mu_cox, l, vov, id_target):
    """Solve W for given Id target: W = 2·Id·L / (μCox·Vov²)."""
    return 2 * id_target * l / (mu_cox * vov**2)


def w_for_gm(mu_cox, l, vov, gm_target):
    """Solve W for given gm target: W = gm·L / (μCox·Vov)."""
    return gm_target * l / (mu_cox * vov)


def ron_tgate(mu_cox, w, l, vt, vdd=VDD):
    """Ron of transmission gate (NMOS only, gate=VDD, worst-case at Vin=VDD/2).
    Ron = 1 / (μCox · W/L · (Vgs - Vt))
    At midpoint: Vgs = VDD - VDD/2 = VDD/2, so Vov = VDD/2 - Vt.
    """
    vov = vdd / 2 - vt
    if vov <= 0:
        return float('inf')
    return 1.0 / (mu_cox * (w / l) * vov)


def tau_rc(ron, cload):
    """RC time constant."""
    return ron * cload


def inv_delay(cload, mu_n_cox, wn, ln, mu_p_cox, wp, lp, vdd=VDD):
    """Propagation delay of CMOS inverter driving Cload.
    tp ≈ 0.69 · Cload · (Rn + Rp) / 2
    Rn = 1/(μn·Cox · Wn/Ln · Vov_n),  Rp = 1/(μp·Cox · Wp/Lp · Vov_p)
    Average current approximation: I_avg ≈ (μCox/2)·(W/L)·(VDD-Vt)² × (some factor)
    Simpler: tp ≈ 0.69·Cload / I_avg, where I_avg ≈ (kp/2)·(W/L)·(VDD/2-Vt)²
    """
    # Effective drive current at VDD/2
    vov_n = vdd - VT_N  # gate at VDD for pull-down
    vov_p = vdd - VT_P  # |Vgs| = VDD for pull-up
    # Average between saturation at VDD and linear at 0
    i_n = (mu_n_cox / 2) * (wn / ln) * (vov_n ** 2) * 0.5  # average factor
    i_p = (mu_p_cox / 2) * (wp / lp) * (vov_p ** 2) * 0.5
    tp_hl = 0.69 * cload * vdd / (2 * i_n)
    tp_lh = 0.69 * cload * vdd / (2 * i_p)
    return (tp_hl + tp_lh) / 2


# ============================================================
# Block 1: StrongARM Comparator
# ============================================================
def size_strongarm():
    print("=" * 70)
    print("  BLOCK 1: StrongARM Latch Comparator")
    print("=" * 70)

    # Specs
    t_resolve = 1.5e-9   # target resolution time [s]
    v_in_min = 5e-3       # minimum detectable ΔVin [V] (½ LSB of 4-bit ADC)
    c_out = 80e-15        # output node cap [F] (layout parasitics + latch drain caps)

    print(f"\n  Specs:")
    print(f"    Resolution time target:  {t_resolve*1e9:.1f} ns")
    print(f"    Min input sensitivity:   {v_in_min*1e3:.1f} mV")
    print(f"    Output node cap (est):   {c_out*1e15:.0f} fF")

    # --- Tail current ---
    # StrongARM works in two phases:
    # Phase 1 (integration): input pair steers current, builds ΔV on drains
    # Phase 2 (regeneration): latch amplifies exponentially
    #
    # Integration phase duration: t_int ≈ C_out × VDD / Itail
    # Initial imbalance: ΔV_init = (gm_in / (2·C_out)) × ΔVin × t_int
    # We want ΔV_init ≈ 50-100mV for fast regeneration

    delta_v_init = 80e-3  # initial imbalance after integration [V]
    # ΔV_init = (gm_in × ΔVin) / (2 · C_out) × t_int
    # t_int = C_out × VDD / Itail
    # → ΔV_init = gm_in × ΔVin × VDD / (2 × Itail)
    # → Itail = gm_in × ΔVin × VDD / (2 × ΔV_init)
    # Also: gm_in = 2·Id_per_branch / Vov_in = Itail / Vov_in (each branch gets Itail/2)
    # → ΔV_init = (Itail/Vov_in) × ΔVin × VDD / (2 × Itail) = ΔVin × VDD / (2×Vov_in)
    # → Vov_in = ΔVin × VDD / (2 × ΔV_init)

    vov_in = v_in_min * VDD / (2 * delta_v_init)
    print(f"\n  --- Input Pair ---")
    print(f"    Required Vov (input):    {vov_in*1e3:.1f} mV")

    # This gives very low Vov! In practice we want Vov_in ≈ 100-200mV for speed.
    # The sensitivity comes from the latch gain, not just the input pair.
    # Let's choose a practical Vov_in:
    vov_in = 0.15  # 150mV — moderate inversion, good gm/Id ≈ 13

    gm_id_in = gm_over_id(vov_in)
    print(f"    Chosen Vov (input):      {vov_in*1e3:.0f} mV  (gm/Id = {gm_id_in:.1f})")

    # Tail current: size for speed
    # Regeneration time: t_reg = (C_out / gm_latch) × ln(VDD / ΔV_init)
    # Total: t_resolve = t_int + t_reg
    # Budget: t_int ≈ 0.5ns, t_reg ≈ 1.0ns

    t_int = 0.5e-9
    # t_int = C_out × VDD / Itail → Itail = C_out × VDD / t_int
    i_tail = c_out * VDD / t_int
    print(f"\n  --- Tail Current ---")
    print(f"    Integration time:        {t_int*1e9:.1f} ns")
    print(f"    Required Itail:          {i_tail*1e6:.1f} μA")

    # Tail NMOS: Vgs = VDD (clock high), so Vov = VDD - Vt = 1.44V (deep strong inversion)
    vov_tail = VDD - VT_N
    w_tail = w_for_id(MU_N_COX, L_MIN, vov_tail, i_tail)
    print(f"    Tail Vov:                {vov_tail:.2f} V (saturated switch)")
    print(f"    W_tail:                  {w_tail*1e6:.2f} μm  (L={L_MIN*1e6:.2f}μm)")
    print(f"    → gm/Id = {gm_over_id(vov_tail):.2f} (very strong inversion — OK, it's a switch)")

    # Input pair sizing
    # Each branch: Id = Itail/2
    id_in = i_tail / 2
    w_in = w_for_id(MU_N_COX, L_MIN, vov_in, id_in)
    gm_in = gm_sat(MU_N_COX, w_in, L_MIN, vov_in)
    print(f"\n  --- Input Pair (NMOS) ---")
    print(f"    Id per branch:           {id_in*1e6:.1f} μA")
    print(f"    Vov:                     {vov_in*1e3:.0f} mV")
    print(f"    W_in:                    {w_in*1e6:.2f} μm  (L={L_MIN*1e6:.2f}μm)")
    print(f"    gm_in:                   {gm_in*1e3:.2f} mS")
    print(f"    gm/Id:                   {gm_id_in:.1f}")

    # Latch (regeneration)
    # t_reg = (C_out / gm_latch) × ln(VDD / ΔV_init)
    t_reg = t_resolve - t_int
    # ΔV_init from input pair: ΔVin × gm_in × t_int / (2 × C_out)
    delta_v = v_in_min * gm_in * t_int / (2 * c_out)
    gain_needed = VDD / delta_v
    ln_gain = math.log(gain_needed)
    gm_latch = c_out * ln_gain / t_reg
    print(f"\n  --- Latch (Cross-Coupled) ---")
    print(f"    Regeneration time:       {t_reg*1e9:.1f} ns")
    print(f"    ΔV_init:                 {delta_v*1e3:.1f} mV")
    print(f"    Gain needed:             {gain_needed:.0f}× ({ln_gain:.1f} nats)")
    print(f"    Required gm_latch:       {gm_latch*1e6:.0f} μS")

    # NMOS latch: biased at ~ VDD/2 during regeneration
    vov_latch_n = 0.20  # moderate inversion
    w_latch_n = w_for_gm(MU_N_COX, L_MIN, vov_latch_n, gm_latch)
    id_latch_n = id_sat(MU_N_COX, w_latch_n, L_MIN, vov_latch_n)
    print(f"\n    NMOS latch:")
    print(f"      Vov:                   {vov_latch_n*1e3:.0f} mV")
    print(f"      W_latch_n:             {w_latch_n*1e6:.2f} μm")
    print(f"      Id (at operating pt):  {id_latch_n*1e6:.1f} μA")
    print(f"      gm/Id:                 {gm_over_id(vov_latch_n):.1f}")

    # PMOS latch: needs ~same gm but μp is lower → wider
    w_latch_p = w_for_gm(MU_P_COX, L_MIN, vov_latch_n, gm_latch)
    id_latch_p = id_sat(MU_P_COX, w_latch_p, L_MIN, vov_latch_n)
    print(f"    PMOS latch:")
    print(f"      Vov:                   {vov_latch_n*1e3:.0f} mV")
    print(f"      W_latch_p:             {w_latch_p*1e6:.2f} μm")
    print(f"      Id (at operating pt):  {id_latch_p*1e6:.1f} μA")

    # Reset PMOS: needs to pull output to VDD quickly between comparisons
    # Target: reset in < 0.5ns, discharging C_out from 0 to VDD
    t_reset = 0.5e-9
    i_reset = c_out * VDD / t_reset
    vov_reset = VDD - VT_P  # gate=0 → |Vgs|=VDD → |Vov|=VDD-|Vt|
    w_reset = w_for_id(MU_P_COX, L_MIN, vov_reset, i_reset)
    print(f"\n  --- Reset PMOS ---")
    print(f"    Reset time target:       {t_reset*1e9:.1f} ns")
    print(f"    Required I_reset:        {i_reset*1e6:.1f} μA")
    print(f"    W_reset:                 {w_reset*1e6:.2f} μm")

    # Summary
    print(f"\n  {'─'*50}")
    print(f"  STRONGARM SIZING SUMMARY (sky130, L=0.15μm):")
    print(f"  {'─'*50}")
    print(f"    Tail (NMOS):     W = {w_tail*1e6:.2f} μm")
    print(f"    Input (NMOS):    W = {w_in*1e6:.2f} μm")
    print(f"    Latch N (NMOS):  W = {w_latch_n*1e6:.2f} μm")
    print(f"    Latch P (PMOS):  W = {w_latch_p*1e6:.2f} μm")
    print(f"    Reset (PMOS):    W = {w_reset*1e6:.2f} μm")
    print(f"    Total Itail:     {i_tail*1e6:.1f} μA")
    print(f"    Power (dynamic): {i_tail * VDD * 1e6:.1f} μW (per comparison)")

    return {
        "w_tail": w_tail, "w_in": w_in,
        "w_latch_n": w_latch_n, "w_latch_p": w_latch_p,
        "w_reset": w_reset, "i_tail": i_tail
    }


# ============================================================
# Block 2: Crossbar CMOS Switches
# ============================================================
def size_crossbar_switches():
    print(f"\n\n{'=' * 70}")
    print("  BLOCK 2: Crossbar Reset & Capacitor Array Switches")
    print("=" * 70)

    # Reset switch spec: discharge C_int (500fF) in < 2ns (during reset phase)
    c_int = 500e-15
    t_settle = 2e-9      # 5τ settling
    tau_target = t_settle / 5
    ron_target = tau_target / c_int

    print(f"\n  Reset Switch:")
    print(f"    C_int:                   {c_int*1e15:.0f} fF")
    print(f"    Settle target:           {t_settle*1e9:.0f} ns (5τ)")
    print(f"    τ target:                {tau_target*1e12:.0f} ps")
    print(f"    Ron target:              {ron_target:.0f} Ω")

    # NMOS Ron at midpoint (Vin = VDD/2, gate = VDD)
    # Ron = 1/(μn·Cox · W/L · (VDD - VDD/2 - Vt)) = 1/(μn·Cox · W/L · (VDD/2 - Vt))
    vov_sw = VDD / 2 - VT_N
    w_rst_n = 1.0 / (MU_N_COX * (1/L_MIN) * vov_sw * ron_target)  # solve for W
    # PMOS complement
    vov_sw_p = VDD / 2 - VT_P
    w_rst_p = 1.0 / (MU_P_COX * (1/L_MIN) * vov_sw_p * ron_target)

    # Parallel Ron: 1/Ron_total = 1/Ron_n + 1/Ron_p
    ron_n = ron_tgate(MU_N_COX, w_rst_n, L_MIN, VT_N)
    ron_p = ron_tgate(MU_P_COX, w_rst_p, L_MIN, VT_P)
    ron_total = 1.0 / (1.0/ron_n + 1.0/ron_p)
    tau_actual = ron_total * c_int

    print(f"    NMOS Vov (at midpoint):  {vov_sw*1e3:.0f} mV")
    print(f"    W_n (reset):             {w_rst_n*1e6:.2f} μm")
    print(f"    W_p (reset):             {w_rst_p*1e6:.2f} μm")
    print(f"    Ron_n:                   {ron_n:.0f} Ω")
    print(f"    Ron_p:                   {ron_p:.0f} Ω")
    print(f"    Ron_parallel:            {ron_total:.0f} Ω")
    print(f"    Actual τ:                {tau_actual*1e12:.0f} ps")

    # Cap array switch: charge sharing into C_unit (50fF)
    # Smaller, but needs to settle in < 1ns for SAR bit trials
    c_unit = 50e-15
    t_cap_settle = 1e-9
    tau_cap = t_cap_settle / 5
    ron_cap = tau_cap / c_unit

    print(f"\n  Cap Array Switch (CDAC):")
    print(f"    C_unit:                  {c_unit*1e15:.0f} fF")
    print(f"    Settle target:           {t_cap_settle*1e9:.0f} ns")
    print(f"    Ron target:              {ron_cap:.0f} Ω")

    w_cap_n = 1.0 / (MU_N_COX * (1/L_MIN) * vov_sw * ron_cap)
    w_cap_p = 1.0 / (MU_P_COX * (1/L_MIN) * vov_sw_p * ron_cap)
    print(f"    W_n (cap sw):            {w_cap_n*1e6:.2f} μm")
    print(f"    W_p (cap sw):            {w_cap_p*1e6:.2f} μm")

    # Mux switch: same as cap array (driving comparator input cap)
    print(f"\n  Analog Mux Switch:")
    print(f"    Same as cap array:       W_n={w_cap_n*1e6:.2f}μm, W_p={w_cap_p*1e6:.2f}μm")

    print(f"\n  {'─'*50}")
    print(f"  SWITCH SIZING SUMMARY (sky130, L=0.15μm):")
    print(f"  {'─'*50}")
    print(f"    Reset TG:   W_n = {w_rst_n*1e6:.2f} μm, W_p = {w_rst_p*1e6:.2f} μm")
    print(f"    CDAC/Mux:   W_n = {w_cap_n*1e6:.2f} μm, W_p = {w_cap_p*1e6:.2f} μm")

    return {
        "rst_wn": w_rst_n, "rst_wp": w_rst_p,
        "cap_wn": w_cap_n, "cap_wp": w_cap_p
    }


# ============================================================
# Block 3: Async Controller (Delay Chains + Logic)
# ============================================================
def size_async_ctrl():
    print(f"\n\n{'=' * 70}")
    print("  BLOCK 3: Async Controller — Delay Chains & Logic Gates")
    print("=" * 70)

    # Target delays:
    # Reset phase: ~5ns (10 stages)
    # Settle phase: ~10ns (20 stages)
    t_rst_total = 5e-9
    t_settle_total = 10e-9
    n_rst = 10
    n_settle = 20
    tp_rst = t_rst_total / n_rst      # 500ps per stage
    tp_settle = t_settle_total / n_settle  # 500ps per stage

    print(f"\n  Delay targets:")
    print(f"    Reset chain:    {t_rst_total*1e9:.0f} ns / {n_rst} stages = {tp_rst*1e12:.0f} ps/stage")
    print(f"    Settle chain:   {t_settle_total*1e9:.0f} ns / {n_settle} stages = {tp_settle*1e12:.0f} ps/stage")

    # Inverter delay: tp ≈ 0.69 × Cload / I_avg
    # For a given Cload, solve for W (which sets I_avg)
    # Or: for given W, solve for required Cload to hit target delay

    # Min-size inverter intrinsic delay (no load, just wiring + next gate cap)
    # In sky130: tp_int ≈ 10-15ps for min-size
    # With FO4 load (4× gate cap): tp_FO4 ≈ 40-60ps
    # To get 500ps/stage with min-size, need explicit load cap

    # Approach: use min-size inverters + explicit Cload
    wn_min = 0.42e-6
    wp_min = 0.84e-6  # 2:1 P:N ratio for equal rise/fall

    # Solve for Cload to get target delay
    # tp ≈ 0.69 × Cload × VDD / (2 × I_avg)
    # I_avg (pull-down) ≈ (μn·Cox/2) × (Wn/Ln) × (VDD-Vtn)² × 0.5
    i_avg_n = (MU_N_COX / 2) * (wn_min / L_MIN) * (VDD - VT_N)**2 * 0.5
    i_avg_p = (MU_P_COX / 2) * (wp_min / L_MIN) * (VDD - VT_P)**2 * 0.5
    i_avg = (i_avg_n + i_avg_p) / 2

    # tp = 0.69 × Cload × VDD / (2 × I_avg) → Cload = tp × 2 × I_avg / (0.69 × VDD)
    c_load_target = tp_rst * 2 * i_avg / (0.69 * VDD)

    print(f"\n  Min-size inverter (Wn=0.42μm, Wp=0.84μm, L=0.15μm):")
    print(f"    I_avg (pull-down):       {i_avg_n*1e6:.1f} μA")
    print(f"    I_avg (pull-up):         {i_avg_p*1e6:.1f} μA")
    print(f"    I_avg (combined):        {i_avg*1e6:.1f} μA")
    print(f"    Required Cload:          {c_load_target*1e15:.1f} fF  (for {tp_rst*1e12:.0f} ps/stage)")

    # Verify with inv_delay function
    tp_calc = inv_delay(c_load_target, MU_N_COX, wn_min, L_MIN, MU_P_COX, wp_min, L_MIN)
    print(f"    Verify tp:               {tp_calc*1e12:.0f} ps")

    # Gate sizing for NAND2 (in critical path)
    # NAND2: series NMOS → 2× Ron, parallel PMOS → 1× Ron
    # To match inverter drive: Wn_nand = 2×Wn_inv, Wp_nand = Wp_inv
    wn_nand = 2 * wn_min
    wp_nand = wp_min  # each PMOS same as inv

    print(f"\n  NAND2 Gate (equal drive to inverter):")
    print(f"    W_n (series):            {wn_nand*1e6:.2f} μm (2× inv)")
    print(f"    W_p (parallel):          {wp_nand*1e6:.2f} μm (1× inv)")

    # Buffer inverters (drive external load — xbar_rst drives crossbar reset caps)
    # Load: 4 × (Cg_reset_sw) + wiring
    # Cg ≈ Cox × W × L for each transistor in reset TG
    # For now, size buffer at 4× min for good drive
    wn_buf = 4 * wn_min
    wp_buf = 4 * wp_min
    print(f"\n  Output Buffer (4× drive for xbar_rst, adc_go):")
    print(f"    W_n:                     {wn_buf*1e6:.2f} μm")
    print(f"    W_p:                     {wp_buf*1e6:.2f} μm")

    # Power: dynamic power of delay chains
    # P_dyn = N × Cload × VDD² × f_switch
    # Single-shot (not clocked): energy per compute = N × Cload × VDD²
    e_rst = n_rst * c_load_target * VDD**2
    e_settle = n_settle * c_load_target * VDD**2
    e_total = e_rst + e_settle
    print(f"\n  Energy per compute cycle:")
    print(f"    Reset chain:             {e_rst*1e15:.1f} fJ")
    print(f"    Settle chain:            {e_settle*1e15:.1f} fJ")
    print(f"    Total ctrl energy:       {e_total*1e15:.1f} fJ")

    print(f"\n  {'─'*50}")
    print(f"  ASYNC CTRL SIZING SUMMARY (sky130, L=0.15μm):")
    print(f"  {'─'*50}")
    print(f"    Delay inv:  W_n=0.42μm, W_p=0.84μm, Cload={c_load_target*1e15:.0f}fF")
    print(f"    NAND2:      W_n={wn_nand*1e6:.2f}μm, W_p={wp_nand*1e6:.2f}μm")
    print(f"    Buffer:     W_n={wn_buf*1e6:.2f}μm, W_p={wp_buf*1e6:.2f}μm")

    return {"c_load": c_load_target, "wn_nand": wn_nand, "wp_nand": wp_nand}


# ============================================================
# Block 4: Capacitor Sizing (kT/C Noise)
# ============================================================
def size_capacitors():
    print(f"\n\n{'=' * 70}")
    print("  BLOCK 4: Capacitor Sizing — kT/C Noise Analysis")
    print("=" * 70)

    k_B = 1.38e-23  # Boltzmann
    T = 300          # Kelvin

    # ADC resolution: 4-bit, Vref = 0.9V
    n_bits = 4
    v_lsb = VREF / (2**n_bits)  # 56.25 mV

    print(f"\n  ADC specs:")
    print(f"    Resolution:              {n_bits} bits")
    print(f"    Vref:                    {VREF} V")
    print(f"    LSB:                     {v_lsb*1e3:.2f} mV")

    # kT/C noise must be < LSB/2 for no degradation (at least)
    # σ_noise = sqrt(kT/C), want σ < LSB/(2×√12) for < 0.5 LSB RMS
    sigma_target = v_lsb / (2 * math.sqrt(12))
    c_min_noise = k_B * T / (sigma_target**2)

    print(f"\n  Noise constraint:")
    print(f"    σ_target (< 0.5 LSB):   {sigma_target*1e3:.2f} mV")
    print(f"    C_min (kT/C):            {c_min_noise*1e15:.1f} fF")

    # CDAC unit cap
    c_unit = 50e-15
    c_total_cdac = c_unit * (2**n_bits - 1)  # 750fF total
    sigma_cdac = math.sqrt(k_B * T / c_total_cdac)

    print(f"\n  CDAC:")
    print(f"    C_unit:                  {c_unit*1e15:.0f} fF")
    print(f"    C_total (Σ binary):      {c_total_cdac*1e15:.0f} fF")
    print(f"    σ_noise (CDAC):          {sigma_cdac*1e3:.2f} mV  ({'OK' if sigma_cdac < sigma_target else 'TOO HIGH'})")

    # Crossbar integration cap
    c_int = 500e-15
    # After charge sharing: C_eff = C_int || (N_active × C_weight)
    # Worst case: all 4 rows active, all weights max
    c_xpt_total = 4 * c_unit * 15  # 4 rows × 15 units max
    c_col_total = c_int + c_xpt_total
    sigma_col = math.sqrt(k_B * T / c_col_total)

    print(f"\n  Crossbar column:")
    print(f"    C_int:                   {c_int*1e15:.0f} fF")
    print(f"    C_xpt (4 rows, max W):  {c_xpt_total*1e15:.0f} fF")
    print(f"    C_col_total:             {c_col_total*1e15:.0f} fF")
    print(f"    σ_noise (column):        {sigma_col*1e3:.2f} mV  ({'OK' if sigma_col < sigma_target else 'TOO HIGH'})")

    # Signal swing analysis
    # V_col = Σ(Vi × Ci) / C_col_total
    # With identity weight (15 units), input at full scale (0.9V):
    # V_col = 0.9 × 750fF / (500fF + 750fF) = 0.54V
    v_col_max = VREF * (c_unit * 15) / (c_int + c_unit * 15)
    snr_db = 20 * math.log10(v_col_max / sigma_col)
    enob = (snr_db - 1.76) / 6.02

    print(f"\n  Signal analysis:")
    print(f"    V_col_max (single row):  {v_col_max*1e3:.0f} mV")
    print(f"    SNR (kT/C limited):      {snr_db:.1f} dB")
    print(f"    ENOB:                    {enob:.1f} bits")

    print(f"\n  {'─'*50}")
    print(f"  CAPACITOR SIZING SUMMARY:")
    print(f"  {'─'*50}")
    print(f"    C_unit (CDAC & xbar):  {c_unit*1e15:.0f} fF  (noise OK)")
    print(f"    C_int (column):        {c_int*1e15:.0f} fF  (sets attenuation)")
    print(f"    ENOB (noise-limited):  {enob:.1f} bits > {n_bits} bits ✓")

    return {"c_unit": c_unit, "c_int": c_int, "enob": enob}


# ============================================================
# Final Summary: Recommended Sizes vs Current Sizes
# ============================================================
def print_comparison(sa, sw, ctrl, caps):
    print(f"\n\n{'=' * 70}")
    print("  FINAL COMPARISON: Current vs Gm/Id-Optimized Sizing")
    print("=" * 70)

    rows = [
        ("StrongARM Tail (NMOS)", "2.0", f"{sa['w_tail']*1e6:.2f}", "deep strong inv, sets speed"),
        ("StrongARM Input (NMOS)", "2.0", f"{sa['w_in']*1e6:.2f}", "moderate inv, gm/Id≈13"),
        ("StrongARM Latch N", "1.0", f"{sa['w_latch_n']*1e6:.2f}", "fast regen"),
        ("StrongARM Latch P", "4.0", f"{sa['w_latch_p']*1e6:.2f}", "match N gm"),
        ("StrongARM Reset P", "1.0", f"{sa['w_reset']*1e6:.2f}", "fast precharge"),
        ("Reset TG (NMOS)", "0.84", f"{sw['rst_wn']*1e6:.2f}", "discharge 500fF in 2ns"),
        ("Reset TG (PMOS)", "1.68", f"{sw['rst_wp']*1e6:.2f}", "complement"),
        ("CDAC/Mux TG (NMOS)", "0.42", f"{sw['cap_wn']*1e6:.2f}", "settle 50fF in 1ns"),
        ("CDAC/Mux TG (PMOS)", "0.84", f"{sw['cap_wp']*1e6:.2f}", "complement"),
        ("Delay Inv (NMOS)", "0.42", "0.42", "min-size + Cload"),
        ("Delay Inv (PMOS)", "0.84", "0.84", "2:1 ratio"),
        ("NAND2 (NMOS)", "0.42", f"{ctrl['wn_nand']*1e6:.2f}", "2× for series stack"),
        ("NAND2 (PMOS)", "0.84", "0.84", "parallel = 1×"),
    ]

    print(f"\n  {'Block':<25}{'Current':<10}{'Optimized':<12}{'Rationale'}")
    print(f"  {'─'*75}")
    for name, curr, opt, reason in rows:
        flag = " ←" if curr != opt else ""
        print(f"  {name:<25}{curr:<10}{opt:<12}{reason}{flag}")

    print(f"\n  All L = 0.15 μm (minimum for sky130)")
    print(f"  Delay chain Cload = {ctrl['c_load']*1e15:.0f} fF per stage")
    print(f"  C_unit = {caps['c_unit']*1e15:.0f} fF, C_int = {caps['c_int']*1e15:.0f} fF")


# ============================================================
# Main
# ============================================================
if __name__ == "__main__":
    print("\n  Gm/Id TRANSISTOR SIZING — MVM Charge-Domain IMC (Sky130)")
    print(f"  VDD={VDD}V, Vref={VREF}V, T=27°C, TT corner\n")

    sa = size_strongarm()
    sw = size_crossbar_switches()
    ctrl = size_async_ctrl()
    caps = size_capacitors()
    print_comparison(sa, sw, ctrl, caps)
    print()
