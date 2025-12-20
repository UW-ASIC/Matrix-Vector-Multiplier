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
 wire net8;
 wire net9;
 wire net10;
 wire net11;
 wire net12;
 wire net13;
 wire net14;
 wire net15;
 wire net16;
 wire net17;
 wire net18;
 wire net19;
 wire net20;
 wire net21;
 wire net22;
 wire net23;
 wire net3;
 wire net4;
 wire net5;
 wire net6;
 wire net24;
 wire net25;
 wire net26;
 wire clknet_0_i_clk;
 wire net1;
 wire net2;
 wire net7;
 wire clknet_1_0__leaf_i_clk;
 wire clknet_1_1__leaf_i_clk;
 wire net27;
 wire net28;
 wire net29;
 wire net30;
 wire net31;

 sky130_fd_sc_hd__nand2_1 _08_ (.A(net3),
    .B(net1),
    .Y(_04_));
 sky130_fd_sc_hd__xnor2_1 _09_ (.A(net4),
    .B(_04_),
    .Y(_00_));
 sky130_fd_sc_hd__and4_1 _10_ (.A(net3),
    .B(net4),
    .C(net5),
    .D(net1),
    .X(_05_));
 sky130_fd_sc_hd__a31o_1 _11_ (.A1(net3),
    .A2(net4),
    .A3(net1),
    .B1(net5),
    .X(_06_));
 sky130_fd_sc_hd__and2b_1 _12_ (.A_N(_05_),
    .B(_06_),
    .X(_01_));
 sky130_fd_sc_hd__xor2_1 _13_ (.A(net31),
    .B(_05_),
    .X(_02_));
 sky130_fd_sc_hd__or2_1 _14_ (.A(net3),
    .B(net1),
    .X(_07_));
 sky130_fd_sc_hd__and2_1 _15_ (.A(_04_),
    .B(_07_),
    .X(_03_));
 sky130_fd_sc_hd__dfrtp_1 _16_ (.CLK(clknet_1_1__leaf_i_clk),
    .D(net30),
    .RESET_B(net28),
    .Q(net4));
 sky130_fd_sc_hd__dfrtp_1 _17_ (.CLK(clknet_1_0__leaf_i_clk),
    .D(_01_),
    .RESET_B(net28),
    .Q(net5));
 sky130_fd_sc_hd__dfrtp_1 _18_ (.CLK(clknet_1_0__leaf_i_clk),
    .D(_02_),
    .RESET_B(net28),
    .Q(net6));
 sky130_fd_sc_hd__dfrtp_1 _19_ (.CLK(clknet_1_1__leaf_i_clk),
    .D(_03_),
    .RESET_B(net28),
    .Q(net3));
 sky130_fd_sc_hd__conb_1 tt_if_8 (.LO(net8));
 sky130_fd_sc_hd__conb_1 tt_if_9 (.LO(net9));
 sky130_fd_sc_hd__conb_1 tt_if_10 (.LO(net10));
 sky130_fd_sc_hd__conb_1 tt_if_11 (.LO(net11));
 sky130_fd_sc_hd__conb_1 tt_if_12 (.LO(net12));
 sky130_fd_sc_hd__conb_1 tt_if_13 (.LO(net13));
 sky130_fd_sc_hd__conb_1 tt_if_14 (.LO(net14));
 sky130_fd_sc_hd__conb_1 tt_if_15 (.LO(net15));
 sky130_fd_sc_hd__conb_1 tt_if_16 (.LO(net16));
 sky130_fd_sc_hd__conb_1 tt_if_17 (.LO(net17));
 sky130_fd_sc_hd__conb_1 tt_if_18 (.LO(net18));
 sky130_fd_sc_hd__conb_1 tt_if_19 (.LO(net19));
 sky130_fd_sc_hd__conb_1 tt_if_20 (.LO(net20));
 sky130_fd_sc_hd__conb_1 tt_if_21 (.LO(net21));
 sky130_fd_sc_hd__conb_1 tt_if_22 (.LO(net22));
 sky130_fd_sc_hd__conb_1 tt_if_23 (.LO(net23));
 sky130_fd_sc_hd__conb_1 tt_if_24 (.LO(net24));
 sky130_fd_sc_hd__conb_1 tt_if_25 (.LO(net25));
 sky130_fd_sc_hd__conb_1 tt_if_26 (.LO(net26));
 sky130_fd_sc_hd__clkbuf_16 clkbuf_0_i_clk (.A(i_clk),
    .X(clknet_0_i_clk));
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
 sky130_fd_sc_hd__clkbuf_1 input1 (.A(net29),
    .X(net1));
 sky130_fd_sc_hd__dlymetal6s2s_1 input2 (.A(net27),
    .X(net2));
 sky130_fd_sc_hd__buf_2 output3 (.A(net3),
    .X(uo_out[0]));
 sky130_fd_sc_hd__buf_2 output4 (.A(net4),
    .X(uo_out[1]));
 sky130_fd_sc_hd__buf_2 output5 (.A(net5),
    .X(uo_out[2]));
 sky130_fd_sc_hd__buf_2 output6 (.A(net6),
    .X(uo_out[3]));
 sky130_fd_sc_hd__conb_1 tt_if_7 (.LO(net7));
 sky130_fd_sc_hd__clkbuf_16 clkbuf_1_0__f_i_clk (.A(clknet_0_i_clk),
    .X(clknet_1_0__leaf_i_clk));
 sky130_fd_sc_hd__clkbuf_16 clkbuf_1_1__f_i_clk (.A(clknet_0_i_clk),
    .X(clknet_1_1__leaf_i_clk));
 sky130_fd_sc_hd__dlygate4sd3_1 hold1 (.A(i_rst_n),
    .X(net27));
 sky130_fd_sc_hd__dlygate4sd3_1 hold2 (.A(net2),
    .X(net28));
 sky130_fd_sc_hd__dlygate4sd3_1 hold3 (.A(i_ena),
    .X(net29));
 sky130_fd_sc_hd__dlygate4sd3_1 hold4 (.A(_00_),
    .X(net30));
 sky130_fd_sc_hd__dlygate4sd3_1 hold5 (.A(net6),
    .X(net31));
 assign uio_oe[0] = net7;
 assign uio_oe[1] = net8;
 assign uio_oe[2] = net9;
 assign uio_oe[3] = net10;
 assign uio_oe[4] = net11;
 assign uio_oe[5] = net12;
 assign uio_oe[6] = net13;
 assign uio_oe[7] = net14;
 assign uio_out[0] = net15;
 assign uio_out[1] = net16;
 assign uio_out[2] = net17;
 assign uio_out[3] = net18;
 assign uio_out[4] = net19;
 assign uio_out[5] = net20;
 assign uio_out[6] = net21;
 assign uio_out[7] = net22;
 assign uo_out[4] = net23;
 assign uo_out[5] = net24;
 assign uo_out[6] = net25;
 assign uo_out[7] = net26;
endmodule
