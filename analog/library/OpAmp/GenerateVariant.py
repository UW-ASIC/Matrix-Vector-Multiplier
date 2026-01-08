#!/usr/bin/env python3
"""
GenerateVariant.py - Generate OpAmp variants with specified parameters

This script generates two-stage Miller-compensated operational amplifier variants
for the Sky130 PDK using either square-law or gm/Id methodology.

Usage:
    python GenerateVariant.py --gbw 10 --slew_rate 10 --c_load 1.0 --variant default
    python GenerateVariant.py --gbw 50 --slew_rate 20 --method gmid --variant high_speed
"""

import argparse
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Dict

# Import the sizing functions from the original sizing module
try:
    from sizing_lib import (
        Specifications,
        SquareLawParams,
        DesignChoices,
        design_square_law,
        design_gmid,
        SKY130_MIN_L,
        LOOKUP_DIR,
    )
except ImportError:
    print("Error: Could not import sizing_lib module")
    print("The sizing functions have been moved to sizing_lib.py")
    sys.exit(1)


def validate_parameters(args):
    """Validate input parameters"""
    errors = []
    
    if args.gbw <= 0:
        errors.append("GBW must be positive")
    if args.slew_rate <= 0:
        errors.append("Slew rate must be positive")
    if args.c_load <= 0:
        errors.append("Load capacitance must be positive")
    if args.vdd <= 0:
        errors.append("Supply voltage must be positive")
    if not (0 <= args.phase_margin <= 90):
        errors.append("Phase margin must be between 0 and 90 degrees")
    
    if errors:
        for error in errors:
            print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)


def generate_variant(args):
    """Generate OpAmp variant with specified parameters"""
    
    print(f"\n{'='*70}")
    print(f"Generating OpAmp Variant: {args.variant}")
    print(f"{'='*70}\n")
    
    # Create specifications
    specs = Specifications(
        gbw=args.gbw,
        phase_margin=args.phase_margin,
        slew_rate=args.slew_rate,
        c_load=args.c_load,
        vdd=args.vdd,
        vss=0.0,
    )
    
    # Process parameters (Sky130 defaults)
    process = SquareLawParams()
    
    # Design choices (use defaults or custom if provided)
    choices = DesignChoices(
        l_m1=args.l_m1,
        l_m3=args.l_m3,
        l_m5=args.l_m5,
        l_m6=args.l_m6,
        l_m7=args.l_m7,
    )
    
    # Run the appropriate design method
    if args.method == "square_law":
        results = design_square_law(specs, process, choices)
    elif args.method == "gmid":
        results = design_gmid(
            specs, process, choices,
            lookup_dir=args.lookup_dir,
            vds_nmos=0.9,
            vds_pmos=-0.9
        )
    else:
        print(f"Error: Unknown method '{args.method}'", file=sys.stderr)
        sys.exit(1)
    
    # Create variant directory
    variant_dir = Path(args.variant)
    variant_dir.mkdir(exist_ok=True)
    
    # Create subdirectories
    (variant_dir / "schematics").mkdir(exist_ok=True)
    (variant_dir / "symbols").mkdir(exist_ok=True)
    (variant_dir / "testbenches").mkdir(exist_ok=True)
    
    # Save sizing results
    sizing_file = variant_dir / "sizing_results.txt"
    with open(sizing_file, 'w') as f:
        f.write(f"OpAmp Variant: {args.variant}\n")
        f.write(f"{'='*70}\n\n")
        f.write(f"Specifications:\n")
        f.write(f"  GBW: {specs.gbw} MHz\n")
        f.write(f"  Phase Margin: {specs.phase_margin}°\n")
        f.write(f"  Slew Rate: {specs.slew_rate} V/μs\n")
        f.write(f"  Load Capacitance: {specs.c_load} pF\n")
        f.write(f"  Supply Voltage: {specs.vdd} V\n\n")
        
        f.write(f"Transistor Sizing (μm):\n")
        f.write(f"{'='*70}\n")
        for name in ["M1", "M2", "M3", "M4", "M5", "M6", "M7"]:
            m = results[name]
            f.write(f"{name}: W={m['W']:.3f}μm, L={m['L']:.3f}μm, W/L={m['W/L']:.2f}\n")
        
        f.write(f"\nCompensation Capacitor: {results['Cc']:.3f} pF\n\n")
        
        f.write(f"Performance:\n")
        f.write(f"{'='*70}\n")
        perf = results['Performance']
        for key, val in perf.items():
            f.write(f"  {key}: {val:.2f}\n")
    
    print(f"\n✓ Variant '{args.variant}' generated successfully")
    print(f"  Directory: {variant_dir}/")
    print(f"  Sizing results: {sizing_file}")
    print(f"\nNote: Schematics and symbols need to be created manually in:")
    print(f"  - {variant_dir}/schematics/")
    print(f"  - {variant_dir}/symbols/")
    print(f"  - {variant_dir}/testbenches/")
    

def main():
    parser = argparse.ArgumentParser(
        description="Generate OpAmp variants for Sky130 PDK",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Required parameters
    parser.add_argument(
        "--gbw",
        type=float,
        required=True,
        help="Unity gain bandwidth in MHz"
    )
    parser.add_argument(
        "--slew_rate",
        type=float,
        required=True,
        help="Slew rate in V/μs"
    )
    parser.add_argument(
        "--c_load",
        type=float,
        required=True,
        help="Load capacitance in pF"
    )
    
    # Optional parameters
    parser.add_argument(
        "--variant",
        type=str,
        default="default",
        help="Variant name (creates subdirectory)"
    )
    parser.add_argument(
        "--method",
        type=str,
        choices=["square_law", "gmid"],
        default="square_law",
        help="Design methodology"
    )
    parser.add_argument(
        "--vdd",
        type=float,
        default=1.8,
        help="Supply voltage in V"
    )
    parser.add_argument(
        "--phase_margin",
        type=float,
        default=60,
        help="Target phase margin in degrees"
    )
    
    # Channel lengths
    parser.add_argument(
        "--l_m1",
        type=float,
        default=0.5,
        help="Input pair transistor length in μm"
    )
    parser.add_argument(
        "--l_m3",
        type=float,
        default=1.0,
        help="Active load transistor length in μm"
    )
    parser.add_argument(
        "--l_m5",
        type=float,
        default=1.0,
        help="Tail source transistor length in μm"
    )
    parser.add_argument(
        "--l_m6",
        type=float,
        default=0.5,
        help="Output driver transistor length in μm"
    )
    parser.add_argument(
        "--l_m7",
        type=float,
        default=1.0,
        help="Output sink transistor length in μm"
    )
    
    # gm/Id specific
    parser.add_argument(
        "--lookup_dir",
        type=str,
        default=LOOKUP_DIR,
        help="Directory containing Sky130 lookup tables (for gm/Id method)"
    )
    
    args = parser.parse_args()
    
    # Validate parameters
    validate_parameters(args)
    
    # Generate variant
    generate_variant(args)


if __name__ == "__main__":
    main()
