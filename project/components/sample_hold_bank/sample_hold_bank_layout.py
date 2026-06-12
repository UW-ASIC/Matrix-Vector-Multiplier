"""Layout for sample-and-hold bank — 4 matched channels, compact."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import spout

N_CHANNELS = 4
# 200fF hold cap: sky130 MIM ~2fF/um^2 → 100um^2 → 10um x 10um
CAP_W, CAP_L = 10000, 10000


def layout():
    pdk = spout.Pdk.sky130()
    c = spout.Component(pdk)

    # --- Devices ---
    # Control inverter
    inv_n = c.add_nmos(420, 150, nf=1)
    inv_p = c.add_pmos(840, 150, nf=1)

    # Per-channel: CMOS switch (NFET+PFET) + hold cap
    ch_sw_n = []
    ch_sw_p = []
    ch_cap = []
    for _ in range(N_CHANNELS):
        ch_sw_n.append(c.add_nmos(840, 150, nf=1))
        ch_sw_p.append(c.add_pmos(1680, 150, nf=2))
        ch_cap.append(c.add_capacitor(CAP_W, CAP_L))

    # --- Nets ---
    vdd = c.named_net("VDD")
    vss = c.named_net("GND")
    net_ctrl = c.named_net("SH_CTRL")

    in_nets = [c.named_net(f"IN{i}") for i in range(N_CHANNELS)]
    out_nets = [c.named_net(f"OUT{i}") for i in range(N_CHANNELS)]

    # Control inverter wiring
    ctrl_b = c.connect([inv_n.d, inv_p.d])
    c.connect_to_net(net_ctrl, [inv_n.g, inv_p.g])
    c.connect_to_net(vss, [inv_n.s, inv_n.b])
    c.connect_to_net(vdd, [inv_p.s, inv_p.b])

    # Per-channel wiring
    for i in range(N_CHANNELS):
        # Switch NFET: D=in, G=ctrl, S=out, B=vss
        c.connect_to_net(in_nets[i], [ch_sw_n[i].d, ch_sw_p[i].d])
        c.connect_to_net(net_ctrl, [ch_sw_n[i].g])
        c.connect_to_net(ctrl_b, [ch_sw_p[i].g])
        # Output node = switch source + cap top
        c.connect_to_net(out_nets[i], [ch_sw_n[i].s, ch_sw_p[i].s, ch_cap[i].port(0)])
        c.connect_to_net(vss, [ch_sw_n[i].b, ch_cap[i].port(1)])
        c.connect_to_net(vdd, [ch_sw_p[i].b])

    # --- Ports ---
    for i in range(N_CHANNELS):
        c.add_port(f"IN{i}", in_nets[i], "input")
    for i in range(N_CHANNELS):
        c.add_port(f"OUT{i}", out_nets[i], "output")
    c.add_port("SH_CTRL", net_ctrl, "input")
    c.add_port("VDD", vdd, "inout")
    c.add_port("GND", vss, "inout")

    # --- Constraints ---
    # All switch NFETs in row (compact, matched)
    c.align_row(ch_sw_n)
    c.align_row(ch_sw_p)

    # PFET above NFET per switch
    for i in range(N_CHANNELS):
        c.above(ch_sw_p[i], ch_sw_n[i])

    # Caps aligned below switches (short route to output node)
    c.align_row(ch_cap)
    for i in range(N_CHANNELS):
        c.below(ch_cap[i], ch_sw_n[i])

    # Control inverter left of switches
    c.above(inv_p, inv_n)
    c.left_of(inv_n, ch_sw_n[0])
    c.left_of(inv_p, ch_sw_p[0])

    # Symmetric pairs for matching (ch0↔ch3, ch1↔ch2)
    c.symmetric(ch_sw_n[0], ch_sw_n[3])
    c.symmetric(ch_sw_n[1], ch_sw_n[2])
    c.symmetric(ch_sw_p[0], ch_sw_p[3])
    c.symmetric(ch_sw_p[1], ch_sw_p[2])
    c.symmetric(ch_cap[0], ch_cap[3])
    c.symmetric(ch_cap[1], ch_cap[2])

    # Match all channel devices
    for i in range(N_CHANNELS - 1):
        c.match_devices(ch_sw_n[i], ch_sw_n[i + 1])
        c.match_devices(ch_sw_p[i], ch_sw_p[i + 1])

    # Power
    c.net_class(vdd, "power")
    c.net_class(vss, "ground")

    # Output nets: analog class (wider spacing)
    for net in out_nets:
        c.net_class(net, "analog")
    # Input nets also analog
    for net in in_nets:
        c.net_class(net, "analog")

    # Horizontal spacing: 10um caps + analog routing channels
    for i in range(N_CHANNELS - 1):
        c.min_spacing(ch_cap[i], ch_cap[i + 1], 12000)
        c.min_spacing(ch_sw_n[i], ch_sw_n[i + 1], 8000)
        c.min_spacing(ch_sw_p[i], ch_sw_p[i + 1], 8000)

    # Vertical gap: routing channels between rows
    for i in range(N_CHANNELS):
        c.min_spacing(ch_sw_n[i], ch_cap[i], 6000)
        c.min_spacing(ch_sw_p[i], ch_sw_n[i], 4000)

    # Inverter clearance from switch array
    c.min_spacing(inv_n, ch_sw_n[0], 8000)
    c.min_spacing(inv_p, ch_sw_p[0], 8000)

    # Guard rings: NMOS in substrate ring, PMOS in nwell ring
    c.guard_ring([inv_n] + ch_sw_n, "substrate")
    c.guard_ring([inv_p] + ch_sw_p, "nwell")

    # Clock net class
    c.net_class(net_ctrl, "clock")

    # --- Layout ---
    c.place()
    c.route()

    # --- Verify ---
    violations = c.check_drc()
    print(f"DRC: {len(violations)} violations")
    for v in violations[:20]:
        print(f"  {v.rule} layer={v.layer}: {v.message}")

    if not violations:
        c.export_gds("sample_hold_bank.gds")
        print("Exported sample_hold_bank.gds")

    return c, violations


if __name__ == "__main__":
    layout()
