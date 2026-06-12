"""Layout for strongarm comparator — compact symmetric with minimal PEX."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import spout


def layout():
    pdk = spout.Pdk.sky130()
    c = spout.Component(pdk)

    # --- Devices (W in nm, L in nm) ---
    # Tail current source
    tail = c.add_nmos(420, 150, nf=1)
    # Input differential pair (8 fingers for matching)
    inp = c.add_nmos(7000, 150, nf=8)
    inn = c.add_nmos(7000, 150, nf=8)
    # Cross-coupled NMOS latch
    xnp = c.add_nmos(1000, 150, nf=2)
    xnn = c.add_nmos(1000, 150, nf=2)
    # Cross-coupled PMOS latch
    xpp = c.add_pmos(4500, 150, nf=6)
    xpn = c.add_pmos(4500, 150, nf=6)
    # Reset PMOS switches
    rstp = c.add_pmos(1000, 150, nf=2)
    rstn = c.add_pmos(1000, 150, nf=2)

    # --- Nets ---
    vdd = c.named_net("VDD")
    vss = c.named_net("GND")
    net_clk = c.named_net("CLK")
    net_vinp = c.named_net("VINP")
    net_vinn = c.named_net("VINN")

    # Internal nets
    net_tail = c.connect([tail.d, inp.s, inn.s])
    net_drn_p = c.connect([inp.d, xnp.s])
    net_drn_n = c.connect([inn.d, xnn.s])
    net_outp = c.connect([xnp.d, xpp.d, rstp.d])
    net_outn = c.connect([xnn.d, xpn.d, rstn.d])

    # Cross-coupling: xnp.g=outn, xnn.g=outp, xpp.g=outn, xpn.g=outp
    c.connect_to_net(net_outn, [xnp.g, xpp.g])
    c.connect_to_net(net_outp, [xnn.g, xpn.g])

    # Power
    c.connect_to_net(vdd, [xpp.s, xpp.b, xpn.s, xpn.b, rstp.s, rstp.b, rstn.s, rstn.b])
    c.connect_to_net(vss, [tail.s, tail.b, inp.b, inn.b, xnp.b, xnn.b])

    # Clock
    c.connect_to_net(net_clk, [tail.g, rstp.g, rstn.g])

    # Inputs
    c.connect_to_net(net_vinp, [inp.g])
    c.connect_to_net(net_vinn, [inn.g])

    # --- Ports ---
    c.add_port("VINP", net_vinp, "input")
    c.add_port("VINN", net_vinn, "input")
    c.add_port("OUTP", net_outp, "output")
    c.add_port("OUTN", net_outn, "output")
    c.add_port("CLK", net_clk, "input")
    c.add_port("VDD", vdd, "inout")
    c.add_port("GND", vss, "inout")

    # --- Constraints ---
    # Symmetry (critical for offset)
    c.symmetric(inp, inn)
    c.symmetric(xnp, xnn)
    c.symmetric(xpp, xpn)
    c.symmetric(rstp, rstn)
    c.self_symmetric(tail)

    # Matching
    c.match_devices(inp, inn)
    c.match_devices(xnp, xnn)
    c.match_devices(xpp, xpn)
    c.match_devices(rstp, rstn)

    # Vertical stacking — PMOS above NMOS
    c.above(xpp, inp)
    c.above(xpn, inn)
    c.above(inp, tail)

    # Power/ground routing class (wider wires, more spacing)
    c.net_class(vdd, "power")
    c.net_class(vss, "ground")

    # --- Layout ---
    c.place()
    c.route()

    # --- Verify ---
    violations = c.check_drc()
    print(f"DRC: {len(violations)} violations")
    for v in violations:
        print(f"  {v.rule} layer={v.layer} loc={v.location}: {v.message}")

    if not violations:
        c.export_gds("project/strongarm.gds")
        print("Exported strongarm.gds")

    return c


if __name__ == "__main__":
    layout()
