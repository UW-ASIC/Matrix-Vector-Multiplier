`timescale 1ns/1ns
module DAC_stim(
    output logic [7:0] dac_out,
    output logic [7:0] dac_out_n
);
    // Parameters
    parameter DAC_WIDTH  = 8;
    parameter CLK_PERIOD = 15.151515;

    initial begin
        dac_out = 0;
        dac_out_n = ~dac_out;
        #CLK_PERIOD;
        dac_out = 8'hFF; // Max value
        dac_out_n = ~dac_out;
        #CLK_PERIOD;
        dac_out = 8'h80; // Mid value
        dac_out_n = ~dac_out;
        #CLK_PERIOD;
        dac_out = 8'h00; // Min value
        dac_out_n = ~dac_out;
        #CLK_PERIOD;
        dac_out = 8'h55; // Arbitrary value
        dac_out_n = ~dac_out;
        #CLK_PERIOD;
        dac_out = 8'hAA; // Arbitrary value
        dac_out_n = ~dac_out;
        #CLK_PERIOD;
        $finish;
    end
endmodule
