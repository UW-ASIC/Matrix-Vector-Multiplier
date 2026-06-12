import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pyspice_rs  # noqa: F401
from library.pdks import get_pdk

pdk = get_pdk()
sz = pdk.sizing

IN_W, IN_L = sz["comp_input"]
REG_P_W, REG_P_L = sz["comp_latch_p"]
REG_N_W, REG_N_L = sz["comp_latch_n"]
TAIL_W, TAIL_L = sz["comp_tail"]
RST_W, RST_L = sz["comp_reset"]


def generate() -> str:
    lines = [".subckt strongarm vinp vinn outp outn clk vdd vss"]

    lines.append(pdk.mos("tail", "tail", "clk", "vss", "vss", pdk.nfet, W=TAIL_W, L=TAIL_L))
    lines.append(pdk.mos("inp", "drn_p", "vinp", "tail", "vss", pdk.nfet, W=IN_W, L=IN_L))
    lines.append(pdk.mos("inn", "drn_n", "vinn", "tail", "vss", pdk.nfet, W=IN_W, L=IN_L))
    lines.append(pdk.mos("xnp", "outp", "outn", "drn_p", "vss", pdk.nfet, W=REG_N_W, L=REG_N_L))
    lines.append(pdk.mos("xnn", "outn", "outp", "drn_n", "vss", pdk.nfet, W=REG_N_W, L=REG_N_L))
    lines.append(pdk.mos("xpp", "outp", "outn", "vdd", "vdd", pdk.pfet, W=REG_P_W, L=REG_P_L))
    lines.append(pdk.mos("xpn", "outn", "outp", "vdd", "vdd", pdk.pfet, W=REG_P_W, L=REG_P_L))
    lines.append(pdk.mos("rstp", "outp", "clk", "vdd", "vdd", pdk.pfet, W=RST_W, L=RST_L))
    lines.append(pdk.mos("rstn", "outn", "clk", "vdd", "vdd", pdk.pfet, W=RST_W, L=RST_L))

    lines.append(".ends strongarm")
    return "\n".join(lines)


if __name__ == "__main__":
    print(generate())
