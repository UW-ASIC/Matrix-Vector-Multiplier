module DAC_input_generator #(
    parameter int TOTAL_BITS = 8,
    parameter int BIN_BITS   = 5,
    localparam int THERM_BITS  = TOTAL_BITS - BIN_BITS,
    localparam int OUTPUT_BITS = BIN_BITS + ((1 << THERM_BITS) - 1)
)
(
    input  logic clk,
    input  logic rst_n,
    output logic [OUTPUT_BITS-1:0] o_DAC_input
);

    // Internal signals
    logic [TOTAL_BITS-1:0] digital_input;
    logic [OUTPUT_BITS-1:0] DAC_input;

    // Simple counter to sweep all input codes
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            digital_input <= '0;
        else
            digital_input <= digital_input + 1;
    end

    // Instantiate bin_to_seg
    bin_to_seg #(
        .TOTAL_BITS(TOTAL_BITS),
        .BIN_BITS(BIN_BITS)
    ) bin_to_seg_inst (
        .clk(clk),
        .rst_n(rst_n),
        .in_data(digital_input),
        .out_data(DAC_input)
    );

    // Connect output
    assign o_DAC_input = DAC_input;

endmodule
