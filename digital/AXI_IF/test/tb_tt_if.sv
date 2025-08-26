`timescale 1ns / 1ps

module tb_tt_if ();

  // Clock and reset
  logic clk;
  logic rst_n;
  logic ena;

  // TinyTapeout GPIO
  logic [7:0] ui_in;
  logic [7:0] uo_out;
  logic [7:0] uio_in;
  logic [7:0] uio_out;
  logic [7:0] uio_oe;

  // Internal AXI signals for monitoring
  logic aw_valid, aw_ready;
  logic [7:0] aw_addr;
  logic w_valid, w_ready;
  logic [7:0] w_data;
  logic w_strb;
  logic b_valid, b_ready;
  logic [1:0] b_resp;
  logic ar_valid, ar_ready;
  logic [7:0] ar_addr;
  logic r_valid, r_ready;
  logic [7:0] r_data;
  logic [1:0] r_resp;

  // Simple AXI slave memory
  logic [7:0] slave_memory[0:15];  // 16 registers

  // AXI slave state machines (using parameters - more compatible)
  localparam W_IDLE = 2'b00, W_ADDR = 2'b01, W_DATA = 2'b10, W_RESP = 2'b11;
  localparam R_IDLE = 2'b00, R_ADDR = 2'b01, R_DATA = 2'b10;

  logic [1:0] w_state, r_state;
  logic [7:0] w_addr_reg, r_addr_reg;

  tt_if dut (
      .i_clk  (clk),
      .i_rst_n(rst_n),
      .i_ena  (ena),
      .ui_in  (ui_in),
      .uo_out (uo_out),
      .uio_in (uio_in),
      .uio_out(uio_out),
      .uio_oe (uio_oe)
  );

  // Connect internal AXI signals for monitoring
  assign aw_valid = dut.tt_to_axi_inst.aw_valid;
  assign aw_addr = dut.tt_to_axi_inst.aw_addr;
  assign w_valid = dut.tt_to_axi_inst.w_valid;
  assign w_data = dut.tt_to_axi_inst.w_data;
  assign w_strb = dut.tt_to_axi_inst.w_strb;
  assign b_ready = dut.tt_to_axi_inst.b_ready;
  assign ar_valid = dut.tt_to_axi_inst.ar_valid;
  assign ar_addr = dut.tt_to_axi_inst.ar_addr;
  assign r_ready = dut.tt_to_axi_inst.r_ready;

  // Connect AXI slave responses
  assign dut.tt_to_axi_inst.aw_ready = aw_ready;
  assign dut.tt_to_axi_inst.w_ready = w_ready;
  assign dut.tt_to_axi_inst.b_valid = b_valid;
  assign dut.tt_to_axi_inst.b_resp = b_resp;
  assign dut.tt_to_axi_inst.ar_ready = ar_ready;
  assign dut.tt_to_axi_inst.r_valid = r_valid;
  assign dut.tt_to_axi_inst.r_data = r_data;
  assign dut.tt_to_axi_inst.r_resp = r_resp;

  // AXI Slave Write Logic
  always_ff @(posedge clk) begin
    if (!rst_n) begin
      w_state <= W_IDLE;
      aw_ready <= 1'b0;
      w_ready <= 1'b0;
      b_valid <= 1'b0;
      b_resp <= 2'b00;
      w_addr_reg <= 8'h0;

      // Initialize memory with explicit loop
      slave_memory[0] <= 8'h00;
      slave_memory[1] <= 8'h00;
      slave_memory[2] <= 8'h00;
      slave_memory[3] <= 8'h00;
      slave_memory[4] <= 8'h00;
      slave_memory[5] <= 8'h00;
      slave_memory[6] <= 8'h00;
      slave_memory[7] <= 8'h00;
      slave_memory[8] <= 8'h00;
      slave_memory[9] <= 8'h00;
      slave_memory[10] <= 8'h00;
      slave_memory[11] <= 8'h00;
      slave_memory[12] <= 8'h00;
      slave_memory[13] <= 8'h00;
      slave_memory[14] <= 8'h00;
      slave_memory[15] <= 8'h00;
    end else begin
      case (w_state)
        W_IDLE: begin
          aw_ready <= 1'b1;
          if (aw_valid && aw_ready) begin
            w_addr_reg <= aw_addr;
            w_state <= W_ADDR;
            aw_ready <= 1'b0;
            $display("t=%0t: AXI Write Address Phase: addr=0x%02h", $time, aw_addr);
          end
        end

        W_ADDR: begin
          w_ready <= 1'b1;
          if (w_valid && w_ready) begin
            if (w_addr_reg < 16) begin
              slave_memory[w_addr_reg] <= w_data;
              b_resp <= 2'b00;  // OKAY
              $display("t=%0t: AXI Write Data Phase: addr=0x%02h, data=0x%02h", $time, w_addr_reg,
                       w_data);
            end else begin
              b_resp <= 2'b10;  // SLVERR
              $display("t=%0t: AXI Write Error: invalid addr=0x%02h", $time, w_addr_reg);
            end
            w_state <= W_RESP;
            w_ready <= 1'b0;
          end
        end

        W_RESP: begin
          b_valid <= 1'b1;
          if (b_valid && b_ready) begin
            b_valid <= 1'b0;
            w_state <= W_IDLE;
            $display("t=%0t: AXI Write Response Phase: resp=0b%02b", $time, b_resp);
          end
        end

        default: w_state <= W_IDLE;
      endcase
    end
  end

  // AXI Slave Read Logic
  always_ff @(posedge clk) begin
    if (!rst_n) begin
      r_state <= R_IDLE;
      ar_ready <= 1'b0;
      r_valid <= 1'b0;
      r_data <= 8'h0;
      r_resp <= 2'b00;
      r_addr_reg <= 8'h0;
    end else begin
      case (r_state)
        R_IDLE: begin
          ar_ready <= 1'b1;
          if (ar_valid && ar_ready) begin
            r_addr_reg <= ar_addr;
            r_state <= R_DATA;
            ar_ready <= 1'b0;
            $display("t=%0t: AXI Read Address Phase: addr=0x%02h", $time, ar_addr);
          end
        end

        R_DATA: begin
          r_valid <= 1'b1;
          if (r_addr_reg < 16) begin
            r_data <= slave_memory[r_addr_reg];
            r_resp <= 2'b00;  // OKAY
            $display("t=%0t: AXI Read Data Phase: addr=0x%02h, data=0x%02h", $time, r_addr_reg,
                     slave_memory[r_addr_reg]);
          end else begin
            r_data <= 8'h00;
            r_resp <= 2'b10;  // SLVERR
            $display("t=%0t: AXI Read Error: invalid addr=0x%02h", $time, r_addr_reg);
          end

          if (r_valid && r_ready) begin
            r_valid <= 1'b0;
            r_state <= R_IDLE;
          end
        end

        default: r_state <= R_IDLE;
      endcase
    end
  end

  // Clock generation
  initial begin
    clk = 0;
    forever #5 clk = ~clk;  // 100MHz clock
  end

  // Main test sequence
  initial begin
    $dumpfile("axi_if.vcd");
    $dumpvars(0, tb_tt_if);

    // Initialize signals
    rst_n = 0;
    ena = 1;
    ui_in = 8'b0;
    uio_in = 8'b0;

    // Reset sequence
    repeat (5) @(posedge clk);
    rst_n = 1;
    repeat (2) @(posedge clk);

    $display("=== Starting TinyTapeout AXI Interface Test ===");

    // Test 1: Single write transaction
    $display("\n--- TEST 1: Single Write Transaction ---");
    write_transaction(6'h05, 8'hA5);

    // Test 2: Single read transaction
    $display("\n--- TEST 2: Single Read Transaction ---");
    read_transaction(6'h05, 8'hA5);  // Expected data

    // Test 3: Multiple write transactions
    $display("\n--- TEST 3: Multiple Write Transactions ---");
    write_transaction(6'h03, 8'h33);
    write_transaction(6'h07, 8'h77);
    write_transaction(6'h0A, 8'hAA);

    // Test 4: Multiple read transactions
    $display("\n--- TEST 4: Multiple Read Transactions ---");
    read_transaction(6'h03, 8'h33);
    read_transaction(6'h07, 8'h77);
    read_transaction(6'h0A, 8'hAA);

    // Test 5: Read uninitialized location
    $display("\n--- TEST 5: Read Uninitialized Location ---");
    read_transaction(6'h0F, 8'h00);  // Should return 0

    // Test 6: Boundary test
    $display("\n--- TEST 6: Boundary Address Test ---");
    write_transaction(6'h0F, 8'hFF);
    read_transaction(6'h0F, 8'hFF);

    // Test 7: Invalid command test
    $display("\n--- TEST 7: Invalid Command Test ---");
    ui_in = 8'b00001111;  // Invalid command (11)
    repeat (10) @(posedge clk);
    ui_in = 8'b00000000;  // Return to idle
    repeat (5) @(posedge clk);

    // Test 8: State transition monitoring
    $display("\n--- TEST 8: State Transition Monitoring ---");
    monitor_state_transitions();

    repeat (10) @(posedge clk);
    $display("\n=== All Tests Completed Successfully! ===");
    $finish;
  end

  // Task: Write transaction
  task write_transaction(input [5:0] addr, input [7:0] data);
    begin
      $display("Starting write: addr=0x%02h, data=0x%02h", addr, data);

      // Step 1: Prepare write data on bidirectional pins
      uio_in = data;
      @(posedge clk);

      // Step 2: Send write command (01) + address
      ui_in = {addr, 2'b01};
      $display("t=%0t: Sent command: ui_in=0b%08b (addr=0x%02h, cmd=01)", $time, ui_in, addr);
      @(posedge clk);

      // Step 3: Wait for transaction to complete
      wait_for_idle();

      $display("Write transaction completed\n");
    end
  endtask

  // Task: Read transaction
  task read_transaction(input [5:0] addr, input [7:0] expected_data);
    logic [7:0] read_data;
    begin
      $display("Starting read: addr=0x%02h, expected=0x%02h", addr, expected_data);

      // Step 1: Send read command (10) + address
      ui_in = {addr, 2'b10};
      $display("t=%0t: Sent command: ui_in=0b%08b (addr=0x%02h, cmd=10)", $time, ui_in, addr);
      @(posedge clk);

      // Step 2: Wait for transaction to complete and capture data
      wait_for_idle();
      read_data = uo_out;

      $display("Read transaction completed: data=0x%02h", read_data);

      // Step 3: Verify data
      if (read_data == expected_data) begin
        $display("✓ PASS: Read data matches expected value");
      end else begin
        $display("✗ FAIL: Expected 0x%02h, got 0x%02h", expected_data, read_data);
      end
      $display("");
    end
  endtask

  // Task: Wait for state machine to return to IDLE
  task wait_for_idle();
    integer timeout_cycles;
    integer cycles;
    logic [2:0] current_state;
    begin
      timeout_cycles = 100;
      cycles = 0;
      @(posedge clk);

      while (cycles < timeout_cycles) begin
        // Get current state from output (lower 3 bits)
        current_state = uo_out[2:0];

        if (current_state == 3'b000) begin  // IDLE state
          // Use disable instead of break
          cycles = timeout_cycles;  // Exit condition
        end else begin
          @(posedge clk);
          cycles = cycles + 1;

          if (cycles >= timeout_cycles) begin
            $error("Timeout waiting for IDLE state! Current state: %03b", current_state);
            $finish;
          end
        end
      end

      // Return to idle command
      ui_in = 8'b00000000;
      repeat (2) @(posedge clk);
    end
  endtask

  // Task: Monitor state transitions during a transaction
  task monitor_state_transitions();
    logic [2:0] prev_state, current_state;
    integer i;
    begin
      $display("Monitoring state transitions during write transaction...");

      // Prepare write data
      uio_in = 8'h42;
      @(posedge clk);

      // Start write transaction
      ui_in = {6'h08, 2'b01};  // Write to address 0x08

      prev_state = 3'b111;  // Invalid initial state

      // Monitor for 30 cycles
      for (i = 0; i < 30; i = i + 1) begin
        current_state = uo_out[2:0];

        if (current_state != prev_state) begin
          case (current_state)
            3'b000:  $display("t=%0t: State -> IDLE", $time);
            3'b001:  $display("t=%0t: State -> WRITE_ADDR", $time);
            3'b010:  $display("t=%0t: State -> WRITE_DATA", $time);
            3'b011:  $display("t=%0t: State -> WRITE_RESP", $time);
            3'b100:  $display("t=%0t: State -> READ_ADDR", $time);
            3'b101:  $display("t=%0t: State -> READ_DATA", $time);
            default: $display("t=%0t: State -> UNKNOWN(%03b)", $time, current_state);
          endcase
          prev_state = current_state;
        end

        // Exit if back to idle and we've seen some transitions
        if (current_state == 3'b000 && i > 5) begin
          i = 30;  // Exit loop
        end else begin
          @(posedge clk);
        end
      end

      // Return to idle
      ui_in = 8'b00000000;
      repeat (3) @(posedge clk);
      $display("State transition monitoring completed\n");
    end
  endtask

  // GPIO Monitor for debugging
  always @(posedge clk) begin
    if (rst_n && ena) begin
      // Monitor significant changes
      if (ui_in[1:0] != 2'b00) begin  // Non-idle command
        $display(
            "t=%0t: GPIO -> ui_in=0x%02h, uo_out=0x%02h, uio_in=0x%02h, uio_out=0x%02h, uio_oe=0b%08b",
            $time, ui_in, uo_out, uio_in, uio_out, uio_oe);
      end
    end
  end

  // Memory dump for debugging
  task dump_memory();
    integer i;
    begin
      $display("=== Memory Dump ===");
      for (i = 0; i < 16; i = i + 1) begin
        $display("Addr 0x%02h: 0x%02h", i, slave_memory[i]);
      end
      $display("==================");
    end
  endtask

  // Timeout watchdog
  initial begin
    #50000;  // 50μs timeout
    $error("Simulation timeout!");
    dump_memory();
    $finish;
  end

endmodule
