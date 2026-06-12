import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pyspice_rs  # noqa: F401
from library.cap_array import cap_array_spice
from library.cmos_switch import cmos_switch_spice
from library.pdks import get_pdk

pdk = get_pdk()
sz = pdk.sizing

N_COLS = 3
N_BITS = 4
C_UNIT = pdk.caps["c_unit"]

IN_W, IN_L = sz["comp_input"]
REG_P_W, REG_P_L = sz["comp_latch_p"]
REG_N_W, REG_N_L = sz["comp_latch_n"]
TAIL_W, TAIL_L = sz["comp_tail"]
RST_W, RST_L = sz["comp_reset"]


def generate() -> str:
    lines = []

    # CDAC cap array
    cdac_name = "iadc_cdac"
    lines.append(cap_array_spice(cdac_name, N_BITS, C_UNIT))
    lines.append("")

    # Mux switch
    mux_sw = "iadc_mux_sw"
    mux_wn, mux_ln = sz["adc_mux_n"]
    mux_wp, mux_lp = sz["adc_mux_p"]
    lines.append(cmos_switch_spice(mux_sw, w_n=mux_wn, l_n=mux_ln, w_p=mux_wp, l_p=mux_lp))
    lines.append("")

    # Main subcircuit: 3 columns
    col_ports = " ".join(f"col{j}" for j in range(N_COLS))
    dout_ports = " ".join(
        f"d{j}b{b}" for j in range(N_COLS) for b in range(N_BITS)
    )
    lines.append(f".subckt interleaved_adc {col_ports} vref "
                 f"{dout_ports} "
                 f"adc_go vdd vss")

    # Unit 0: handles col0, col1 (interleaved, muxed through one comparator)
    # Unit 1: handles col2 (single column, dedicated comparator)
    for unit in range(2):
        if unit == 0:
            cols = [0, 1]
        else:
            cols = [2]
        u = f"u{unit}_"

        lines.append(f"* ADC Unit {unit}: columns {cols}")

        # StrongARM comparator
        lines.append(pdk.mos(f"{u}tail", f"{u}tail", "adc_go", "vss", "vss", pdk.nfet, W=TAIL_W, L=TAIL_L))
        lines.append(pdk.mos(f"{u}inp", f"{u}drn_p", f"{u}mux_out", f"{u}tail", "vss", pdk.nfet, W=IN_W, L=IN_L))
        lines.append(pdk.mos(f"{u}inn", f"{u}drn_n", f"{u}cdac_top", f"{u}tail", "vss", pdk.nfet, W=IN_W, L=IN_L))
        lines.append(pdk.mos(f"{u}xnp", f"{u}outp", f"{u}outn", f"{u}drn_p", "vss", pdk.nfet, W=REG_N_W, L=REG_N_L))
        lines.append(pdk.mos(f"{u}xnn", f"{u}outn", f"{u}outp", f"{u}drn_n", "vss", pdk.nfet, W=REG_N_W, L=REG_N_L))
        lines.append(pdk.mos(f"{u}xpp", f"{u}outp", f"{u}outn", "vdd", "vdd", pdk.pfet, W=REG_P_W, L=REG_P_L))
        lines.append(pdk.mos(f"{u}xpn", f"{u}outn", f"{u}outp", "vdd", "vdd", pdk.pfet, W=REG_P_W, L=REG_P_L))
        lines.append(pdk.mos(f"{u}rstp", f"{u}outp", "adc_go", "vdd", "vdd", pdk.pfet, W=RST_W, L=RST_L))
        lines.append(pdk.mos(f"{u}rstn", f"{u}outn", "adc_go", "vdd", "vdd", pdk.pfet, W=RST_W, L=RST_L))
        # Parasitic caps
        lines.append(f"C{u}tail {u}tail vss 5f")
        lines.append(f"C{u}drp {u}drn_p vss 2f")
        lines.append(f"C{u}drn {u}drn_n vss 2f")
        lines.append(f"C{u}outp {u}outp vss 2f")
        lines.append(f"C{u}outn {u}outn vss 2f")

        # Mux (behavioral) — unit0 muxes col0, unit1 takes col2 directly
        first_col = cols[0]
        lines.append(f"B_{u}mux {u}mux_out vss V = V(col{first_col})")

        # CDAC instance
        cdac_sw = " ".join(f"{u}sw{b}" for b in range(N_BITS))
        lines.append(f"X{u}cdac {cdac_sw} {u}cdac_top vref vdd vss {cdac_name}")
        lines.append(f"Rbias_{u}cdac {u}cdac_top vss 10G")

        # Behavioral SAR for each column handled by this unit
        for col in cols:
            cp = f"{u}col{col}_"
            levels = 2 ** N_BITS

            for bit_idx in range(N_BITS - 1, -1, -1):
                frac = (2 ** bit_idx) / levels
                if bit_idx == N_BITS - 1:
                    lines.append(
                        f"B_{cp}b{bit_idx} {cp}bit{bit_idx} vss V = "
                        f"V(col{col}) >= V(vref) * {frac} ? 1 : 0")
                    lines.append(
                        f"B_{cp}dac{bit_idx} {cp}dac{bit_idx} vss V = "
                        f"V({cp}bit{bit_idx}) * V(vref) * {frac}")
                else:
                    prev = bit_idx + 1
                    lines.append(
                        f"B_{cp}b{bit_idx} {cp}bit{bit_idx} vss V = "
                        f"V(col{col}) >= V({cp}dac{prev}) + V(vref) * {frac} ? 1 : 0")
                    lines.append(
                        f"B_{cp}dac{bit_idx} {cp}dac{bit_idx} vss V = "
                        f"V({cp}dac{prev}) + V({cp}bit{bit_idx}) * V(vref) * {frac}")

            # Drive CDAC switches from first column's SAR
            if col == cols[0]:
                for b in range(N_BITS):
                    lines.append(f"B_{cp}sw{b} {u}sw{b} vss V = V({cp}bit{b}) > 0.5 ? V(vdd) : 0")

            # Output digital bits
            for b in range(N_BITS):
                lines.append(f"B_{cp}d{b} d{col}b{b} vss V = V({cp}bit{b}) > 0.5 ? V(vdd) : 0")

    lines.append(".ends interleaved_adc")
    return "\n".join(lines)


if __name__ == "__main__":
    print(generate())
