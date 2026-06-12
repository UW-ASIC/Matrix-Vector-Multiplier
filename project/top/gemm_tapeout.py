"""TinyTapeout 3x3 GEMM Accelerator Top Level.

3x3 MVM via charge-domain crossbar. Fully digital I/O.

TinyTapeout Pin Map (active during each phase):
  clk            — TT clock
  rst_n          — active-low reset (resets FSM + crossbar)
  ena            — TT enable

  ui_in[7:4]     — data_hi: weight/input for col0 (LOAD_W) or x0 (LOAD_X)
  ui_in[3:0]     — data_lo: weight/input for col1 (LOAD_W) or x1 (LOAD_X)
  uio_in[3:0]    — data_ext: weight/input for col2 (LOAD_W) or x2 (LOAD_X)
  uio_in[5:4]    — row_addr: selects row 0/1/2 for LOAD_W
  uio_in[7:6]    — opcode: 00=NOP, 01=LOAD_W, 10=LOAD_X, 11=READ_Y

  uo_out[7:4]    — result_hi: y0 (4-bit ADC output, col0)
  uo_out[3:0]    — result_lo: y1 (4-bit ADC output, col1)
  uio_out[3:0]   — result_ext: y2 (4-bit ADC output, col2)
  uio_out[7:4]   — status (bit 7 = done)
  uio_oe[7:0]    — output enables (set by FSM: low 4 during READ_Y)

FSM (6 cycles per GEMM):
  Cycle 0-2: LOAD_W — load weight row 0,1,2 (3 x 4-bit weights per cycle)
  Cycle 3:   LOAD_X — load input vector (3 x 4-bit values)
  Cycle 4:   COMPUTE — crossbar MAC + ADC conversion
  Cycle 5:   READ_Y — output 3 x 4-bit results

Analog path: charge_dac -> S&H -> 3x3 crossbar -> interleaved ADC
Digital path: weight/input latches (behavioral) + output mux

Ports: ui0..7, uo0..7, uio0..7, uio_oe,
       sh_ctrl, xbar_rst, adc_go, wr_en, dac_ld, vref, vdd, vss
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pyspice_rs  # noqa: F401
from library.cmos_switch import cmos_switch_spice
from library.pdks import get_pdk

pdk = get_pdk()
inv = pdk.inv

N_ROWS = 3
N_COLS = 3
N_BITS = 4


def generate() -> str:
    lines = []

    # Sub-subcircuits
    sh_sw = "gemm_sh_sw"
    lines.append(cmos_switch_spice(sh_sw))
    lines.append("")

    # Top-level ports
    ui = " ".join(f"ui{i}" for i in range(8))
    uo = " ".join(f"uo{i}" for i in range(8))
    uio = " ".join(f"uio{i}" for i in range(8))
    ctrl = "uio_oe sh_ctrl xbar_rst adc_go wr_en dac_ld"

    lines.append(f".subckt gemm_tapeout {ui} {uo} {uio} {ctrl} vref vdd vss")

    # ============================================================
    # ANALOG SIGNAL PATH
    # ============================================================

    # 3 Input DACs (charge_dac: vref, b0..b3, out, vdd, vss)
    for i in range(N_ROWS):
        bits = " ".join(f"dac{i}_b{b}" for b in range(N_BITS))
        lines.append(f"Xdac{i} vref {bits} dac{i}_out vdd vss charge_dac")

    # S&H on DAC outputs
    lines.extend(inv("sh_inv", "sh_ctrl_b", "sh_ctrl", "vdd", "vss"))
    for i in range(N_ROWS):
        lines.append(f"Xsh{i} dac{i}_out xbar_in{i} sh_ctrl sh_ctrl_b vdd vss {sh_sw}")
        lines.append(f"Csh{i} xbar_in{i} vss {pdk.caps['c_hold']}")

    # 3x3 IMC Crossbar
    xbar_x = " ".join(f"xbar_in{i}" for i in range(N_ROWS))
    xbar_y = " ".join(f"col{j}" for j in range(N_COLS))
    xbar_wb = " ".join(
        f"wb_{i}{j}{b}"
        for i in range(N_ROWS) for j in range(N_COLS) for b in range(N_BITS)
    )
    lines.append(f"Xxbar {xbar_x} {xbar_y} {xbar_wb} xbar_rst vdd vss imc_crossbar")

    # Interleaved ADC (3 columns)
    col_ports = " ".join(f"col{j}" for j in range(N_COLS))
    adc_d = " ".join(f"adc_d{j}b{b}" for j in range(N_COLS) for b in range(N_BITS))
    lines.append(f"Xadc {col_ports} vref {adc_d} adc_go vdd vss interleaved_adc")

    # ============================================================
    # DIGITAL DATA PATH (behavioral latches)
    # ============================================================

    # Weight register: 36-bit (3x3x4), loaded row-by-row via wr_en
    # Row address from uio[5:4], data from ui[7:4]=col0, ui[3:0]=col1, uio[3:0]=col2
    lines.append("* Weight register (36-bit, row-addressed via uio[5:4])")

    # Decode row address: row_sel_i = (uio4,uio5) == i
    lines.append("B_row_addr row_addr vss V = V(uio4) + 2*V(uio5)")
    for i in range(N_ROWS):
        lines.append(
            f"B_row_sel{i} row_sel{i} vss V = "
            f"abs(V(row_addr) - {i}*V(vdd)) < 0.5*V(vdd) ? V(vdd) : 0")

    for i in range(N_ROWS):
        for j in range(N_COLS):
            for b in range(N_BITS):
                # Source pin mapping: col0→ui[7:4], col1→ui[3:0], col2→uio[3:0]
                if j == 0:
                    src = f"ui{b + 4}"
                elif j == 1:
                    src = f"ui{b}"
                else:
                    src = f"uio{b}"
                # Latch: update only when wr_en HIGH and row_sel matches
                lines.append(
                    f"B_wb_{i}{j}{b} wb_{i}{j}{b} vss V = "
                    f"V(wr_en) > 0.9 && V(row_sel{i}) > 0.9 ? V({src}) : V(wb_{i}{j}{b})")

    # Input DAC register: 3x4-bit, loaded from ui+uio when dac_ld=HIGH
    # x0→ui[7:4], x1→ui[3:0], x2→uio[3:0]
    lines.append("* DAC input latches (loaded via dac_ld)")
    for i in range(N_ROWS):
        for b in range(N_BITS):
            if i == 0:
                src = f"ui{b + 4}"
            elif i == 1:
                src = f"ui{b}"
            else:
                src = f"uio{b}"
            lines.append(
                f"B_dac{i}_b{b} dac{i}_b{b} vss V = "
                f"V(dac_ld) > 0.9 ? V({src}) : V(dac{i}_b{b})")

    # Output mux: ADC results to output pins during read (uio_oe=HIGH)
    # y0→uo[7:4], y1→uo[3:0], y2→uio[3:0]
    lines.append("* Output drivers")
    for j in range(N_COLS):
        for b in range(N_BITS):
            if j == 0:
                pin = f"uo{b + 4}"
            elif j == 1:
                pin = f"uo{b}"
            else:
                pin = f"uio{b}"
            lines.append(
                f"B_out_{j}{b} {pin} vss V = "
                f"V(uio_oe) > 0.9 ? V(adc_d{j}b{b}) : 0")

    # Status output: done flag on uio7
    lines.append("B_done uio7 vss V = V(uio_oe) > 0.9 ? V(vdd) : 0")

    lines.append(".ends gemm_tapeout")
    return "\n".join(lines)


if __name__ == "__main__":
    print(generate())
