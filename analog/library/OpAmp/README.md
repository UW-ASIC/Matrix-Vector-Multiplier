## OpAmp (Operational Amplifier)

Two-stage Miller-compensated operational amplifier designed for the Sky130 PDK. Supports programmatic variant generation with customizable specifications.

### Specifications (Default Variant)

- **GBW**: 10 MHz (configurable)
- **Phase Margin**: 60° (target)
- **Slew Rate**: 10 V/μs
- **Load Capacitance**: 1 pF
- **Supply Voltage**: 1.8 V
- **Power**: ~50 μW (typical, varies by variant)

### Generating Variants

Use `GenerateVariant.py` to create OpAmp variants with different performance specifications:

```bash
# Low power variant (lower GBW, lower current)
python GenerateVariant.py --gbw 5 --slew_rate 5 --c_load 1.0 --variant low_power

# High speed variant (higher GBW, higher current)
python GenerateVariant.py --gbw 50 --slew_rate 20 --c_load 1.0 --variant high_speed

# Custom variant with gm/Id method (more accurate)
python GenerateVariant.py --gbw 20 --slew_rate 15 --c_load 2.0 --method gmid --variant custom
```

### Parameters

#### Required Parameters

| Parameter | Type | Description | Units |
|-----------|------|-------------|-------|
| `--gbw` | float | Unity gain bandwidth | MHz |
| `--slew_rate` | float | Slew rate | V/μs |
| `--c_load` | float | Load capacitance | pF |

#### Optional Parameters

| Parameter | Type | Description | Default | Units |
|-----------|------|-------------|---------|-------|
| `--variant` | str | Variant name (subdirectory) | `default` | - |
| `--method` | str | Design method: `square_law` or `gmid` | `square_law` | - |
| `--vdd` | float | Supply voltage | `1.8` | V |
| `--phase_margin` | float | Target phase margin | `60` | degrees |
| `--l_m1` | float | Input pair transistor length | `0.5` | μm |
| `--l_m3` | float | Active load transistor length | `1.0` | μm |
| `--l_m5` | float | Tail source transistor length | `1.0` | μm |
| `--l_m6` | float | Output driver transistor length | `0.5` | μm |
| `--l_m7` | float | Output sink transistor length | `1.0` | μm |
| `--lookup_dir` | str | Lookup table directory (for gm/Id) | `../tools/scripts/GMID/sky130_lookup_tables` | - |

### Design Methodology

This module supports two design methodologies:

1. **Square-Law** (default): Fast analytical design using simplified transistor equations
   - Good for initial sizing and exploration
   - No external dependencies required
   
2. **gm/Id Method**: Accurate design using Sky130 characterization data
   - Requires lookup tables (generate with `tools/scripts/GMID/lookup.py`)
   - Requires `mosplot` package: `pip install mosplot`
   - More accurate for short-channel effects

### Output Structure

Running `GenerateVariant.py` creates a subdirectory with the variant name:

```
variant_name/
├── sizing_results.txt    # Calculated transistor dimensions and performance
├── schematics/           # Empty directory for XSchem schematics
├── symbols/              # Empty directory for symbols
└── testbenches/          # Empty directory for testbenches
```

After generation, manually create the schematics using the dimensions from `sizing_results.txt`.

### Dependencies

- **Python 3.x**: numpy, dataclasses
- **gm/Id method only**: `mosplot` package (`pip install mosplot`)
- **gm/Id method only**: Sky130 lookup tables (generate using `tools/scripts/GMID/lookup.py`)

### Example Workflow

```bash
# Generate a high-speed variant
python GenerateVariant.py --gbw 100 --slew_rate 50 --c_load 0.5 --variant high_speed_100MHz

# Check the sizing results
cat high_speed_100MHz/sizing_results.txt

# Open XSchem and create the schematic using the calculated dimensions
xschem &
# Create schematic in high_speed_100MHz/schematics/ using sizes from sizing_results.txt
```

### Help

For complete parameter documentation:
```bash
python GenerateVariant.py --help
```
