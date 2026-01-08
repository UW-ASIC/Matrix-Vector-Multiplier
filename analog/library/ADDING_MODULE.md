# Adding a New Module to the Analog Library

This document provides guidelines for adding a new analog module to the UWASIC analog library.

## Directory Structure

Each module should follow this structure:

```
ModuleName/
├── README.md                  # Module documentation (REQUIRED)
├── GenerateVariant.py         # Python variant generator (OPTIONAL)
├── VariantName1/              # Specific variant/implementation
│   ├── schematics/            # XSchem schematics
│   │   ├── component.sch
│   │   └── ...
│   ├── symbols/               # XSchem symbols
│   │   ├── component.sym
│   │   └── ...
│   └── testbenches/           # Testbench schematics (optional)
│       ├── component_tb.sch
│       └── ...
├── VariantName2/              # Another variant (if applicable)
│   └── ...
└── schematics/                # Alternative: Direct schematics if no variants
    └── ...
```

### Example: Existing Modules

**AnalogMux/** (Direct schematics):
```
AnalogMux/
├── README.md
├── schematics/          # Direct schematic files
│   ├── analog_mux.sch
│   ├── Aswitch.sch
│   └── ...
└── symbols/
    ├── analog_mux.sym
    └── ...
```

**DAC/** (Variant-based):
```
DAC/
├── README.md
└── Custom/              # Variant subdirectory
    ├── schematics/
    ├── symbols/
    └── testbenches/
```

---

## README.md Requirements

Each module **must** include a `README.md` file in its root directory. This README will be automatically aggregated into the top-level library README.

Your module README should include:

### Required Sections

1. **Module name and brief description**
2. **Key specifications** (voltage, current, performance metrics)
3. **Variants** (if applicable - list available variants and their differences)
4. **Usage instructions** (how to use the schematic or generate variants)
5. **Parameters** (if using GenerateVariant.py - document all required parameters)
6. **Dependencies** (required tools, PDK versions, etc.)

### Example README Template

```markdown
## ModuleName

Brief description of what this module does and its key features.

### Specifications

- Supply Voltage: X V
- Input Range: Y V
- Output Range: Z V
- Power Consumption: W μW
- Technology: Sky130 PDK

### Available Variants

- **VariantName1**: Description of this variant (use case, trade-offs)
- **VariantName2**: Description of this variant

### Usage

#### Direct Use
Open the schematic in XSchem:
\`\`\`bash
xschem schematics/component.sch
\`\`\`

#### Generating Variants (if applicable)
\`\`\`bash
python GenerateVariant.py --param1 value1 --param2 value2
\`\`\`

### Parameters (if using GenerateVariant.py)

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| param1    | int  | Description | value   |
| param2    | float| Description | value   |

### Dependencies

- XSchem
- Sky130 PDK
- (Other dependencies as needed)
```

---

## GenerateVariant.py (Optional)

If your module supports **programmatic variant generation**, include a `GenerateVariant.py` script in the module root.

### Purpose

The script automates the creation of different variants of the same component with different parameters or configurations.

### Requirements

1. **Clear parameter specification**: Document all required and optional parameters
2. **Help message**: Implement `--help` to show usage
3. **Parameter validation**: Validate user inputs before generating
4. **Output organization**: Generate variants in organized subdirectories

### Example Structure

```python
#!/usr/bin/env python3
"""
GenerateVariant.py - Generate variants of ModuleName component

Usage:
    python GenerateVariant.py --width 10 --length 0.5 --variant low_power
"""

import argparse
from pathlib import Path

def generate_variant(width: float, length: float, variant_name: str):
    """Generate a variant with specified parameters"""
    # Create variant directory
    variant_dir = Path(variant_name)
    variant_dir.mkdir(exist_ok=True)
    
    # Generate schematics, symbols, etc.
    # ... implementation ...
    
    print(f"✓ Generated variant '{variant_name}' with W={width}μm, L={length}μm")

def main():
    parser = argparse.ArgumentParser(
        description="Generate ModuleName variants"
    )
    
    # Required parameters
    parser.add_argument("--width", type=float, required=True,
                       help="Transistor width in μm")
    parser.add_argument("--length", type=float, required=True,
                       help="Transistor length in μm")
    
    # Optional parameters
    parser.add_argument("--variant", type=str, default="default",
                       help="Variant name (default: default)")
    
    args = parser.parse_args()
    
    # Validate parameters
    if args.width <= 0 or args.length <= 0:
        parser.error("Width and length must be positive")
    
    generate_variant(args.width, args.length, args.variant)

if __name__ == "__main__":
    main()
```

### Documentation in README

When using `GenerateVariant.py`, your README **must** document:

1. **All parameters**: Name, type, description, default value, valid range
2. **Example commands**: Show how to generate common variants
3. **Output structure**: Explain what files/directories are created
4. **Prerequisites**: Any dependencies or setup required

Example:
```markdown
### Generating Variants

\`\`\`bash
# Generate low-power variant
python GenerateVariant.py --width 5 --length 1.0 --variant low_power

# Generate high-speed variant
python GenerateVariant.py --width 20 --length 0.5 --variant high_speed
\`\`\`

This creates subdirectories:
- \`low_power/schematics/\`
- \`high_speed/schematics/\`
Each containing the generated schematics and symbols.
```

---

## File Organization

### Schematics and Symbols

Store XSchem files in organized subdirectories:

- **schematics/**: Main schematic files (`.sch`)
- **symbols/**: Symbol files (`.sym`) for hierarchical use
- **testbenches/**: Testbench schematics (optional but recommended)

### Naming Conventions

- **Module directory**: PascalCase (e.g., `OpAmp`, `AnalogMux`, `TransImpedanceAmplifier`)
- **Variant subdirectories**: PascalCase or descriptive (e.g., `Custom`, `SAR`, `HighSpeed`)
- **Python files**: PascalCase for generators (e.g., `GenerateVariant.py`)
- **Schematic files**: snake_case or descriptive (e.g., `analog_mux.sch`, `Aswitch.sch`)

---

## Automatic README Generation

> **Important**: The top-level `README.md` is **auto-generated**. Do not edit it manually.

When you push changes to your module's README:
1. GitHub Actions automatically runs `UpdateReadME.py`
2. Your module README is aggregated into the top-level README
3. The updated top-level README is committed back to the repository

---

## Checklist for New Modules

Before submitting your module:

- [ ] Created module directory with proper naming
- [ ] Added comprehensive `README.md` with all required sections
- [ ] Organized schematics in `schematics/` directory (or variant subdirectories)
- [ ] Organized symbols in `symbols/` directory
- [ ] (Recommended) Added testbenches in `testbenches/` directory
- [ ] (If applicable) Created `GenerateVariant.py` with clear parameter documentation
- [ ] (If using GenerateVariant.py) Documented all parameters in README
- [ ] Verified schematic files open correctly in XSchem
- [ ] Committed and pushed changes
- [ ] Verified top-level README was auto-updated via GitHub Actions

---

## Common Patterns

### Pattern 1: Simple Module (No Variants)

```
ModuleName/
├── README.md
├── schematics/
│   └── component.sch
└── symbols/
    └── component.sym
```

### Pattern 2: Multiple Variants (Manual)

```
ModuleName/
├── README.md
├── VariantA/
│   ├── schematics/
│   └── symbols/
└── VariantB/
    ├── schematics/
    └── symbols/
```

### Pattern 3: Programmatic Variants

```
ModuleName/
├── README.md
├── GenerateVariant.py
├── LowPower/         # Generated
│   ├── schematics/
│   └── symbols/
└── HighSpeed/        # Generated
    ├── schematics/
    └── symbols/
```

---

## Questions?

If you have questions about module structure or conventions, refer to existing modules:
- **AnalogMux/**: Example of direct schematic organization
- **DAC/**: Example of variant-based organization
- **ADC/SAR/**: Example of nested variant structure
