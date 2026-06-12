"""CMOS Transmission Gate Switch.

Generates .subckt cmos_switch — a complementary pass gate with NMOS + PMOS.
"""

from library.pdks import get_pdk

_pdk = get_pdk()


def cmos_switch_spice(name, w_n=None, l_n=None, w_p=None, l_p=None):
    """Return SPICE string for a CMOS transmission gate subcircuit.

    Defaults to the active PDK's minimum inverter sizing if not specified.
    """
    w_n = w_n or _pdk.sizing["inv_n"][0]
    l_n = l_n or _pdk.sizing["inv_n"][1]
    w_p = w_p or _pdk.sizing["inv_p"][0]
    l_p = l_p or _pdk.sizing["inv_p"][1]
    return f""".subckt {name} in_ out ctrl ctrl_b vdd vss
X{name}_n in_ ctrl out vss {_pdk.nfet} W={w_n} L={l_n}
X{name}_p in_ ctrl_b out vdd {_pdk.pfet} W={w_p} L={l_p}
.ends {name}"""


if __name__ == "__main__":
    print(cmos_switch_spice("cmos_switch"))
