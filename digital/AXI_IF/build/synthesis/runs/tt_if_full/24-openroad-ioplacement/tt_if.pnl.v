module tt_if (i_clk,
    i_ena,
    i_rst_n,
    VDD,
    VSS,
    ui_in,
    uio_in,
    uio_oe,
    uio_out,
    uo_out);
 input i_clk;
 input i_ena;
 input i_rst_n;
 inout VDD;
 inout VSS;
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
    .VGND(VSS),
    .VNB(VSS),
    .VPB(VDD),
    .VPWR(VDD),
    .Y(_04_));
 sky130_fd_sc_hd__xnor2_2 _09_ (.A(uo_out[1]),
    .B(_04_),
    .VGND(VSS),
    .VNB(VSS),
    .VPB(VDD),
    .VPWR(VDD),
    .Y(_00_));
 sky130_fd_sc_hd__and4_2 _10_ (.A(uo_out[0]),
    .B(uo_out[1]),
    .C(uo_out[2]),
    .D(i_ena),
    .VGND(VSS),
    .VNB(VSS),
    .VPB(VDD),
    .VPWR(VDD),
    .X(_05_));
 sky130_fd_sc_hd__a31o_2 _11_ (.A1(uo_out[0]),
    .A2(uo_out[1]),
    .A3(i_ena),
    .B1(uo_out[2]),
    .VGND(VSS),
    .VNB(VSS),
    .VPB(VDD),
    .VPWR(VDD),
    .X(_06_));
 sky130_fd_sc_hd__and2b_2 _12_ (.A_N(_05_),
    .B(_06_),
    .VGND(VSS),
    .VNB(VSS),
    .VPB(VDD),
    .VPWR(VDD),
    .X(_01_));
 sky130_fd_sc_hd__xor2_2 _13_ (.A(uo_out[3]),
    .B(_05_),
    .VGND(VSS),
    .VNB(VSS),
    .VPB(VDD),
    .VPWR(VDD),
    .X(_02_));
 sky130_fd_sc_hd__or2_2 _14_ (.A(uo_out[0]),
    .B(i_ena),
    .VGND(VSS),
    .VNB(VSS),
    .VPB(VDD),
    .VPWR(VDD),
    .X(_07_));
 sky130_fd_sc_hd__and2_2 _15_ (.A(_04_),
    .B(_07_),
    .VGND(VSS),
    .VNB(VSS),
    .VPB(VDD),
    .VPWR(VDD),
    .X(_03_));
 sky130_fd_sc_hd__dfrtp_2 _16_ (.CLK(i_clk),
    .D(_00_),
    .RESET_B(i_rst_n),
    .VGND(VSS),
    .VNB(VSS),
    .VPB(VDD),
    .VPWR(VDD),
    .Q(uo_out[1]));
 sky130_fd_sc_hd__dfrtp_2 _17_ (.CLK(i_clk),
    .D(_01_),
    .RESET_B(i_rst_n),
    .VGND(VSS),
    .VNB(VSS),
    .VPB(VDD),
    .VPWR(VDD),
    .Q(uo_out[2]));
 sky130_fd_sc_hd__dfrtp_2 _18_ (.CLK(i_clk),
    .D(_02_),
    .RESET_B(i_rst_n),
    .VGND(VSS),
    .VNB(VSS),
    .VPB(VDD),
    .VPWR(VDD),
    .Q(uo_out[3]));
 sky130_fd_sc_hd__dfrtp_2 _19_ (.CLK(i_clk),
    .D(_03_),
    .RESET_B(i_rst_n),
    .VGND(VSS),
    .VNB(VSS),
    .VPB(VDD),
    .VPWR(VDD),
    .Q(uo_out[0]));
 sky130_fd_sc_hd__conb_1 _20_ (.VGND(VSS),
    .VNB(VSS),
    .VPB(VDD),
    .VPWR(VDD),
    .LO(uio_oe[0]));
 sky130_fd_sc_hd__conb_1 _21_ (.VGND(VSS),
    .VNB(VSS),
    .VPB(VDD),
    .VPWR(VDD),
    .LO(uio_oe[1]));
 sky130_fd_sc_hd__conb_1 _22_ (.VGND(VSS),
    .VNB(VSS),
    .VPB(VDD),
    .VPWR(VDD),
    .LO(uio_oe[2]));
 sky130_fd_sc_hd__conb_1 _23_ (.VGND(VSS),
    .VNB(VSS),
    .VPB(VDD),
    .VPWR(VDD),
    .LO(uio_oe[3]));
 sky130_fd_sc_hd__conb_1 _24_ (.VGND(VSS),
    .VNB(VSS),
    .VPB(VDD),
    .VPWR(VDD),
    .LO(uio_oe[4]));
 sky130_fd_sc_hd__conb_1 _25_ (.VGND(VSS),
    .VNB(VSS),
    .VPB(VDD),
    .VPWR(VDD),
    .LO(uio_oe[5]));
 sky130_fd_sc_hd__conb_1 _26_ (.VGND(VSS),
    .VNB(VSS),
    .VPB(VDD),
    .VPWR(VDD),
    .LO(uio_oe[6]));
 sky130_fd_sc_hd__conb_1 _27_ (.VGND(VSS),
    .VNB(VSS),
    .VPB(VDD),
    .VPWR(VDD),
    .LO(uio_oe[7]));
 sky130_fd_sc_hd__conb_1 _28_ (.VGND(VSS),
    .VNB(VSS),
    .VPB(VDD),
    .VPWR(VDD),
    .LO(uio_out[0]));
 sky130_fd_sc_hd__conb_1 _29_ (.VGND(VSS),
    .VNB(VSS),
    .VPB(VDD),
    .VPWR(VDD),
    .LO(uio_out[1]));
 sky130_fd_sc_hd__conb_1 _30_ (.VGND(VSS),
    .VNB(VSS),
    .VPB(VDD),
    .VPWR(VDD),
    .LO(uio_out[2]));
 sky130_fd_sc_hd__conb_1 _31_ (.VGND(VSS),
    .VNB(VSS),
    .VPB(VDD),
    .VPWR(VDD),
    .LO(uio_out[3]));
 sky130_fd_sc_hd__conb_1 _32_ (.VGND(VSS),
    .VNB(VSS),
    .VPB(VDD),
    .VPWR(VDD),
    .LO(uio_out[4]));
 sky130_fd_sc_hd__conb_1 _33_ (.VGND(VSS),
    .VNB(VSS),
    .VPB(VDD),
    .VPWR(VDD),
    .LO(uio_out[5]));
 sky130_fd_sc_hd__conb_1 _34_ (.VGND(VSS),
    .VNB(VSS),
    .VPB(VDD),
    .VPWR(VDD),
    .LO(uio_out[6]));
 sky130_fd_sc_hd__conb_1 _35_ (.VGND(VSS),
    .VNB(VSS),
    .VPB(VDD),
    .VPWR(VDD),
    .LO(uio_out[7]));
 sky130_fd_sc_hd__conb_1 _36_ (.VGND(VSS),
    .VNB(VSS),
    .VPB(VDD),
    .VPWR(VDD),
    .LO(uo_out[4]));
 sky130_fd_sc_hd__conb_1 _37_ (.VGND(VSS),
    .VNB(VSS),
    .VPB(VDD),
    .VPWR(VDD),
    .LO(uo_out[5]));
 sky130_fd_sc_hd__conb_1 _38_ (.VGND(VSS),
    .VNB(VSS),
    .VPB(VDD),
    .VPWR(VDD),
    .LO(uo_out[6]));
 sky130_fd_sc_hd__conb_1 _39_ (.VGND(VSS),
    .VNB(VSS),
    .VPB(VDD),
    .VPWR(VDD),
    .LO(uo_out[7]));
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_0_Right_0 (.VGND(VSS),
    .VNB(VSS),
    .VPB(VDD),
    .VPWR(VDD));
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_1_Right_1 (.VGND(VSS),
    .VNB(VSS),
    .VPB(VDD),
    .VPWR(VDD));
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_2_Right_2 (.VGND(VSS),
    .VNB(VSS),
    .VPB(VDD),
    .VPWR(VDD));
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_3_Right_3 (.VGND(VSS),
    .VNB(VSS),
    .VPB(VDD),
    .VPWR(VDD));
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_4_Right_4 (.VGND(VSS),
    .VNB(VSS),
    .VPB(VDD),
    .VPWR(VDD));
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_5_Right_5 (.VGND(VSS),
    .VNB(VSS),
    .VPB(VDD),
    .VPWR(VDD));
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_6_Right_6 (.VGND(VSS),
    .VNB(VSS),
    .VPB(VDD),
    .VPWR(VDD));
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_7_Right_7 (.VGND(VSS),
    .VNB(VSS),
    .VPB(VDD),
    .VPWR(VDD));
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_8_Right_8 (.VGND(VSS),
    .VNB(VSS),
    .VPB(VDD),
    .VPWR(VDD));
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_0_Left_9 (.VGND(VSS),
    .VNB(VSS),
    .VPB(VDD),
    .VPWR(VDD));
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_1_Left_10 (.VGND(VSS),
    .VNB(VSS),
    .VPB(VDD),
    .VPWR(VDD));
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_2_Left_11 (.VGND(VSS),
    .VNB(VSS),
    .VPB(VDD),
    .VPWR(VDD));
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_3_Left_12 (.VGND(VSS),
    .VNB(VSS),
    .VPB(VDD),
    .VPWR(VDD));
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_4_Left_13 (.VGND(VSS),
    .VNB(VSS),
    .VPB(VDD),
    .VPWR(VDD));
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_5_Left_14 (.VGND(VSS),
    .VNB(VSS),
    .VPB(VDD),
    .VPWR(VDD));
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_6_Left_15 (.VGND(VSS),
    .VNB(VSS),
    .VPB(VDD),
    .VPWR(VDD));
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_7_Left_16 (.VGND(VSS),
    .VNB(VSS),
    .VPB(VDD),
    .VPWR(VDD));
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_8_Left_17 (.VGND(VSS),
    .VNB(VSS),
    .VPB(VDD),
    .VPWR(VDD));
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_0_18 (.VGND(VSS),
    .VPWR(VDD));
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_2_19 (.VGND(VSS),
    .VPWR(VDD));
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_4_20 (.VGND(VSS),
    .VPWR(VDD));
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_6_21 (.VGND(VSS),
    .VPWR(VDD));
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_8_22 (.VGND(VSS),
    .VPWR(VDD));
endmodule
