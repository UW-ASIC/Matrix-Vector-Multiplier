import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pyspice_rs  # noqa: F401
from library.pdks import get_pdk

pdk = get_pdk()
sz = pdk.sizing
delay_cfg = pdk.delay

N_RST_DELAY = delay_cfg["n_rst_stages"]
N_SETTLE_DELAY = delay_cfg["n_settle_stages"]
CLOAD = delay_cfg["cload"]


def delay_chain_subckt(name, n_stages, cload=CLOAD):
    """Generate delay chain with n_stages inverters + load caps."""
    inv_wn, inv_ln = sz["inv_n"]
    inv_wp, inv_lp = sz["inv_p"]
    dl = []
    dl.append(f".subckt {name} in out vdd vss")
    for i in range(n_stages):
        src = "in" if i == 0 else f"d{i-1}"
        dst = "out" if i == n_stages - 1 else f"d{i}"
        dl.append(pdk.mos(f"n{i}", dst, src, "vss", "vss", pdk.nfet, W=inv_wn, L=inv_ln))
        dl.append(pdk.mos(f"p{i}", dst, src, "vdd", "vdd", pdk.pfet, W=inv_wp, L=inv_lp))
        dl.append(f"Cload{i} {dst} vss {cload}")
    dl.append(f".ends {name}")
    return dl


def generate() -> str:
    lines = []

    lines.extend(delay_chain_subckt("rst_delay", N_RST_DELAY))
    lines.append("")
    lines.extend(delay_chain_subckt("settle_delay", N_SETTLE_DELAY))
    lines.append("")

    # Muller C-element
    mp_w, mp_l = sz["muller_p_series"]
    mn_w, mn_l = sz["muller_n_series"]
    mk_p_w, mk_p_l = sz["muller_keeper_p"]
    mk_n_w, mk_n_l = sz["muller_keeper_n"]
    fb_p_w, fb_p_l = sz["muller_fb_p"]
    fb_n_w, fb_n_l = sz["muller_fb_n"]

    lines.append(".subckt muller_c a b out vdd vss")
    lines.append(pdk.mos("p1", "out", "a", "n1p", "vdd", pdk.pfet, W=mp_w, L=mp_l))
    lines.append(pdk.mos("p2", "n1p", "b", "vdd", "vdd", pdk.pfet, W=mp_w, L=mp_l))
    lines.append(pdk.mos("p3", "out", "out_b", "vdd", "vdd", pdk.pfet, W=mk_p_w, L=mk_p_l))
    lines.append(pdk.mos("n1", "out", "a", "n1n", "vss", pdk.nfet, W=mn_w, L=mn_l))
    lines.append(pdk.mos("n2", "n1n", "b", "vss", "vss", pdk.nfet, W=mn_w, L=mn_l))
    lines.append(pdk.mos("n3", "out", "out_b", "vss", "vss", pdk.nfet, W=mk_n_w, L=mk_n_l))
    lines.append(pdk.mos("pfb", "out_b", "out", "vdd", "vdd", pdk.pfet, W=fb_p_w, L=fb_p_l))
    lines.append(pdk.mos("nfb", "out_b", "out", "vss", "vss", pdk.nfet, W=fb_n_w, L=fb_n_l))
    lines.append(".ends muller_c")
    lines.append("")

    # Main subcircuit
    lines.append(".subckt async_ctrl go adc_done xbar_rst adc_go latch_out done vdd vss")

    lines.extend(pdk.inv("inv_go1", "go_b", "go", "vdd", "vss"))
    lines.extend(pdk.inv("inv_go2", "go_buf", "go_b", "vdd", "vss"))

    # RESET PHASE
    lines.append("Xrst_dly go_buf rst_dly_raw vdd vss rst_delay")
    lines.extend(pdk.inv("inv_rd1", "rst_dly_b", "rst_dly_raw", "vdd", "vss"))
    lines.extend(pdk.inv("inv_rd2", "rst_delayed", "rst_dly_b", "vdd", "vss"))

    lines.extend(pdk.nand2("nand_rst", "rst_nand", "go_buf", "rst_dly_b", "vdd", "vss",
                            wn=sz["inv_p"][0], wp=sz["inv_p"][0]))
    lines.extend(pdk.inv("inv_rst", "xbar_rst", "rst_nand", "vdd", "vss"))

    # SETTLE PHASE
    lines.append("Xsettle_dly rst_delayed stl_dly_raw vdd vss settle_delay")
    lines.extend(pdk.inv("inv_sd1", "stl_dly_b", "stl_dly_raw", "vdd", "vss"))
    lines.extend(pdk.inv("inv_sd2", "settle_delayed", "stl_dly_b", "vdd", "vss"))

    # ADC PHASE
    lines.extend(pdk.inv("inv_ag1", "adc_go_b", "settle_delayed", "vdd", "vss"))
    lines.extend(pdk.inv("inv_ag2", "adc_go", "adc_go_b", "vdd", "vss"))

    # DONE
    lines.extend(pdk.inv("inv_ld1", "latch_b", "adc_done", "vdd", "vss"))
    lines.extend(pdk.inv("inv_ld2", "latch_out", "latch_b", "vdd", "vss"))
    lines.extend(pdk.inv("inv_dn1", "done_b", "latch_out", "vdd", "vss"))
    lines.extend(pdk.inv("inv_dn2", "done", "done_b", "vdd", "vss"))

    lines.append(".ends async_ctrl")
    return "\n".join(lines)


if __name__ == "__main__":
    print(generate())
