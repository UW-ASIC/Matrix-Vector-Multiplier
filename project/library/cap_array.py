"""Parameterized Binary-Weighted Capacitor Bank.

Generates .subckt cap_array — N binary-weighted capacitors with per-bit
CMOS switch control and inverters for complementary enable.
"""

from library.cmos_switch import cmos_switch_spice
from library.pdks import get_pdk

_pdk = get_pdk()


def cap_array_spice(name, n_bits, c_unit,
                    w_n=None, l_n=None, w_p=None, l_p=None):
    """Return SPICE string for a binary-weighted cap array with per-bit switches."""
    w_n = w_n or _pdk.sizing["inv_n"][0]
    l_n = l_n or _pdk.sizing["inv_n"][1]
    w_p = w_p or _pdk.sizing["inv_p"][0]
    l_p = l_p or _pdk.sizing["inv_p"][1]

    sw_name = f"{name}_sw"
    input_ports = " ".join(f"in{i}" for i in range(n_bits))
    lines = [cmos_switch_spice(sw_name, w_n, l_n, w_p, l_p), ""]
    lines.append(f".subckt {name} {input_ports} top_plate bottom_plate vdd vss")

    for i in range(n_bits):
        cap_val = c_unit * (2 ** i)
        lines.append(_pdk.mos(f"inv_n{i}", f"ctrl_b_{i}", f"in{i}", "vss", "vss",
                              _pdk.nfet, W=f"{w_n}", L=f"{l_n}"))
        lines.append(_pdk.mos(f"inv_p{i}", f"ctrl_b_{i}", f"in{i}", "vdd", "vdd",
                              _pdk.pfet, W=f"{w_p}", L=f"{l_p}"))
        lines.append(f"Xsw{i} bottom_plate cap_bot_{i} in{i} ctrl_b_{i} vdd vss {sw_name}")
        lines.append(f"Cb{i} top_plate cap_bot_{i} {cap_val}")
        lines.append(f"Rbias{i} cap_bot_{i} vss 100G")

    lines.append(f".ends {name}")
    return "\n".join(lines)


if __name__ == "__main__":
    print(cap_array_spice("cap_array_4bit", n_bits=4, c_unit=_pdk.caps["c_unit"]))
