module tt_if (i_clk,
    i_ena,
    i_rst_n,
    ui_in,
    uio_in,
    uio_oe,
    uio_out,
    uo_out);
 input i_clk;
 input i_ena;
 input i_rst_n;
 input [7:0] ui_in;
 input [7:0] uio_in;
 output [7:0] uio_oe;
 output [7:0] uio_out;
 output [7:0] uo_out;

 wire _00_;
 wire _01_;
 wire _02_;
 wire _03_;
 wire _04_;
 wire _05_;
 wire _06_;
 wire _07_;

 sky130_fd_sc_hd__nand2_2 _08_ (.A(uo_out[0]),
    .B(i_ena),
    .Y(_04_));
 sky130_fd_sc_hd__xnor2_2 _09_ (.A(uo_out[1]),
    .B(_04_),
    .Y(_00_));
 sky130_fd_sc_hd__and4_2 _10_ (.A(uo_out[0]),
    .B(uo_out[1]),
    .C(uo_out[2]),
    .D(i_ena),
    .X(_05_));
 sky130_fd_sc_hd__a31o_2 _11_ (.A1(uo_out[0]),
    .A2(uo_out[1]),
    .A3(i_ena),
    .B1(uo_out[2]),
    .X(_06_));
 sky130_fd_sc_hd__and2b_2 _12_ (.A_N(_05_),
    .B(_06_),
    .X(_01_));
 sky130_fd_sc_hd__xor2_2 _13_ (.A(uo_out[3]),
    .B(_05_),
    .X(_02_));
 sky130_fd_sc_hd__or2_2 _14_ (.A(uo_out[0]),
    .B(i_ena),
    .X(_07_));
 sky130_fd_sc_hd__and2_2 _15_ (.A(_04_),
    .B(_07_),
    .X(_03_));
 sky130_fd_sc_hd__dfrtp_2 _16_ (.CLK(i_clk),
    .D(_00_),
    .RESET_B(i_rst_n),
    .Q(uo_out[1]));
 sky130_fd_sc_hd__dfrtp_2 _17_ (.CLK(i_clk),
    .D(_01_),
    .RESET_B(i_rst_n),
    .Q(uo_out[2]));
 sky130_fd_sc_hd__dfrtp_2 _18_ (.CLK(i_clk),
    .D(_02_),
    .RESET_B(i_rst_n),
    .Q(uo_out[3]));
 sky130_fd_sc_hd__dfrtp_2 _19_ (.CLK(i_clk),
    .D(_03_),
    .RESET_B(i_rst_n),
    .Q(uo_out[0]));
 sky130_fd_sc_hd__conb_1 _20_ (.LO(uio_oe[0]));
 sky130_fd_sc_hd__conb_1 _21_ (.LO(uio_oe[1]));
 sky130_fd_sc_hd__conb_1 _22_ (.LO(uio_oe[2]));
 sky130_fd_sc_hd__conb_1 _23_ (.LO(uio_oe[3]));
 sky130_fd_sc_hd__conb_1 _24_ (.LO(uio_oe[4]));
 sky130_fd_sc_hd__conb_1 _25_ (.LO(uio_oe[5]));
 sky130_fd_sc_hd__conb_1 _26_ (.LO(uio_oe[6]));
 sky130_fd_sc_hd__conb_1 _27_ (.LO(uio_oe[7]));
 sky130_fd_sc_hd__conb_1 _28_ (.LO(uio_out[0]));
 sky130_fd_sc_hd__conb_1 _29_ (.LO(uio_out[1]));
 sky130_fd_sc_hd__conb_1 _30_ (.LO(uio_out[2]));
 sky130_fd_sc_hd__conb_1 _31_ (.LO(uio_out[3]));
 sky130_fd_sc_hd__conb_1 _32_ (.LO(uio_out[4]));
 sky130_fd_sc_hd__conb_1 _33_ (.LO(uio_out[5]));
 sky130_fd_sc_hd__conb_1 _34_ (.LO(uio_out[6]));
 sky130_fd_sc_hd__conb_1 _35_ (.LO(uio_out[7]));
 sky130_fd_sc_hd__conb_1 _36_ (.LO(uo_out[4]));
 sky130_fd_sc_hd__conb_1 _37_ (.LO(uo_out[5]));
 sky130_fd_sc_hd__conb_1 _38_ (.LO(uo_out[6]));
 sky130_fd_sc_hd__conb_1 _39_ (.LO(uo_out[7]));
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_0_Right_0 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_1_Right_1 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_2_Right_2 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_3_Right_3 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_4_Right_4 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_5_Right_5 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_6_Right_6 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_7_Right_7 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_8_Right_8 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_0_Left_9 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_1_Left_10 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_2_Left_11 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_3_Left_12 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_4_Left_13 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_5_Left_14 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_6_Left_15 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_7_Left_16 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_8_Left_17 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_0_18 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_2_19 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_4_20 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_6_21 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_8_22 ();
endmodule
