module tt_if (
    input i_clk,
    input i_rst_n,
    input i_ena,
    input [7:0] ui_in,
    output [7:0] uo_out,
    input [7:0] uio_in,
    output [7:0] uio_out,
    output [7:0] uio_oe
);

  wire [3:0] count;

  counter_4bit counter_inst (
      .clk(i_clk),
      .rst_n(i_rst_n),
      .enable(i_ena),
      .count(count)
  );

  assign uo_out  = {4'b0000, count};
  assign uio_out = 8'b0000_0000;
  assign uio_oe  = 8'b0000_0000;

endmodule

`default_nettype wire
