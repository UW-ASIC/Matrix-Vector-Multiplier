`default_nettype none

// Internal Structure that just routes the DAC output to the right location
// Should exist as a handshake between the I2C Module and the DAC Module,
// giving a signal when the DAC is ready to be routed to the correct address
// The analog signal is then given to one of the lines of o_data_out
module DAC_Router #(
    // Make sure these parameters match the i2c_module parameters
    parameter VECTOR_SIZE = 4,  // used to find out the addr width required
    parameter TOTAL_OPTIONS = (VECTOR_SIZE * 2) + (VECTOR_SIZE * VECTOR_SIZE),
    parameter ADDR_WIDTH = $clog2(TOTAL_OPTIONS)  // Address width required for the routing
) (
    input i_clk,   // Clock for synchronous logic
    input i_rst_n, // Reset (active low)

    // From/TO DAC
    input  i_dac_data_valid,  // DAC data valid signal
    input  i_dac_ack_in,      // Acknowledge input from DAC
    output o_dac_enable,      // Enable signal to DAC

    // From/TO I2C Module
    input      [ADDR_WIDTH-1:0] i_addr_out,    // Address output received from I2C Module
    input                       i_addr_ready,  // Address ready from I2C Module
    output reg                  o_ack_out,     // Acknowledge bit to I2C Module

    // From/TO Analog Matrix-Vector Multiplier
    output reg [TOTAL_OPTIONS-1:0] o_data_out,  // Data re-route to Analog Matrix-Vector Multiplier
    output reg o_routing_valid  // Signal indicating routing is valid
);

  // Internal state machine for handshaking
  typedef enum logic [1:0] {
    IDLE,
    ROUTING,
    ACKNOWLEDGE,
    WAIT_CLEAR
  } state_t;

  state_t current_state, next_state;

  // Registered address to hold during routing
  reg [ADDR_WIDTH-1:0] latched_addr;
  reg addr_valid;

  // State machine - sequential logic
  always_ff @(posedge i_clk or negedge i_rst_n) begin
    if (!i_rst_n) begin
      current_state <= IDLE;
      latched_addr <= '0;
      addr_valid <= 1'b0;
    end else begin
      current_state <= next_state;

      // Latch address when it becomes ready
      if (i_addr_ready && current_state == IDLE) begin
        latched_addr <= i_addr_out;
        addr_valid   <= 1'b1;
      end else if (current_state == WAIT_CLEAR) begin
        addr_valid <= 1'b0;
      end
    end
  end

  // State machine - combinational logic
  always_comb begin
    next_state = current_state;

    case (current_state)
      IDLE: begin
        if (i_addr_ready && i_dac_data_valid) begin
          next_state = ROUTING;
        end
      end

      ROUTING: begin
        if (i_dac_ack_in) begin
          next_state = ACKNOWLEDGE;
        end
      end

      ACKNOWLEDGE: begin
        next_state = WAIT_CLEAR;
      end

      WAIT_CLEAR: begin
        if (!i_addr_ready) begin
          next_state = IDLE;
        end
      end
    endcase
  end

  // Output control logic
  always_comb begin
    // Default values
    o_data_out = '0;
    o_ack_out = 1'b0;
    o_dac_enable = 1'b0;
    o_routing_valid = 1'b0;

    case (current_state)
      IDLE: begin
        o_dac_enable = i_addr_ready;  // Enable DAC when address is ready
      end

      ROUTING: begin
        o_dac_enable = 1'b1;
        o_routing_valid = 1'b1;

        // Route DAC output to the specified address line
        if (addr_valid && latched_addr < TOTAL_OPTIONS) begin
          o_data_out[latched_addr] = 1'b1;  // Enable the selected output line
        end
      end

      ACKNOWLEDGE: begin
        o_ack_out       = 1'b1;  // Send acknowledge to I2C module
        o_routing_valid = 1'b1;

        // Keep routing active during acknowledge
        if (addr_valid && latched_addr < TOTAL_OPTIONS) begin
          o_data_out[latched_addr] = 1'b1;
        end
      end

      WAIT_CLEAR: begin
        // All outputs return to default (cleared above)
      end
    endcase
  end

  // Address bounds checking for safety
  always_ff @(posedge i_clk) begin
    if (i_addr_ready && i_addr_out >= TOTAL_OPTIONS) begin
      $warning("DAC_Router: Address %d exceeds maximum %d", i_addr_out, TOTAL_OPTIONS - 1);
    end
  end

  // Optional: Debug output for simulation
`ifdef SIMULATION
  always_ff @(posedge i_clk) begin
    if (current_state == ROUTING) begin
      $display("DAC_Router: Routing to address %d at time %t", latched_addr, $time);
    end
  end
`endif

endmodule
