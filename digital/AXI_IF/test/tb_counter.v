`include "counter_4bit.v"
`default_nettype none

module tb_counter (
    output wire [3:0] count_out  // Counter output to observe
);
  reg clk;
  reg rst_n;
  reg enable;

  counter_4bit counter (
      .rst_n(rst_n),
      .clk(clk),
      .enable(enable),
      .count(count_out)
  );

  parameter CLK_PERIOD = 15.1515;  // In ns

  always #(CLK_PERIOD / 2) clk = ~clk;
  initial begin
    $dumpfile("tb_counter.vcd");
    $dumpvars(0, tb_counter);

    // Initial stimulus
    #1 rst_n = 1'bx;
    clk = 1'bx;
    enable = 1;

    #(CLK_PERIOD * 3) rst_n = 1;
    #(CLK_PERIOD * 3) rst_n = 0;
    clk = 0;

    repeat (5) @(posedge clk);
    rst_n = 1;

    @(posedge clk);
    repeat (2) @(posedge clk);

    $finish(2);
  end
endmodule

`default_nettype wire
