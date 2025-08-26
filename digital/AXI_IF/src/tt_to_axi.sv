module tt_to_axi #(
    parameter DATA_WIDTH = 8,
    parameter ADDR_WIDTH = 8
) (
    // TinyTapeout GPIO
    input              i_clk,
    input              i_rst_n,
    input              i_ena,
    input        [7:0] i_ui_in,    // 8 dedicated inputs
    output logic [7:0] o_uo_out,   // 8 dedicated outputs
    input        [7:0] i_uio_in,   // 8 bidirectional inputs
    output logic [7:0] o_uio_out,  // 8 bidirectional outputs
    output logic [7:0] o_uio_oe,   // 8 bidirectional output enables

    // AXI4-Lite Interface
    // Write Address Channel
    output logic aw_valid,
    input aw_ready,
    output logic [ADDR_WIDTH-1:0] aw_addr,

    // Write Data Channel
    output logic w_valid,
    input w_ready,
    output logic [DATA_WIDTH-1:0] w_data,
    output logic [(DATA_WIDTH/8)-1:0] w_strb,

    // Write Response Channel
    input b_valid,
    output logic b_ready,
    input [1:0] b_resp,

    // Read Address Channel
    output logic ar_valid,
    input ar_ready,
    output logic [ADDR_WIDTH-1:0] ar_addr,

    // Read Data Channel
    input r_valid,
    output logic r_ready,
    input [DATA_WIDTH-1:0] r_data,
    input [1:0] r_resp
);

  // State machine for AXI phases
  typedef enum logic [2:0] {
    IDLE       = 3'b000,
    WRITE_ADDR = 3'b001,
    WRITE_DATA = 3'b010,
    WRITE_RESP = 3'b011,
    READ_ADDR  = 3'b100,
    READ_DATA  = 3'b101
  } axi_state_t;

  axi_state_t state, next_state;

  // Command interface from i_ui_in
  // i_ui_in[1:0] = command: 00=idle, 01=write, 10=read, 11=reserved
  // i_ui_in[7:2] = address for transaction (6 bits)
  logic [1:0] cmd;
  logic [5:0] cmd_addr_6bit;
  logic [ADDR_WIDTH-1:0] cmd_addr;

  assign cmd = i_ui_in[1:0];
  assign cmd_addr_6bit = i_ui_in[7:2];
  assign cmd_addr = {{(ADDR_WIDTH - 6) {1'b0}}, cmd_addr_6bit};

  // Data storage for write transactions
  logic [DATA_WIDTH-1:0] write_data_reg;
  logic [(DATA_WIDTH/8)-1:0] write_strb_reg;
  logic [ADDR_WIDTH-1:0] addr_reg;

  // State machine - next state logic
  always_comb begin
    next_state = state;

    case (state)
      IDLE: begin
        case (cmd)
          2'b01:   next_state = WRITE_ADDR;  // Write command
          2'b10:   next_state = READ_ADDR;  // Read command
          default: next_state = IDLE;
        endcase
      end

      WRITE_ADDR: begin
        if (aw_valid && aw_ready) next_state = WRITE_DATA;
      end

      WRITE_DATA: begin
        if (w_valid && w_ready) next_state = WRITE_RESP;
      end

      WRITE_RESP: begin
        if (b_valid && b_ready) next_state = IDLE;
      end

      READ_ADDR: begin
        if (ar_valid && ar_ready) next_state = READ_DATA;
      end

      READ_DATA: begin
        if (r_valid && r_ready) next_state = IDLE;
      end

      default: next_state = IDLE;
    endcase
  end

  // State machine - state register
  always_ff @(posedge i_clk) begin
    if (!i_rst_n) begin
      state <= IDLE;
      write_data_reg <= {DATA_WIDTH{1'b0}};
      write_strb_reg <= {(DATA_WIDTH / 8) {1'b0}};
      addr_reg <= {ADDR_WIDTH{1'b0}};
    end else if (i_ena) begin
      state <= next_state;

      // Capture address and write data when entering from IDLE
      if (state == IDLE) begin
        addr_reg <= cmd_addr;  // Capture address
        if (next_state == WRITE_ADDR) begin
          write_data_reg <= i_uio_in;  // Get write data from bidirectional pins
          write_strb_reg <= {(DATA_WIDTH / 8) {1'b1}};  // Full byte enable
        end
      end
    end
  end

  // AXI signal assignments
  always_comb begin
    // Default values
    aw_valid = 1'b0;
    aw_addr  = {ADDR_WIDTH{1'b0}};
    w_valid  = 1'b0;
    w_data   = {DATA_WIDTH{1'b0}};
    w_strb   = {(DATA_WIDTH / 8) {1'b0}};
    b_ready  = 1'b0;
    ar_valid = 1'b0;
    ar_addr  = {ADDR_WIDTH{1'b0}};
    r_ready  = 1'b0;

    case (state)
      WRITE_ADDR: begin
        aw_valid = 1'b1;
        aw_addr  = addr_reg;
      end

      WRITE_DATA: begin
        w_valid = 1'b1;
        w_data  = write_data_reg;
        w_strb  = write_strb_reg;
      end

      WRITE_RESP: begin
        b_ready = 1'b1;
      end

      READ_ADDR: begin
        ar_valid = 1'b1;
        ar_addr  = addr_reg;
      end

      READ_DATA: begin
        r_ready = 1'b1;
      end
    endcase
  end

  // TinyTapeout GPIO pin mapping based on state
  always_comb begin
    // Default values
    o_uo_out  = 8'b0;
    o_uio_out = 8'b0;
    o_uio_oe  = 8'b0;

    case (state)
      IDLE: begin
        o_uo_out  = {5'b0, state};  // Show current state
        o_uio_out = 8'b0;
        o_uio_oe  = 8'b00000000;  // All inputs (listening for write data)
      end

      WRITE_ADDR: begin
        o_uo_out  = addr_reg[7:0];  // Address on dedicated outputs
        o_uio_out = {5'b0, state};  // State info on bidirectional
        o_uio_oe  = 8'b00000111;  // Enable output for state bits
      end

      WRITE_DATA: begin
        o_uo_out  = w_data;  // Data on dedicated outputs
        o_uio_out = {4'b0, w_strb[0], state};  // Strobe + state
        o_uio_oe  = 8'b00001111;  // Enable output for strobe + state
      end

      WRITE_RESP: begin
        o_uo_out  = {6'b0, b_resp};  // Write response on dedicated outputs
        o_uio_out = {4'b0, b_valid, state};  // Response valid + state
        o_uio_oe  = 8'b00001111;  // Enable output for control bits
      end

      READ_ADDR: begin
        o_uo_out  = addr_reg[7:0];  // Read address on dedicated outputs
        o_uio_out = {5'b0, state};  // State info
        o_uio_oe  = 8'b00000111;  // Enable output for state bits
      end

      READ_DATA: begin
        o_uo_out  = r_data;  // Read data on dedicated outputs
        o_uio_out = {3'b0, r_valid, r_resp, state};  // Control info
        o_uio_oe  = 8'b00011111;  // Enable output for control bits
      end

      default: begin
        o_uo_out  = 8'hFF;  // Error indicator
        o_uio_out = 8'b0;
        o_uio_oe  = 8'b00000000;
      end
    endcase
  end

endmodule

`default_nettype wire
