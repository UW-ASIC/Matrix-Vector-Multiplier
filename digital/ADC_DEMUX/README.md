# DAC Router - Digital Control for Analog Routing

A pure digital component that acts as a **handshaking multiplexer controller** for routing analog signals without directly touching the analog data path.

## 🎯 Purpose

The DAC Router is a **digital switching controller** that coordinates between:
- **I2C Module** (provides target address)
- **DAC** (provides analog data)  
- **Analog Switch Array** (physical routing hardware)

**Key Point**: This module **never handles analog signals directly** - it only generates digital control signals for external analog switches.

## 🔄 Handshaking Protocol

### Input Handshake Signals
```systemverilog
input i_addr_ready     // I2C says "address is valid"
input i_dac_ack_in     // DAC says "data is stable"
input i_dac_data_valid // DAC says "output is ready"
```

### Output Control Signals  
```systemverilog
output o_ack_out           // Tell I2C "routing complete"
output o_dac_enable        // Tell DAC "start conversion"
output o_routing_valid     // Tell system "switches are set"
output [N-1:0] o_data_out  // One-hot switch control
```

## 🎛️ Digital Multiplexer Control

The router generates **one-hot encoded** switch control signals:

```
Address 5 selected:
o_data_out = 24'b000000000000000100000000
                              ↑
                         Only bit 5 is high
```

This digital pattern controls an **external analog switch array**:

```
Analog_Signal ─┬─ [Switch_0] ─ Output_0
               ├─ [Switch_1] ─ Output_1  
               ├─ [Switch_2] ─ Output_2
               ├─ [Switch_3] ─ Output_3
               ├─ [Switch_4] ─ Output_4
               ├─ [Switch_5] ─ Output_5  ← ENABLED
               └─ [Switch_N] ─ Output_N
                     ↑
               o_data_out[5] = 1
```

## ⏱️ State Machine Operation

### State Flow
```
IDLE → ROUTING → ACKNOWLEDGE → WAIT_CLEAR → IDLE
```

### Detailed Operation
1. **IDLE**: Wait for both `i_addr_ready` AND `i_dac_data_valid`
2. **ROUTING**: 
   - Enable `o_dac_enable` (start DAC)
   - Set `o_data_out[address] = 1` (enable one switch)
   - Wait for `i_dac_ack_in` (DAC confirms data stable)
3. **ACKNOWLEDGE**: 
   - Assert `o_ack_out` (tell I2C "done")
   - Keep switch enabled during handshake
4. **WAIT_CLEAR**: 
   - Clear all outputs
   - Wait for I2C to deassert `i_addr_ready`

## 🎚️ Switch Control Logic

### One-Hot Encoding
```systemverilog
// Only ONE switch enabled at a time
o_data_out = '0;  // Start with all switches OFF
if (addr_valid && latched_addr < TOTAL_OPTIONS) begin
    o_data_out[latched_addr] = 1'b1;  // Enable ONLY the target switch
end
```

### Address Bounds Checking
```systemverilog
// Safety: Prevent invalid addressing
if (i_addr_out >= TOTAL_OPTIONS) begin
    // Log error, don't enable any switches
    o_data_out = '0;
end
```

## 🔌 External Analog Switch Interface

The router controls **external hardware** like this:

### NMOS Switch Array
```verilog
// External analog hardware (not in this module)
module analog_switch_array (
    input analog_signal,           // From DAC
    input [23:0] switch_control,   // From DAC_Router.o_data_out
    output [23:0] routed_outputs   // To storage capacitors
);

genvar i;
generate
    for (i = 0; i < 24; i++) begin
        nmos switch_i (
            .drain(routed_outputs[i]),
            .source(analog_signal), 
            .gate(switch_control[i])    // ← DAC_Router controls this
        );
    end
endgenerate
endmodule
```

## 🤝 Interface Coordination

### With I2C Module
```
I2C: "Store value at address 7"
│
├─ i_addr_out = 7
├─ i_addr_ready = 1
│
Router: "Acknowledged, routing to address 7"
│
├─ o_data_out[7] = 1 (all others = 0)
├─ o_ack_out = 1
```

### With DAC
```
Router: "Please convert next value"
│
├─ o_dac_enable = 1
│
DAC: "Conversion complete, output stable"
│
├─ i_dac_ack_in = 1
├─ i_dac_data_valid = 1
```

## 🎯 Key Design Principles

### 1. **Digital-Only Controller**
- **No analog signals** pass through this module
- **Pure digital logic** for maximum reliability
- **Clock-synchronous** operation for predictable timing

### 2. **Handshaking Multiplexer**
- **Waits for all parties** before enabling switches
- **Atomic operations** - either fully routed or not at all
- **Clean handoffs** between I2C, DAC, and analog hardware

### 3. **Safety First**
- **One-hot encoding** prevents multiple switches enabled
- **Address bounds checking** prevents invalid routing
- **Default-off state** when not actively routing

### 4. **Analog Isolation**
- **No direct analog paths** through digital logic
- **Clean control signals** minimize switching noise
- **Predictable timing** for stable analog operations

## 📊 Timing Diagram

```
Clock      ___/‾\___/‾\___/‾\___/‾\___/‾\___/‾\___
i_addr_ready    ‾‾‾‾‾‾‾‾‾‾‾‾\_____________
i_dac_valid     ____/‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\____
o_data_out[5]   ________/‾‾‾‾‾‾‾‾‾‾‾‾\_____
o_ack_out       ____________/‾‾‾‾‾\________

State:     IDLE  ROUTING  ACK  WAIT  IDLE
```

## 🔧 Usage Example

```systemverilog
// Instantiate the router
DAC_Router #(.VECTOR_SIZE(4)) router (
    .i_clk(clk),
    .i_rst_n(rst_n),
    
    // From I2C
    .i_addr_out(i2c_target_addr),
    .i_addr_ready(i2c_addr_valid),
    .o_ack_out(routing_complete),
    
    // From/To DAC  
    .i_dac_ack_in(dac_conversion_done),
    .i_dac_data_valid(dac_output_ready),
    .o_dac_enable(start_dac_conversion),
    
    // To external analog switches
    .o_data_out(switch_control_signals),  // 24-bit one-hot
    .o_routing_valid(switches_are_set)
);

// Connect to external analog switch array
analog_switch_array switches (
    .analog_signal(dac_analog_output),
    .switch_control(switch_control_signals),  // From router
    .routed_outputs(storage_capacitor_inputs)
);
```

---

**Summary**: The DAC Router is a **pure digital handshaking controller** that coordinates timing between I2C, DAC, and analog switches without ever touching the analog signal itself. It's essentially a **smart address decoder with handshaking** that ensures reliable analog signal routing.
