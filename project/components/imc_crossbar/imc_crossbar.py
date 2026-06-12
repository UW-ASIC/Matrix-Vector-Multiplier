import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pyspice_rs  # noqa: F401
from library.cap_array import cap_array_spice
from library.cmos_switch import cmos_switch_spice
from library.pdks import get_pdk

pdk = get_pdk()
sz = pdk.sizing

N_ROWS = 3
N_COLS = 3
WEIGHT_BITS = 4
C_UNIT = pdk.caps["c_unit"]
C_INT = pdk.caps["c_int"]


def generate() -> str:
    lines = []

    # Crosspoint cap array
    cap_name = "imc_crossbar_xpt_cap"
    xpt_wn, xpt_ln = sz["xbar_xpt_n"]
    xpt_wp, xpt_lp = sz["xbar_xpt_p"]
    lines.append(cap_array_spice(cap_name, WEIGHT_BITS, C_UNIT,
                                 w_n=xpt_wn, l_n=xpt_ln, w_p=xpt_wp, l_p=xpt_lp))
    lines.append("")

    # Reset switch
    rst_sw = "imc_crossbar_rst_sw"
    rst_wn, rst_ln = sz["xbar_rst_n"]
    rst_wp, rst_lp = sz["xbar_rst_p"]
    lines.append(cmos_switch_spice(rst_sw, w_n=rst_wn, l_n=rst_ln, w_p=rst_wp, l_p=rst_lp))
    lines.append("")

    # Main crossbar
    row_ports = " ".join(f"x{i}" for i in range(N_ROWS))
    col_ports = " ".join(f"y{j}" for j in range(N_COLS))
    wb_ports = " ".join(
        f"wb_{i}{j}{b}"
        for i in range(N_ROWS) for j in range(N_COLS) for b in range(WEIGHT_BITS)
    )
    lines.append(f".subckt imc_crossbar {row_ports} {col_ports} {wb_ports} rst vdd vss")

    lines.extend(pdk.inv("rst_inv", "rst_b", "rst", "vdd", "vss"))

    for j in range(N_COLS):
        lines.append(f"Cint_{j} y{j} vss {C_INT}")
        lines.append(f"Xrst_sw_{j} y{j} vss rst rst_b vdd vss {rst_sw}")
        for i in range(N_ROWS):
            wb = " ".join(f"wb_{i}{j}{b}" for b in range(WEIGHT_BITS))
            lines.append(f"Xxpt_{i}_{j} {wb} y{j} x{i} vdd vss {cap_name}")

    lines.append(".ends imc_crossbar")
    return "\n".join(lines)


if __name__ == "__main__":
    print(generate())
