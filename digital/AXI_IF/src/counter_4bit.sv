`timescale 1ns/1ns

module counter_4bit (
    input logic clk,
    input logic rst_n,
    input logic enable,
    output logic [3:0] count
);
  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) count <= '0;
    else if (enable) count <= count + 1;
  end
endmodule
`default_nettype none
