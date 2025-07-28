`default_nettype none

// Connects to the DAC module and State Machine Digital Logic, providing the
// data and address respectively, waiting on an acknowledge bit from the DAC
// Module, that the State Machine also uses to determine when the DAC is ready
// to be routed to the correct location with the address bits as well
module i2c_module #(
    parameter DATA_WIDTH = 8,  // Width of the data
    parameter VECTOR_SIZE = 4,  // used to find out the addr width required
    parameter ADDR_WIDTH = $clog2((VECTOR_SIZE * 2) + (VECTOR_SIZE * VECTOR_SIZE))
) (
    // Connections to the TinyTapeout GPIO
    input i_clk,    // clock
    input i_rst_n,  // reset_n - low to reset
    input ena,      // always 1 when the design is powered, so you can ignore it

    input  [7:0] ui_in,  // Dedicated inputs
    output [7:0] uo_out, // Dedicated outputs

    input  [7:0] uio_in,   // IOs: Input path
    output [7:0] uio_out,  // IOs: Output path
    output [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)

    // Internal Connections
    output [DATA_WIDTH-1:0] o_data_out,  // Data output to DAC
    input i_ack_in,  // Acknowledge input from State Machine
    output [ADDR_WIDTH-1:0] o_addr_out  // Address output to State Machine Logic
);
  // Clock Freq Max: 66MHz, https://tinytapeout.com/specs/gpio/
  // I2C Interface
  logic i2c_sda_in, i2c_scl_in, i2c_sda_out;
  assign i2c_sda_in = ui_in[0];
  assign i2c_scl_in = ui_in[1];
  assign uo_out[0]  = i2c_sda_out;



  // ======================================
  // To prevent Warnings
  // ======================================
  // List all unused inputs to prevent warnings
  wire _unused = &{ena, clk, rst_n, 1'b0};

  // If not used assign to 0
  always_comb begin
    uo_out  = 0;
    uio_out = 0;
    uio_oe  = 0;
  end
endmodule
