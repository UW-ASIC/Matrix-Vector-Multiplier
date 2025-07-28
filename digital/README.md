## The Digital aspect of this project is represented in three seperate components

1. I2C_IF, accepts I2C commands for synchronous but out-of-order read/writes to the vector/matrix stored internally.

2. DAC_MUX, a digital handshake protocol to control an external analog input, and mux it exernally.

3. ADC_DEMUX, a digital handshake protocol to control an external analog output, and demux it externally.

### Diagram of the System with I2C_IF and Analog_MUX included

