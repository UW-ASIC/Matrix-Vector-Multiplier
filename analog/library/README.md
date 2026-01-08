### Official Analog Library for UWASIC

This repository exists as the official library that UWASIC's analog team will be using.

> **Note**: This README is auto-generated. Module information is aggregated from individual module READMEs.
> To update this file, modify the respective module's README.md and push your changes.

---

## Modules

### ADC

*Documentation coming soon...*

### AnalogMux

*Documentation coming soon...*

### DAC

*Documentation coming soon...*

### OpAmp

## OpAmp (Operational Amplifier)

Two-stage Miller-compensated operational amplifier designed for the Sky130 PDK.

### Specifications

- **GBW**: 10 MHz (configurable)
- **Phase Margin**: 60° (target)
- **Slew Rate**: 10 V/μs
- **Load Capacitance**: 1 pF
- **Supply Voltage**: 1.8 V
- **Power**: ~50 μW (typical)

### Design Methodology

This module uses both **square-law** and **gm/Id** design methodologies:

- **Square-law**: Quick analytical design using hand calculations
- **gm/Id**: More accurate design using Sky130 lookup tables

The sizing script (`sizing.py`) implements both methods and outputs transistor dimensions ready for schematic generation.

### Usage

```python
from OpAmp.sizing import get_sizing, Specifications, DesignChoices

# Define your specifications
specs = Specifications(
    gbw=10.0,        # MHz
    slew_rate=10.0,  # V/μs
    c_load=1.0       # pF
)

# Get sizing using square-law method
results = get_sizing(method="square_law", specs=specs)

# Or use gm/Id method (requires lookup tables)
# results = get_sizing(method="gmid", specs=specs)
```

### Dependencies

- **Python**: numpy, dataclasses
- **gm/Id method**: mosplot package (`pip install mosplot`)
- **Lookup tables**: Sky130 lookup tables (generate using `tools/scripts/GMID/lookup.py`)

### Testing

```bash
cd OpAmp
python sizing.py          # Run example sizing
python test_sizing.py     # Run unit tests
```

### Template Files

- `template/OpAmp.sch` - Two-stage Miller-compensated op-amp schematic
- `template/OpAmp.sym` - Symbol for hierarchical designs
- `template/OpAmp_tb.sch` - AC/transient/DC testbench

### TIAs

*Documentation coming soon...*


---


## Tools


*Tools documentation coming soon...*
