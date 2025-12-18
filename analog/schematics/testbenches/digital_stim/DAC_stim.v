// Digital input for DAC testbench
module DAC_stim #(parameter WIDTH = 8)(
    input wire clk,
    input wire rst_n,
    input wire [WIDTH-1:0] dac_in,
    output reg [WIDTH-1:0] dac_out
);

always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        dac_out <= 0;
    end else begin
        dac_out <= dac_in;
    end
end

endmodule
