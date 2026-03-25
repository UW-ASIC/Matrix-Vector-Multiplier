//binary to segmented, parameterizable thermometer values
module bin_to_seg #(
    parameter integer TOTAL_BITS = 8,
    parameter integer BIN_BITS = 5,
    localparam int OUTPUT_BITS = BIN_BITS + (1 << (TOTAL_BITS-BIN_BITS)) - 1
)   
(
    input logic clk,
    input logic rst_n,
    input logic [TOTAL_BITS-1:0] in_data
    output logic [OUTPUT_BITS-1:0] out_data
);
    //generate
    //    if (BIN_BITS + THERM_BITS != TOTAL_BITS)begin
    //        $error("%m ** Illegal Condition ** CONDITION(%d) > MAX_ALLOWED(%d)", CONDITION, MAX_ALLOWED);
    //    end
    //endgenerate
    always_ff @(posedge clk) begin
        if (!rst_n) begin
            out_data <= '0
        end else begin
            out_data[BIN_BITS-1:0] <= in_data[BIN_BITS-1:0]
        end
    end
endmodule
