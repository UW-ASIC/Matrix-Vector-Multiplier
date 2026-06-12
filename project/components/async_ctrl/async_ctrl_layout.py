"""Layout for async controller — signal-flow left-to-right, compact digital."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import spout

N_RST_DELAY = 10
N_SETTLE_DELAY = 20


def add_inv(c, wn=420, wp=840):
    """Add one CMOS inverter, return (nfet, pfet)."""
    n = c.add_nmos(wn, 150, nf=1)
    p = c.add_pmos(wp, 150, nf=1)
    return n, p


def add_nand2(c, wn=420, wp=840):
    """Add 2-input NAND. Returns (p1, p2, n1, n2)."""
    p1 = c.add_pmos(wp, 150, nf=1)
    p2 = c.add_pmos(wp, 150, nf=1)
    n1 = c.add_nmos(wn, 150, nf=1)
    n2 = c.add_nmos(wn, 150, nf=1)
    return p1, p2, n1, n2


def wire_inv(c, n, p, in_net, out_net, vdd, vss):
    """Wire an inverter."""
    c.connect_to_net(in_net, [n.g, p.g])
    c.connect_to_net(out_net, [n.d, p.d])
    c.connect_to_net(vss, [n.s, n.b])
    c.connect_to_net(vdd, [p.s, p.b])


def layout():
    pdk = spout.Pdk.sky130()
    c = spout.Component(pdk)

    # --- Nets ---
    vdd = c.named_net("VDD")
    vss = c.named_net("GND")
    net_go = c.named_net("GO")
    net_adc_done = c.named_net("ADC_DONE")
    net_xbar_rst = c.named_net("XBAR_RST")
    net_adc_go = c.named_net("ADC_GO")
    net_latch_out = c.named_net("LATCH_OUT")
    net_done = c.named_net("DONE")

    # --- Build all inverters ---
    # GO buffer
    inv_go1 = add_inv(c)
    inv_go2 = add_inv(c)

    # Reset delay chain (10 stages)
    rst_dly = []
    for _ in range(N_RST_DELAY):
        rst_dly.append(add_inv(c))

    # Post-delay buffers
    inv_rd1 = add_inv(c)
    inv_rd2 = add_inv(c)

    # NAND + inverter for xbar_rst
    nand_rst = add_nand2(c, wn=840, wp=840)
    inv_rst = add_inv(c)

    # Settle delay chain (20 stages)
    stl_dly = []
    for _ in range(N_SETTLE_DELAY):
        stl_dly.append(add_inv(c))

    # Post-settle buffers
    inv_sd1 = add_inv(c)
    inv_sd2 = add_inv(c)

    # ADC go buffers
    inv_ag1 = add_inv(c)
    inv_ag2 = add_inv(c)

    # Done path
    inv_ld1 = add_inv(c)
    inv_ld2 = add_inv(c)
    inv_dn1 = add_inv(c)
    inv_dn2 = add_inv(c)

    # --- Wiring ---
    # GO buffer chain
    net_go_b = c.connect([])
    wire_inv(c, *inv_go1, net_go, net_go_b, vdd, vss)
    net_go_buf = c.connect([])
    wire_inv(c, *inv_go2, net_go_b, net_go_buf, vdd, vss)

    # Reset delay chain
    prev_net = net_go_buf
    for i, (n, p) in enumerate(rst_dly):
        next_net = c.connect([])
        wire_inv(c, n, p, prev_net, next_net, vdd, vss)
        prev_net = next_net
    net_rst_dly_raw = prev_net

    # Post-delay buffers
    net_rst_dly_b = c.connect([])
    wire_inv(c, *inv_rd1, net_rst_dly_raw, net_rst_dly_b, vdd, vss)
    net_rst_delayed = c.connect([])
    wire_inv(c, *inv_rd2, net_rst_dly_b, net_rst_delayed, vdd, vss)

    # NAND: xbar_rst = go_buf AND rst_dly_b
    p1, p2, n1, n2 = nand_rst
    net_rst_nand = c.connect([p1.d, p2.d, n1.d])
    c.connect_to_net(net_go_buf, [p1.g, n1.g])
    c.connect_to_net(net_rst_dly_b, [p2.g, n2.g])
    c.connect_to_net(vdd, [p1.s, p1.b, p2.s, p2.b])
    nand_mid = c.connect([n1.s, n2.d])
    c.connect_to_net(vss, [n2.s, n1.b, n2.b])

    # Invert NAND output → xbar_rst
    wire_inv(c, *inv_rst, net_rst_nand, net_xbar_rst, vdd, vss)

    # Settle delay chain
    prev_net = net_rst_delayed
    for i, (n, p) in enumerate(stl_dly):
        next_net = c.connect([])
        wire_inv(c, n, p, prev_net, next_net, vdd, vss)
        prev_net = next_net
    net_stl_dly_raw = prev_net

    # Post-settle buffers
    net_stl_dly_b = c.connect([])
    wire_inv(c, *inv_sd1, net_stl_dly_raw, net_stl_dly_b, vdd, vss)
    net_settle_delayed = c.connect([])
    wire_inv(c, *inv_sd2, net_stl_dly_b, net_settle_delayed, vdd, vss)

    # ADC go
    net_adc_go_b = c.connect([])
    wire_inv(c, *inv_ag1, net_settle_delayed, net_adc_go_b, vdd, vss)
    wire_inv(c, *inv_ag2, net_adc_go_b, net_adc_go, vdd, vss)

    # Done path
    net_latch_b = c.connect([])
    wire_inv(c, *inv_ld1, net_adc_done, net_latch_b, vdd, vss)
    wire_inv(c, *inv_ld2, net_latch_b, net_latch_out, vdd, vss)
    net_done_b = c.connect([])
    wire_inv(c, *inv_dn1, net_latch_out, net_done_b, vdd, vss)
    wire_inv(c, *inv_dn2, net_done_b, net_done, vdd, vss)

    # --- Ports ---
    c.add_port("GO", net_go, "input")
    c.add_port("ADC_DONE", net_adc_done, "input")
    c.add_port("XBAR_RST", net_xbar_rst, "output")
    c.add_port("ADC_GO", net_adc_go, "output")
    c.add_port("LATCH_OUT", net_latch_out, "output")
    c.add_port("DONE", net_done, "output")
    c.add_port("VDD", vdd, "inout")
    c.add_port("GND", vss, "inout")

    # --- Constraints ---
    # Collect all NFET/PFET for row alignment
    all_inv_n = [inv_go1[0], inv_go2[0]]
    all_inv_p = [inv_go1[1], inv_go2[1]]
    rst_dly_n = [pair[0] for pair in rst_dly]
    rst_dly_p = [pair[1] for pair in rst_dly]
    stl_dly_n = [pair[0] for pair in stl_dly]
    stl_dly_p = [pair[1] for pair in stl_dly]

    # Signal flow: left-to-right ordering with min_spacing to avoid DRC
    PITCH = 840  # nm between adjacent inverter stages

    # Main chain: go_buf → rst_dly → rd_buf → stl_dly → sd_buf → ag_buf
    c.left_of(inv_go1[0], inv_go2[0])
    c.min_spacing(inv_go1[0], inv_go2[0], PITCH)
    c.left_of(inv_go2[0], rst_dly[0][0])
    c.min_spacing(inv_go2[0], rst_dly[0][0], PITCH)
    for i in range(N_RST_DELAY - 1):
        c.left_of(rst_dly[i][0], rst_dly[i + 1][0])
        c.min_spacing(rst_dly[i][0], rst_dly[i + 1][0], PITCH)
    c.left_of(rst_dly[-1][0], inv_rd1[0])
    c.min_spacing(rst_dly[-1][0], inv_rd1[0], PITCH)
    c.left_of(inv_rd1[0], inv_rd2[0])
    c.min_spacing(inv_rd1[0], inv_rd2[0], PITCH)
    c.left_of(inv_rd2[0], stl_dly[0][0])
    c.min_spacing(inv_rd2[0], stl_dly[0][0], PITCH)
    for i in range(N_SETTLE_DELAY - 1):
        c.left_of(stl_dly[i][0], stl_dly[i + 1][0])
        c.min_spacing(stl_dly[i][0], stl_dly[i + 1][0], PITCH)
    c.left_of(stl_dly[-1][0], inv_sd1[0])
    c.min_spacing(stl_dly[-1][0], inv_sd1[0], PITCH)
    c.left_of(inv_sd1[0], inv_sd2[0])
    c.min_spacing(inv_sd1[0], inv_sd2[0], PITCH)
    c.left_of(inv_sd2[0], inv_ag1[0])
    c.min_spacing(inv_sd2[0], inv_ag1[0], PITCH)
    c.left_of(inv_ag1[0], inv_ag2[0])
    c.min_spacing(inv_ag1[0], inv_ag2[0], PITCH)

    # Align delay chains in rows
    c.align_row(rst_dly_n)
    c.align_row(rst_dly_p)
    c.align_row(stl_dly_n)
    c.align_row(stl_dly_p)

    # PMOS above NMOS for all inverters
    for n, p in rst_dly:
        c.above(p, n)
    for n, p in stl_dly:
        c.above(p, n)
    c.above(inv_go1[1], inv_go1[0])
    c.above(inv_go2[1], inv_go2[0])
    c.above(inv_rd1[1], inv_rd1[0])
    c.above(inv_rd2[1], inv_rd2[0])
    c.above(inv_sd1[1], inv_sd1[0])
    c.above(inv_sd2[1], inv_sd2[0])
    c.above(inv_ag1[1], inv_ag1[0])
    c.above(inv_ag2[1], inv_ag2[0])
    c.above(inv_ld1[1], inv_ld1[0])
    c.above(inv_ld2[1], inv_ld2[0])
    c.above(inv_dn1[1], inv_dn1[0])
    c.above(inv_dn2[1], inv_dn2[0])

    # NAND gate: place between rd2 and stl_dly[0], below main chain
    c.above(nand_rst[0], nand_rst[2])  # p1 above n1
    c.above(nand_rst[1], nand_rst[3])  # p2 above n2
    c.left_of(nand_rst[2], nand_rst[3])  # n1 left of n2
    c.left_of(nand_rst[0], nand_rst[1])  # p1 left of p2
    c.min_spacing(nand_rst[2], nand_rst[3], PITCH)
    c.left_of(nand_rst[3], inv_rst[0])
    c.min_spacing(nand_rst[3], inv_rst[0], PITCH)
    c.below(nand_rst[2], inv_rd2[0])
    c.min_spacing(nand_rst[2], inv_rd2[0], 1200)

    # Done chain below main signal path
    c.below(inv_ld1[0], stl_dly[0][0])
    c.min_spacing(inv_ld1[0], stl_dly[0][0], 1200)
    c.left_of(inv_ld1[0], inv_ld2[0])
    c.min_spacing(inv_ld1[0], inv_ld2[0], PITCH)
    c.left_of(inv_ld2[0], inv_dn1[0])
    c.min_spacing(inv_ld2[0], inv_dn1[0], PITCH)
    c.left_of(inv_dn1[0], inv_dn2[0])
    c.min_spacing(inv_dn1[0], inv_dn2[0], PITCH)
    c.align_row([inv_ld1[0], inv_ld2[0], inv_dn1[0], inv_dn2[0]])

    # Power
    c.net_class(vdd, "power")
    c.net_class(vss, "ground")

    # --- Layout ---
    c.place()
    c.route()

    violations = c.check_drc()
    print(f"DRC: {len(violations)} violations")
    for v in violations[:20]:
        print(f"  {v.rule} layer={v.layer}")

    if not violations:
        c.export_gds("async_ctrl.gds")
        print("Exported async_ctrl.gds")

    return c


if __name__ == "__main__":
    layout()
