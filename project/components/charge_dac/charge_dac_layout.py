"""Layout for charge DAC — common-centroid caps, compact switches."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import spout

N_BITS = 4
CAP_W, CAP_L = 5000, 5000  # unit cap in nm


def layout():
    pdk = spout.Pdk.sky130()
    c = spout.Component(pdk)

    # --- Devices ---
    inv_n = []
    inv_p = []
    sw_n = []
    sw_p = []
    caps = []

    for i in range(N_BITS):
        inv_n.append(c.add_nmos(420, 150, nf=1))
        inv_p.append(c.add_pmos(840, 150, nf=1))
        sw_n.append(c.add_nmos(840, 150, nf=1))
        sw_p.append(c.add_pmos(1680, 150, nf=2))
        w = CAP_W * (2 ** i)
        caps.append(c.add_capacitor(w, CAP_L))

    # --- Nets ---
    vdd = c.named_net("VDD")
    vss = c.named_net("GND")
    net_vref = c.named_net("VREF")
    net_out = c.named_net("OUT")
    bit_nets = [c.named_net(f"B{i}") for i in range(N_BITS)]

    for i in range(N_BITS):
        ctrl_b = c.connect([inv_n[i].d, inv_p[i].d, sw_p[i].g])
        c.connect_to_net(bit_nets[i], [inv_n[i].g, inv_p[i].g, sw_n[i].g])
        c.connect_to_net(vss, [inv_n[i].s, inv_n[i].b])
        c.connect_to_net(vdd, [inv_p[i].s, inv_p[i].b])

        cap_bot = c.connect([sw_n[i].d, sw_p[i].d, caps[i].port(0)])
        c.connect_to_net(net_vref, [sw_n[i].s, sw_p[i].s])
        c.connect_to_net(vss, [sw_n[i].b])
        c.connect_to_net(vdd, [sw_p[i].b])

        c.connect_to_net(net_out, [caps[i].port(1)])

    # --- Ports ---
    c.add_port("VREF", net_vref, "input")
    for i in range(N_BITS):
        c.add_port(f"B{i}", bit_nets[i], "input")
    c.add_port("OUT", net_out, "output")
    c.add_port("VDD", vdd, "inout")
    c.add_port("GND", vss, "inout")

    # --- Constraints ---
    c.net_class(vdd, "power")
    c.net_class(vss, "ground")

    # Inverter rows — generous spacing
    c.align_row(inv_n)
    c.align_row(inv_p)
    for i in range(N_BITS):
        c.above(inv_p[i], inv_n[i])
    for i in range(N_BITS - 1):
        c.min_spacing(inv_n[i], inv_n[i + 1], 10000)

    # Switch rows above inverters
    c.align_row(sw_n)
    c.align_row(sw_p)
    for i in range(N_BITS):
        c.above(sw_p[i], sw_n[i])
        c.above(sw_n[i], inv_p[i])
    for i in range(N_BITS - 1):
        c.min_spacing(sw_n[i], sw_n[i + 1], 10000)

    # Caps: row above switches with BIG spacing between them
    c.align_row(caps)
    for i in range(N_BITS):
        c.above(caps[i], sw_p[i])
    for i in range(N_BITS - 1):
        c.min_spacing(caps[i], caps[i + 1], 5000)

    # Vertical separation
    for i in range(N_BITS):
        c.min_spacing(sw_p[i], caps[i], 8000)

    # --- Layout ---
    c.place()
    c.route()

    # --- Verify ---
    violations = c.check_drc()
    print(f"DRC: {len(violations)} violations")
    for v in violations[:30]:
        print(f"  {v.rule} layer={v.layer}: {v.message}")

    if not violations:
        c.export_gds("charge_dac.gds")
        print("Exported charge_dac.gds")
    else:
        c.export_gds("charge_dac_debug.gds")
        print("Exported charge_dac_debug.gds (with violations)")

    return c


if __name__ == "__main__":
    layout()
