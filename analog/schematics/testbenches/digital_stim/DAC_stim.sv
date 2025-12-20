`timescale 1ns/1ns
module DAC_stim();
    // Parameters
    parameter DAC_WIDTH  = 8;
    parameter CLK_PERIOD = 15.151515;

    // Signals
    logic clk;
    logic rst_n;
    logic [DAC_WIDTH-1:0] dac_data;
    logic dac_out;

    initial begin
        forever #(CLK_PERIOD/2) clk = ~clk;
    end
endmodule
