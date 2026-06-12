"""Layout for interleaved ADC — 2 symmetric SAR units, matched CDACs."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import spout

N_BITS = 4
CAP_W, CAP_L = 5000, 5000  # unit cap 50fF


def build_comparator(c, prefix_unused):
    """Add one StrongARM comparator. Returns dict of device refs."""
    d = {}
    d['tail'] = c.add_nmos(420, 150, nf=1)
    d['inp'] = c.add_nmos(7000, 150, nf=8)
    d['inn'] = c.add_nmos(7000, 150, nf=8)
    d['xnp'] = c.add_nmos(1000, 150, nf=2)
    d['xnn'] = c.add_nmos(1000, 150, nf=2)
    d['xpp'] = c.add_pmos(4500, 150, nf=6)
    d['xpn'] = c.add_pmos(4500, 150, nf=6)
    d['rstp'] = c.add_pmos(1000, 150, nf=2)
    d['rstn'] = c.add_pmos(1000, 150, nf=2)
    return d


def build_cdac(c):
    """Add one 4-bit CDAC. Returns (inv_n[], inv_p[], sw_n[], sw_p[], caps[])."""
    inv_n, inv_p, sw_n, sw_p, caps = [], [], [], [], []
    for b in range(N_BITS):
        inv_n.append(c.add_nmos(420, 150, nf=1))
        inv_p.append(c.add_pmos(840, 150, nf=1))
        sw_n.append(c.add_nmos(420, 150, nf=1))
        sw_p.append(c.add_pmos(1420, 150, nf=2))
        caps.append(c.add_capacitor(CAP_W * (2 ** b), CAP_L))
    return inv_n, inv_p, sw_n, sw_p, caps


def layout():
    pdk = spout.Pdk.sky130()
    c = spout.Component(pdk)

    # --- Build 2 ADC units ---
    units = []
    for _ in range(2):
        comp = build_comparator(c, None)
        cdac = build_cdac(c)
        units.append((comp, cdac))

    # --- Nets ---
    vdd = c.named_net("VDD")
    vss = c.named_net("GND")
    net_vref = c.named_net("VREF")
    net_adc_go = c.named_net("ADC_GO")
    col_nets = [c.named_net(f"COL{i}") for i in range(4)]

    # Digital output nets
    dout_nets = [[c.named_net(f"D{col}B{b}") for b in range(N_BITS)] for col in range(4)]

    # --- Wire each unit ---
    unit_outp_nets = []
    unit_outn_nets = []

    for u_idx, (comp, (cdac_inv_n, cdac_inv_p, cdac_sw_n, cdac_sw_p, cdac_caps)) in enumerate(units):
        # Comparator internal wiring
        net_tail = c.connect([comp['tail'].d, comp['inp'].s, comp['inn'].s])
        net_drn_p = c.connect([comp['inp'].d, comp['xnp'].s])
        net_drn_n = c.connect([comp['inn'].d, comp['xnn'].s])
        net_outp = c.connect([comp['xnp'].d, comp['xpp'].d, comp['rstp'].d])
        net_outn = c.connect([comp['xnn'].d, comp['xpn'].d, comp['rstn'].d])
        unit_outp_nets.append(net_outp)
        unit_outn_nets.append(net_outn)

        # Cross-coupling
        c.connect_to_net(net_outn, [comp['xnp'].g, comp['xpp'].g])
        c.connect_to_net(net_outp, [comp['xnn'].g, comp['xpn'].g])

        # Power
        c.connect_to_net(vdd, [comp['xpp'].s, comp['xpp'].b, comp['xpn'].s, comp['xpn'].b,
                                comp['rstp'].s, comp['rstp'].b, comp['rstn'].s, comp['rstn'].b])
        c.connect_to_net(vss, [comp['tail'].s, comp['tail'].b, comp['inp'].b, comp['inn'].b,
                                comp['xnp'].b, comp['xnn'].b])

        # Clock/go
        c.connect_to_net(net_adc_go, [comp['tail'].g, comp['rstp'].g, comp['rstn'].g])

        # Comparator inp connects to column (first col this unit handles)
        col_a = u_idx * 2
        c.connect_to_net(col_nets[col_a], [comp['inp'].g])

        # Comparator inn connects to CDAC top plate
        cdac_top = c.connect([comp['inn'].g])

        # CDAC wiring
        for b in range(N_BITS):
            # Inverter
            ctrl_b = c.connect([cdac_inv_n[b].d, cdac_inv_p[b].d, cdac_sw_p[b].g])
            sw_ctrl = c.named_net(f"U{u_idx}_SW{b}")
            c.connect_to_net(sw_ctrl, [cdac_inv_n[b].g, cdac_inv_p[b].g, cdac_sw_n[b].g])
            c.connect_to_net(vss, [cdac_inv_n[b].s, cdac_inv_n[b].b, cdac_sw_n[b].b])
            c.connect_to_net(vdd, [cdac_inv_p[b].s, cdac_inv_p[b].b, cdac_sw_p[b].b])

            # Switch
            c.connect([cdac_sw_n[b].d, cdac_sw_p[b].d, cdac_caps[b].port(0)])
            c.connect_to_net(net_vref, [cdac_sw_n[b].s, cdac_sw_p[b].s])

            # Cap top → CDAC top plate
            c.connect_to_net(cdac_top, [cdac_caps[b].port(1)])

    # --- Ports ---
    for i in range(4):
        c.add_port(f"COL{i}", col_nets[i], "input")
    c.add_port("VREF", net_vref, "input")
    for col in range(4):
        for b in range(N_BITS):
            c.add_port(f"D{col}B{b}", dout_nets[col][b], "output")
    c.add_port("ADC_GO", net_adc_go, "input")
    c.add_port("VDD", vdd, "inout")
    c.add_port("GND", vss, "inout")

    # --- Constraints ---
    u0_comp, (u0_inv_n, u0_inv_p, u0_sw_n, u0_sw_p, u0_caps) = units[0]
    u1_comp, (u1_inv_n, u1_inv_p, u1_sw_n, u1_sw_p, u1_caps) = units[1]

    # Inter-unit symmetry (unit0 ↔ unit1)
    c.symmetric(u0_comp['inp'], u1_comp['inp'])
    c.symmetric(u0_comp['inn'], u1_comp['inn'])
    c.symmetric(u0_comp['tail'], u1_comp['tail'])
    c.symmetric(u0_comp['xnp'], u1_comp['xnp'])
    c.symmetric(u0_comp['xnn'], u1_comp['xnn'])
    c.symmetric(u0_comp['xpp'], u1_comp['xpp'])
    c.symmetric(u0_comp['xpn'], u1_comp['xpn'])
    c.symmetric(u0_comp['rstp'], u1_comp['rstp'])
    c.symmetric(u0_comp['rstn'], u1_comp['rstn'])

    # Intra-unit comparator symmetry
    for comp, _ in units:
        c.symmetric(comp['inp'], comp['inn'])
        c.symmetric(comp['xnp'], comp['xnn'])
        c.symmetric(comp['xpp'], comp['xpn'])
        c.symmetric(comp['rstp'], comp['rstn'])
        c.self_symmetric(comp['tail'])
        c.match_devices(comp['inp'], comp['inn'])
        c.match_devices(comp['xnp'], comp['xnn'])
        c.match_devices(comp['xpp'], comp['xpn'])

        # Vertical stacking per comparator
        c.above(comp['rstp'], comp['xpp'])
        c.above(comp['xpp'], comp['xnp'])
        c.above(comp['xnp'], comp['inp'])
        c.above(comp['inp'], comp['tail'])

    # CDAC common centroid per unit
    c.common_centroid(u0_caps)
    c.common_centroid(u1_caps)

    # CDACs below comparators
    for (comp, (inv_n, inv_p, sw_n, sw_p, caps)) in units:
        c.below(caps[0], comp['tail'])
        c.align_row(caps)
        c.align_row(sw_n)
        for b in range(N_BITS):
            c.above(inv_p[b], inv_n[b])
            c.above(sw_n[b], inv_p[b])
            c.above(caps[b], sw_p[b])
            c.above(sw_p[b], sw_n[b])

    # Spacing — give router room (layer3 spacing = 1900 internal = 190nm)
    for comp, _ in units:
        c.min_spacing(comp['inp'], comp['tail'], 2000)
        c.min_spacing(comp['xnp'], comp['inp'], 2000)
        c.min_spacing(comp['xpp'], comp['xnp'], 2000)
        c.min_spacing(comp['rstp'], comp['xpp'], 2000)

    # Inter-unit spacing
    c.min_spacing(u0_comp['inp'], u1_comp['inp'], 5000)

    # CDAC cap spacing (big devices)
    for _, (inv_n, inv_p, sw_n, sw_p, caps) in units:
        for b in range(N_BITS - 1):
            c.min_spacing(caps[b], caps[b + 1], 2000)

    # Power
    c.net_class(vdd, "power")
    c.net_class(vss, "ground")
    c.net_class(net_adc_go, "clock")

    # --- Layout ---
    c.place()
    c.route()

    # --- Verify ---
    violations = c.check_drc()
    print(f"DRC: {len(violations)} violations")
    for v in violations[:20]:
        print(f"  {v.rule} layer={v.layer}: {v.message}")

    if not violations:
        c.export_gds("interleaved_adc.gds")
        print("Exported interleaved_adc.gds")

    return c


if __name__ == "__main__":
    layout()
