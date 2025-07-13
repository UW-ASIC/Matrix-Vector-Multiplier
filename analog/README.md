## The Trelford

### Project Structure
- `schematics/ADC.sch` - Analog-to-Digital Converter schematic
- `schematics/DAC.sch` - Digital-to-Analog Converter schematic
- `schematics/CurrentSensor.sch` - Current sensing and amplification schematic
- `output/` - Digital logic output files
- `library/` - Shared schematics and symbols

### Build Instructions
refer to https://github.com/UW-ASIC/TinyTapeout_Flows for flow instructions

After completing the design:
```bash
cd ../flows
make CreateCaravel  # Generate Caravel/fab-friendly format
```

### Sub-Groups and Responsibilities

**ADC Team** (Matthew, Damir)
- Implement ADC to convert analog outputs Y₁ to Yₙ to digital values

**Current Sensor Team** (Omar, Matthew)  
- Implement trans-impedance amplifiers (TIA) to amplify matrix multiplication results

**DAC - Voltage Source Team** (Sam, Mounib)
- Implement DACs to output voltages representing vector entries X₁ to Xₘ

**DAC - Programmable Resistor Team** (Kareem, Kelly)
- Implement programmable resistors for matrix row entries

**Digital Logic Team** (Omar, Kelly)
- Interface and control logic for analog design

### References
- [Vector Matrix Multiplier on Field Programmable Analog Array](https://ieeexplore.ieee.org/document/5495508?denied=)
- [Analog Matrix Computing with Resistive Memory: Circuits and Theory](https://ieeexplore.ieee.org/document/9770998?denied=)
- [Verilog-A Tutorial](https://xschem.sourceforge.io/stefan/xschem_man/video_tutorials/verilog_a.mp4)
