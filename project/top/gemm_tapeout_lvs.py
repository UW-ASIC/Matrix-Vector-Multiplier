"""Structural LVS netlist for gemm_tapeout — no behavioral B-sources.

Port list matches Magic flat extraction (gemm_tapeout_flat) EXACTLY.
All subcircuits are structural (transistors + caps only, no B-sources).
"""

import sys
import os
import re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pyspice_rs  # noqa: F401
from library.cmos_switch import cmos_switch_spice
from library.pdks import get_pdk

pdk = get_pdk()
inv = pdk.inv

N_ROWS = 3
N_COLS = 3
N_BITS = 4

# Device sizes from layout (interleaved_adc.py)
MUX_N_W, MUX_N_L = 0.42, 0.15
MUX_P_W, MUX_P_L = 1.42, 0.15
BUF_N_W, BUF_N_L = 0.42, 0.15
BUF_P_W, BUF_P_L = 0.84, 0.15

NFET = "sky130_fd_pr__nfet_01v8"
PFET = "sky130_fd_pr__pfet_01v8"


def _strip_subckt(text: str, name: str) -> str:
    """Remove a .subckt ... .ends block from SPICE text."""
    pattern = rf"^\.subckt {re.escape(name)} .*?^\.ends {re.escape(name)}"
    return re.sub(pattern, "", text, flags=re.MULTILINE | re.DOTALL)


