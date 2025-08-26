module tt_if (
    // TinyTapeout GPIO (exact names - do not change)
    input i_clk,
    input i_rst_n,
    input i_ena,
    input [7:0] ui_in,
    output [7:0] uo_out,
    input [7:0] uio_in,
    output [7:0] uio_out,
    output [7:0] uio_oe
);

  // Internal AXI signals
  logic aw_valid, aw_ready;
  logic [7:0] aw_addr;
  logic w_valid, w_ready;
  logic [7:0] w_data;
  logic w_strb;
  logic b_valid, b_ready;
  logic [1:0] b_resp;
  logic ar_valid, ar_ready;
  logic [7:0] ar_addr;
  logic r_valid, r_ready;
  logic [7:0] r_data;
  logic [1:0] r_resp;

  // Instantiate the TinyTapeout to AXI bridge
  tt_to_axi #(
      .DATA_WIDTH(8),
      .ADDR_WIDTH(8)
  ) tt_to_axi_inst (
      .i_clk(i_clk),
      .i_rst_n(i_rst_n),
      .i_ena(i_ena),
      .i_ui_in(ui_in),
      .o_uo_out(uo_out),
      .i_uio_in(uio_in),
      .o_uio_out(uio_out),
      .o_uio_oe(uio_oe),
      // AXI Interface
      .aw_valid(aw_valid),
      .aw_ready(aw_ready),
      .aw_addr(aw_addr),
      .w_valid(w_valid),
      .w_ready(w_ready),
      .w_data(w_data),
      .w_strb(w_strb),
      .b_valid(b_valid),
      .b_ready(b_ready),
      .b_resp(b_resp),
      .ar_valid(ar_valid),
      .ar_ready(ar_ready),
      .ar_addr(ar_addr),
      .r_valid(r_valid),
      .r_ready(r_ready),
      .r_data(r_data),
      .r_resp(r_resp)
  );
endmodule

`default_nettype wire
