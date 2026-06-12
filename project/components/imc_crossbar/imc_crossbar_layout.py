"""Layout for IMC crossbar — 4x4 regular array, compact routing."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import spout

N_ROWS = 4
N_COLS = 4
N_BITS = 4
# Unit cap 50fF: ~25um^2 → 5um x 5um
CAP_W, CAP_L = 5000, 5000
# Integration cap 500fF: ~250um^2 → ~16um x 16um
CINT_W, CINT_L = 16000, 16000


def layout():
    pdk = spout.Pdk.sky130()
    c = spout.Component(pdk)

    # --- Devices ---
    # Reset inverter
    rst_inv_n = c.add_nmos(420, 150, nf=1)
    rst_inv_p = c.add_pmos(840, 150, nf=1)

    # Per-column: reset switch (CMOS TG) + integration cap
    rst_sw_n = []
    rst_sw_p = []
    int_caps = []
    for j in range(N_COLS):
        rst_sw_n.append(c.add_nmos(1260, 150, nf=2))
        rst_sw_p.append(c.add_pmos(7000, 150, nf=8))
        int_caps.append(c.add_capacitor(CINT_W, CINT_L))

    # Crosspoint caps: xpt[row][col][bit]
    # Per crosspoint: inv_n + inv_p + sw_n + sw_p + cap (per bit)
    xpt_inv_n = [[[None]*N_BITS for _ in range(N_COLS)] for _ in range(N_ROWS)]
    xpt_inv_p = [[[None]*N_BITS for _ in range(N_COLS)] for _ in range(N_ROWS)]
    xpt_sw_n = [[[None]*N_BITS for _ in range(N_COLS)] for _ in range(N_ROWS)]
    xpt_sw_p = [[[None]*N_BITS for _ in range(N_COLS)] for _ in range(N_ROWS)]
    xpt_cap = [[[None]*N_BITS for _ in range(N_COLS)] for _ in range(N_ROWS)]

    for i in range(N_ROWS):
        for j in range(N_COLS):
            for b in range(N_BITS):
                xpt_inv_n[i][j][b] = c.add_nmos(420, 150, nf=1)
                xpt_inv_p[i][j][b] = c.add_pmos(840, 150, nf=1)
                xpt_sw_n[i][j][b] = c.add_nmos(840, 150, nf=1)
                xpt_sw_p[i][j][b] = c.add_pmos(1680, 150, nf=2)
                w = CAP_W * (2 ** b)
                xpt_cap[i][j][b] = c.add_capacitor(w, CAP_L)

    # --- Nets ---
    vdd = c.named_net("VDD")
    vss = c.named_net("GND")
    net_rst = c.named_net("RST")
    row_nets = [c.named_net(f"X{i}") for i in range(N_ROWS)]
    col_nets = [c.named_net(f"Y{j}") for j in range(N_COLS)]
    wb_nets = [[[c.named_net(f"WB_{i}{j}{b}")
                 for b in range(N_BITS)]
                for j in range(N_COLS)]
               for i in range(N_ROWS)]

    # Reset inverter
    rst_b = c.connect([rst_inv_n.d, rst_inv_p.d])
    c.connect_to_net(net_rst, [rst_inv_n.g, rst_inv_p.g])
    c.connect_to_net(vss, [rst_inv_n.s, rst_inv_n.b])
    c.connect_to_net(vdd, [rst_inv_p.s, rst_inv_p.b])

    # Per-column: reset switch + integration cap
    for j in range(N_COLS):
        # Reset switch: TG between col and vss
        c.connect_to_net(col_nets[j], [rst_sw_n[j].d, rst_sw_p[j].d, int_caps[j].port(0)])
        c.connect_to_net(vss, [rst_sw_n[j].s, rst_sw_p[j].s, rst_sw_n[j].b, int_caps[j].port(1)])
        c.connect_to_net(vdd, [rst_sw_p[j].b])
        c.connect_to_net(net_rst, [rst_sw_n[j].g])
        c.connect_to_net(rst_b, [rst_sw_p[j].g])

    # Crosspoint wiring
    for i in range(N_ROWS):
        for j in range(N_COLS):
            for b in range(N_BITS):
                # Inverter for ctrl complement
                ctrl_b_net = c.connect([xpt_inv_n[i][j][b].d, xpt_inv_p[i][j][b].d,
                                        xpt_sw_p[i][j][b].g])
                c.connect_to_net(wb_nets[i][j][b], [xpt_inv_n[i][j][b].g,
                                                     xpt_inv_p[i][j][b].g,
                                                     xpt_sw_n[i][j][b].g])
                c.connect_to_net(vss, [xpt_inv_n[i][j][b].s, xpt_inv_n[i][j][b].b,
                                       xpt_sw_n[i][j][b].b])
                c.connect_to_net(vdd, [xpt_inv_p[i][j][b].s, xpt_inv_p[i][j][b].b,
                                       xpt_sw_p[i][j][b].b])

                # Switch: passes row input to cap bottom
                cap_bot = c.connect([xpt_sw_n[i][j][b].d, xpt_sw_p[i][j][b].d,
                                     xpt_cap[i][j][b].port(0)])
                c.connect_to_net(row_nets[i], [xpt_sw_n[i][j][b].s, xpt_sw_p[i][j][b].s])

                # Cap top plate → column (charge integration)
                c.connect_to_net(col_nets[j], [xpt_cap[i][j][b].port(1)])

    # --- Ports ---
    for i in range(N_ROWS):
        c.add_port(f"X{i}", row_nets[i], "input")
    for j in range(N_COLS):
        c.add_port(f"Y{j}", col_nets[j], "output")
    for i in range(N_ROWS):
        for j in range(N_COLS):
            for b in range(N_BITS):
                c.add_port(f"WB_{i}{j}{b}", wb_nets[i][j][b], "input")
    c.add_port("RST", net_rst, "input")
    c.add_port("VDD", vdd, "inout")
    c.add_port("GND", vss, "inout")

    # --- Manual Placement ---
    # Floorplan: 4 column groups, each with 4 rows of crosspoints stacked vertically.
    # Per crosspoint cell: cap on top, switches in middle, inverters at bottom.
    # Below entire array: reset switches + integration caps.
    #
    # Spacing (nm):
    #   - Between bits within a column: 3000 (routing channel)
    #   - Between column groups: 10000 (shielded Y wire channel)
    #   - Between row groups: 8000 (routing channel for X wires)
    #   - MOS height estimate: ~2000nm
    #   - Cap bit widths: 5000, 10000, 20000, 40000

    MOS_H = 4000       # MOS cell height with contact clearance
    CAP_H = CAP_L      # cap height = 5000
    BIT_GAP = 5000     # gap between bits within column (routing channel)
    COL_GAP = 15000    # gap between column groups (Y wire channel)
    ROW_GAP = 12000    # gap between row groups (X wire routing)
    SW_GAP = 4000      # gap between switch and cap / inverter rows

    # Compute X offset for each column group's bit 0
    # Within a column: bits laid out left-to-right with widths 5000, 10000, 20000, 40000
    bit_widths = [CAP_W * (2**b) for b in range(N_BITS)]
    # Total width of one column group = sum of bit widths + gaps between bits
    col_width = sum(bit_widths) + (N_BITS - 1) * BIT_GAP  # 5+10+20+40 + 3*3 = 84um

    col_x_origin = []  # X start of each column group
    x = 5000  # initial left margin
    for j in range(N_COLS):
        col_x_origin.append(x)
        x += col_width + COL_GAP

    # Per-column, per-bit X position (left edge of cap)
    def bit_x(col, bit):
        """X position of cap[col][bit]."""
        bx = col_x_origin[col]
        for b2 in range(bit):
            bx += bit_widths[b2] + BIT_GAP
        return bx

    # Row Y positions: row 0 at bottom of array, row 3 at top
    # Each row group height = CAP_H + SW_GAP + 2*MOS_H + SW_GAP + 2*MOS_H
    # (cap + gap + sw_n/sw_p + gap + inv_n/inv_p)
    row_cell_h = CAP_H + SW_GAP + 2 * MOS_H + SW_GAP + 2 * MOS_H
    row_y_origin = []  # Y of cap bottom edge for each row
    # Stack from bottom: reset section, then rows 0..3
    reset_section_h = 25000  # space for int_caps + reset switches
    y = reset_section_h
    for i in range(N_ROWS):
        row_y_origin.append(y)
        y += row_cell_h + ROW_GAP

    # Place crosspoint devices
    for i in range(N_ROWS):
        for j in range(N_COLS):
            for b in range(N_BITS):
                bx = bit_x(j, b)
                cap_y = row_y_origin[i] + row_cell_h - CAP_H  # cap at top of cell
                sw_y = cap_y - SW_GAP - MOS_H  # sw_p just below cap
                sw_n_y = sw_y - MOS_H           # sw_n below sw_p
                inv_p_y = sw_n_y - SW_GAP - MOS_H  # inv_p below switch pair
                inv_n_y = inv_p_y - MOS_H           # inv_n at bottom

                c.fix_position(xpt_cap[i][j][b], bx, cap_y)
                c.fix_position(xpt_sw_p[i][j][b], bx, sw_y)
                c.fix_position(xpt_sw_n[i][j][b], bx, sw_n_y)
                c.fix_position(xpt_inv_p[i][j][b], bx, inv_p_y)
                c.fix_position(xpt_inv_n[i][j][b], bx, inv_n_y)

    # Place reset section below the array
    rst_y = 3000  # base Y for reset section
    for j in range(N_COLS):
        # Integration cap at bottom
        int_x = col_x_origin[j] + (col_width - CINT_W) // 2  # centered in column
        c.fix_position(int_caps[j], int_x, rst_y)
        # Reset switches above int_caps
        sw_base_y = rst_y + CINT_L + 3000
        sw_x = col_x_origin[j] + col_width // 2  # centered
        c.fix_position(rst_sw_n[j], sw_x, sw_base_y)
        c.fix_position(rst_sw_p[j], sw_x, sw_base_y + MOS_H + 1000)

    # Reset inverter to the left
    c.fix_position(rst_inv_n, 1000, rst_y + CINT_L + 3000)
    c.fix_position(rst_inv_p, 1000, rst_y + CINT_L + 3000 + MOS_H + 1000)

    # --- Net Constraints (routing hints only) ---
    c.net_class(vdd, "power")
    c.net_class(vss, "ground")
    for j in range(N_COLS):
        c.net_class(col_nets[j], "analog")

    # --- Place & Route ---
    c.place()
    c.route()

    violations = c.check_drc()
    print(f"DRC: {len(violations)} violations")
    if violations:
        from collections import Counter
        by_layer = Counter(v.layer for v in violations)
        print(f"  By layer: {dict(by_layer)}")

    out_path = os.path.join(os.path.dirname(__file__), "imc_crossbar.gds")
    c.export_gds(out_path)
    print(f"Exported {out_path}")

    return c


if __name__ == "__main__":
    layout()