def _structural_interleaved_adc() -> str:
    """Generate structural interleaved_adc matching the layout exactly.

    Layout has per ADC unit:
      - 2 CMOS mux TGs (iadc_mux_sw)
      - 1 StrongARM comparator (9 MOSFETs)
      - 1 CDAC (iadc_cdac: 4 bit caps + 8 switches + 4 inverters)
      - 2 SAR buffer banks (4 bits × 2 inverters = 16 MOSFETs each)
    """
    lines = []
    # Define SAR buffer inverter subcircuit
    lines.append(f".subckt iadc_sar_inv a y vdd vss")
    lines.append(f"Xn y a vss vss {NFET} W={BUF_N_W} L={BUF_N_L}")
    lines.append(f"Xp y a vdd vdd {PFET} W={BUF_P_W} L={BUF_P_L}")
    lines.append(f".ends iadc_sar_inv")
    lines.append("")

    # interleaved_adc ports match the behavioral version
    ports = ["col0", "col1", "col2", "vref"]
    ports += [f"d{j}b{b}" for j in range(N_COLS) for b in range(N_BITS)]
    ports += ["adc_go", "vdd", "vss"]

    lines.append(f".subckt interleaved_adc {' '.join(ports)}")
    lines.append("")

    # ---- Unit 0: handles col0 (mux_a), col1 (mux_b) ----
    # ---- Unit 1: handles col2 (mux_a), col2 again (mux_b — only 3 cols) ----
    unit_cols = [
        ("u0", "col0", "col1", "d0b", "d1b"),
        ("u1", "col2", "col2", "d2b", "d2b"),  # u1 only handles col2
    ]

    for uid, col_a, col_b, out_a_pfx, out_b_pfx in unit_cols:
        lines.append(f"* === ADC Unit {uid} ===")
        mux_out = f"{uid}_mux_out"
        cdac_top = f"{uid}_cdac_top"

        # Mux switches (connect columns to comparator input+)
        lines.append(f"* Input mux")
        lines.append(f"X{uid}_mux_a {col_a} {mux_out} {uid}_mux_sel_a {uid}_mux_sel_ab vdd vss iadc_mux_sw")
        lines.append(f"X{uid}_mux_b {col_b} {mux_out} {uid}_mux_sel_b {uid}_mux_sel_bb vdd vss iadc_mux_sw")

        # StrongARM comparator (9T)
        lines.append(f"* StrongARM comparator")
        lines.append(f"X{uid}_tail {uid}_tail adc_go vss vss {NFET} W=0.42 L=0.15")
        lines.append(f"X{uid}_inp {uid}_drn_p {mux_out} {uid}_tail vss {NFET} W=7.0 L=0.15")
        lines.append(f"X{uid}_inn {uid}_drn_n {cdac_top} {uid}_tail vss {NFET} W=7.0 L=0.15")
        lines.append(f"X{uid}_xnp {uid}_outp {uid}_outn {uid}_drn_p vss {NFET} W=1.0 L=0.15")
        lines.append(f"X{uid}_xnn {uid}_outn {uid}_outp {uid}_drn_n vss {NFET} W=1.0 L=0.15")
        lines.append(f"X{uid}_xpp {uid}_outp {uid}_outn vdd vdd {PFET} W=4.5 L=0.15")
        lines.append(f"X{uid}_xpn {uid}_outn {uid}_outp vdd vdd {PFET} W=4.5 L=0.15")
        lines.append(f"X{uid}_rstp {uid}_outp adc_go vdd vdd {PFET} W=1.0 L=0.15")
        lines.append(f"X{uid}_rstn {uid}_outn adc_go vdd vdd {PFET} W=1.0 L=0.15")

        # Parasitic caps
        lines.append(f"C{uid}_tail {uid}_tail vss 5f")
        lines.append(f"C{uid}_drp {uid}_drn_p vss 2f")
        lines.append(f"C{uid}_drn {uid}_drn_n vss 2f")
        lines.append(f"C{uid}_outp {uid}_outp vss 2f")
        lines.append(f"C{uid}_outn {uid}_outn vss 2f")

        # CDAC
        lines.append(f"* CDAC")
        sw_nets = " ".join(f"{uid}_sw{b}" for b in range(N_BITS))
        lines.append(f"X{uid}_cdac {sw_nets} {cdac_top} vref vdd vss iadc_cdac")
        lines.append(f"Rbias_{uid}_cdac {cdac_top} vss 10G")

        # SAR output buffers (channel A: 4 bits)
        lines.append(f"* SAR output buffers channel A")
        for b in range(N_BITS):
            mid = f"{uid}_buf_a{b}_mid"
            lines.append(f"X{uid}_buf_a{b}_1 {uid}_sar_a_in{b} {mid} vdd vss iadc_sar_inv")
            lines.append(f"X{uid}_buf_a{b}_2 {mid} {out_a_pfx}{b} vdd vss iadc_sar_inv")

        # SAR output buffers (channel B: 4 bits)
        lines.append(f"* SAR output buffers channel B")
        for b in range(N_BITS):
            mid = f"{uid}_buf_b{b}_mid"
            lines.append(f"X{uid}_buf_b{b}_1 {uid}_sar_b_in{b} {mid} vdd vss iadc_sar_inv")
            lines.append(f"X{uid}_buf_b{b}_2 {mid} {out_b_pfx}{b} vdd vss iadc_sar_inv")

        lines.append("")

    lines.append(".ends interleaved_adc")
    return "\n".join(lines)


