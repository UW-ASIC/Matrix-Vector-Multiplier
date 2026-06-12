import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pyspice_rs  # noqa: F401
from library.cmos_switch import cmos_switch_spice
from library.pdks import get_pdk

pdk = get_pdk()
sz = pdk.sizing

N_CHANNELS = 3
C_HOLD = pdk.caps["c_hold"]


def generate() -> str:
    lines = []

    sw_name = "sh_bank_sw"
    w_n, l_n = sz["sh_sw_n"]
    w_p, l_p = sz["sh_sw_p"]
    lines.append(cmos_switch_spice(sw_name, w_n=w_n, l_n=l_n, w_p=w_p, l_p=l_p))
    lines.append("")

    ports = " ".join(f"in{i}" for i in range(N_CHANNELS))
    ports += " " + " ".join(f"out{i}" for i in range(N_CHANNELS))
    ports += " sh_ctrl vdd vss"
    lines.append(f".subckt sample_hold_bank {ports}")

    lines.extend(pdk.inv("inv_ctrl", "sh_ctrl_b", "sh_ctrl", "vdd", "vss"))

    for i in range(N_CHANNELS):
        lines.append(f"Xsw{i} in{i} out{i} sh_ctrl sh_ctrl_b vdd vss {sw_name}")
        lines.append(f"Chold{i} out{i} vss {C_HOLD}")

    lines.append(".ends sample_hold_bank")
    return "\n".join(lines)


if __name__ == "__main__":
    print(generate())
