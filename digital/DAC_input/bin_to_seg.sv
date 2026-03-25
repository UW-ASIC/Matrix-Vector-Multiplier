module bin_to_seg #(
    parameter int TOTAL_BITS = 8,
    parameter int BIN_BITS = 5,
    localparam int THERM_BITS = TOTAL_BITS - BIN_BITS,
    localparam int OUTPUT_BITS = BIN_BITS + ((1 << THERM_BITS) - 1)
) (
    input  logic [TOTAL_BITS-1:0] in_data,
    input  logic clk,
    input  logic rst_n,
    output logic [OUTPUT_BITS-1:0] out_data
);

    // Optional check for illegal parameters
    generate
        if (THERM_BITS <= 0) begin
            initial begin
                $error("%m ** Illegal Condition: THERM_BITS <= 0 **");
            end
        end
    endgenerate

    logic [THERM_BITS-1:0] therm_part;

    // Convert upper bits to thermometer code
    always_comb begin
        integer i;
        for (i = 0; i < THERM_BITS; i=i+1) begin
            therm_part[i] = (i < in_data[TOTAL_BITS-1:BIN_BITS]) ? 1'b1 : 1'b0;
        end
    end

    // Register output
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            out_data <= '0;
        else
            out_data <= {therm_part, in_data[BIN_BITS-1:0]};
    end

endmodule
