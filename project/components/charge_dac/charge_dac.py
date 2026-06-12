import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pyspice_rs  # noqa: F401
from library.cmos_switch import cmos_switch_spice
from library.pdks import get_pdk

pdk = get_pdk()
sz = pdk.sizing

N_BITS = 4
C_UNIT = pdk.caps["c_unit"]


def generate() -> str:
    lines = []

    sw_name = "charge_dac_sw"
    w_n, l_n = sz["dac_sw_n"]
    w_p, l_p = sz["dac_sw_p"]
    lines.append(cmos_switch_spice(sw_name, w_n=w_n, l_n=l_n, w_p=w_p, l_p=l_p))
    lines.append("")

    lines.append(".subckt charge_dac vref b0 b1 b2 b3 out vdd vss")

    for i in range(N_BITS):
        cap_val = C_UNIT * (2 ** i)
        lines.extend(pdk.inv(f"inv{i}", f"b{i}_b", f"b{i}", "vdd", "vss"))
        lines.append(f"Xsw_hi{i} vref cap_bot_{i} b{i} b{i}_b vdd vss {sw_name}")
        lines.append(f"Xsw_lo{i} vss cap_bot_{i} b{i}_b b{i} vdd vss {sw_name}")
        lines.append(f"Cb{i} out cap_bot_{i} {cap_val}")

    lines.append("Rbias out vss 10G")
    lines.append(".ends charge_dac")
    return "\n".join(lines)


if __name__ == "__main__":
    print(generate())