def generate() -> str:
    """Generate structural-only SPICE for LVS comparison."""
    lines = []

    # ------------------------------------------------------------------
    # 1. Import component subcircuit definitions
    # ------------------------------------------------------------------
    from components.sample_hold_bank.sample_hold_bank import generate as gen_sh
    from components.imc_crossbar.imc_crossbar import generate as gen_xbar
    from components.interleaved_adc.interleaved_adc import generate as gen_adc
    from components.async_ctrl.async_ctrl import generate as gen_async
    from components.charge_dac.charge_dac import generate as gen_dac

    lines.append("* === Component subcircuits for LVS ===")
    lines.append("")

    lines.append(gen_dac())
    lines.append("")
    lines.append(gen_sh())
    lines.append("")
    lines.append(gen_xbar())
    lines.append("")

    # ADC: keep subcircuit definitions but replace the behavioral
    # interleaved_adc with structural version
    adc_text = gen_adc()
    adc_text = _strip_subckt(adc_text, "interleaved_adc")
    lines.append(adc_text)
    lines.append("")
    lines.append(_structural_interleaved_adc())
    lines.append("")

    lines.append(gen_async())
    lines.append("")

    # ------------------------------------------------------------------
    # 2. CMOS switch for S&H (used in top-level)
    # ------------------------------------------------------------------
    sh_sw = "gemm_sh_sw"
    lines.append(cmos_switch_spice(sh_sw))
    lines.append("")

    # ------------------------------------------------------------------
    # 3. Top-level — port list matches extraction EXACTLY
    # ------------------------------------------------------------------
    ports = []
    ports.append("clk ena rst_n")
    ports.append(" ".join(f"ui_in[{i}]" for i in range(8)))
    ports.append(" ".join(f"uio_in[{i}]" for i in range(8)))
    ports.append(" ".join(f"uo_out[{i}]" for i in range(8)))
    ports.append(" ".join(f"uio_out[{i}]" for i in range(8)))
    ports.append(" ".join(f"uio_oe[{i}]" for i in range(8)))
    ports.append("VPWR VGND")

    port_str = " ".join(ports)
    lines.append(f".subckt gemm_tapeout {port_str}")
    lines.append("")

    # All TT pins are floating stubs (met4 at top edge, no internal routing)
    lines.append("* All uo_out/uio_out/uio_oe/ui_in/uio_in/clk/ena/rst_n/VPWR/VGND")
    lines.append("* are floating met4 stubs — no connection to internal circuitry")
    lines.append("")

    # ============================================================
    # ANALOG SIGNAL PATH
    # ============================================================

    # 3 Input DACs
    lines.append("* Input DACs")
    for i in range(N_ROWS):
        bits = " ".join(f"dac{i}_b{b}" for b in range(N_BITS))
        lines.append(f"Xdac{i} vref {bits} dac{i}_out vdd vss charge_dac")

    lines.append("")

    # S&H on DAC outputs
    lines.append("* Sample-and-hold switches")
    lines.extend(inv("sh_inv", "sh_ctrl_b", "sh_ctrl", "vdd", "vss"))
    for i in range(N_ROWS):
        lines.append(f"Xsh{i} dac{i}_out xbar_in{i} sh_ctrl sh_ctrl_b vdd vss {sh_sw}")
        lines.append(f"Csh{i} xbar_in{i} vss {pdk.caps['c_hold']}")

    lines.append("")

    # 3x3 IMC Crossbar
    lines.append("* 3x3 IMC crossbar")
    xbar_x = " ".join(f"xbar_in{i}" for i in range(N_ROWS))
    xbar_y = " ".join(f"col{j}" for j in range(N_COLS))
    xbar_wb = " ".join(
        f"wb_{i}{j}{b}"
        for i in range(N_ROWS) for j in range(N_COLS) for b in range(N_BITS)
    )
    lines.append(f"Xxbar {xbar_x} {xbar_y} {xbar_wb} xbar_rst vdd vss imc_crossbar")

    lines.append("")

    # Interleaved ADC (3 columns, structural)
    lines.append("* Interleaved ADC (structural)")
    col_ports = " ".join(f"col{j}" for j in range(N_COLS))
    adc_d = " ".join(f"adc_d{j}b{b}" for j in range(N_COLS) for b in range(N_BITS))
    lines.append(f"Xadc {col_ports} vref {adc_d} adc_go vdd vss interleaved_adc")

    lines.append("")

    # Async controller
    lines.append("* Async controller")
    lines.append("Xasync go_sig adc_done xbar_rst adc_go latch_out done vdd vss async_ctrl")

    lines.append("")

    lines.append(".ends gemm_tapeout")
    return "\n".join(lines)


if __name__ == "__main__":
    print(generate())
