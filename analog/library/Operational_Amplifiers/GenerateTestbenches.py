#!/usr/bin/env python3
"""
Automated Op-Amp Characterization Script
Generates and runs SPICE simulations for multiple op-amp designs
"""

import os
import glob
import subprocess
import re
import csv
from pathlib import Path

class OpAmpCharacterizer:
    def __init__(self, template_file="opamp_template.cir", results_dir="results"):
        self.template_file = template_file
        self.results_dir = results_dir
        self.results = []
        
        # Create results directory
        os.makedirs(results_dir, exist_ok=True)
        
        # Template SPICE file content
        self.template_content = """* Op-Amp Characterization Template
* This file will be automatically modified for each design

.lib /usr/local/share/pdk/sky130A/libs.tech/ngspice/sky130.lib.spice tt

* Include the op-amp netlist (WILL BE REPLACED)
.include "{netlist_file}"

* ========================================
* TEST 1: DIFFERENTIAL GAIN
* ========================================
.subckt test_diff_gain vip vin vout vdd vss
X_dut vip vin vout vdd vss {opamp_name}
.ends

Xtest1 inp inn out vdd vss test_diff_gain
Vdd vdd 0 DC 1.8
Vss vss 0 DC 0
Vdm inp inn DC 0 AC 1m
Vcm inp 0 DC 0.9

.op
.ac dec 20 1 10G
.measure ac diff_gain_db MAX vdb(out)
.measure ac gbw WHEN vdb(out)=0

* ========================================
* TEST 2: CMRR
* ========================================
.subckt test_cmrr vip vin vout vdd vss
X_dut2 vip vin vout vdd vss {opamp_name}
.ends

Xtest2 inp2 inn2 out2 vdd vss test_cmrr
Vcm_test inp2 inn2 DC 0.9 AC 1
Vdd vdd 0 DC 1.8
Vss vss 0 DC 0

* ========================================
* TEST 3: PHASE MARGIN
* ========================================
.subckt test_stability vin vout vdd vss
X_dut3 vout vin vout vdd vss {opamp_name}
.ends

Xtest3 in3 out3 vdd vss test_stability
Vin3 in3 0 DC 0.9 AC 1m
Vdd vdd 0 DC 1.8
Vss vss 0 DC 0

* ========================================
* TEST 4: SLEW RATE
* ========================================
.subckt test_slew_rate vin vout vdd vss
X_dut4 vin 0 vout vdd vss {opamp_name}
Rf vout vin 1k
.ends

Xtest4 in4 out4 vdd vss test_slew_rate
Vin4 in4 0 PULSE(0 1.8 1n 1p 1p 10n 20n)
Vdd vdd 0 DC 1.8
Vss vss 0 DC 0

* ========================================
* TEST 5: POWER DISSIPATION  
* ========================================
.subckt test_power vin vout vdd vss
X_dut5 vin 0 vout vdd vss {opamp_name}
Rf vout vin 100k
Rl vout 0 1k
.ends

Xtest5 in5 out5 vdd vss test_power
Vin5 in5 0 DC 0 SIN(0 0.5m 10k)
Vdd vdd 0 DC 1.8  
Vss vss 0 DC 0

* ========================================
* CONTROL SECTION
* ========================================
.control
set color0=white
set color1=black

echo "Characterizing: {opamp_name}"

* Test 1: Differential Gain
echo "Running Differential Gain Test..."
ac dec 20 1 10G
let gain_linear = db(out)
let gain_db = vdb(out)
meas ac diff_gain_db MAX gain_db
meas ac gbw WHEN gain_db=0
wrdata {results_dir}/{opamp_name}_gain.txt gain_db frequency

* Test 2: CMRR
echo "Running CMRR Test..."
ac dec 20 1 1MEG  
let cmrr_db = vdb(out2)
meas ac cmrr find cmrr_db at=1k
wrdata {results_dir}/{opamp_name}_cmrr.txt cmrr_db frequency

* Test 3: Phase Margin
echo "Running Phase Margin Test..."
ac dec 20 1 10G
let phase_deg = 180*vp(out3)/pi
meas ac unity_freq WHEN vdb(out3)=0
meas ac phase_at_unity find phase_deg WHEN vdb(out3)=0  
let phase_margin = 180 + phase_at_unity
wrdata {results_dir}/{opamp_name}_phase.txt vdb(out3) phase_deg frequency

* Test 4: Slew Rate
echo "Running Slew Rate Test..."
tran 1p 50n
meas tran v_10pct find v(out4) WHEN time=5n
meas tran v_90pct find v(out4) WHEN time=15n  
meas tran t_10pct WHEN v(out4)=0.18 RISE=1
meas tran t_90pct WHEN v(out4)=1.62 RISE=1
let slew_rate = (v_90pct-v_10pct)/(t_90pct-t_10pct)
wrdata {results_dir}/{opamp_name}_slew.txt v(in4) v(out4) time

* Test 5: Power
echo "Running Power Test..."  
tran 1u 1m
meas tran avg_power AVG p(Vdd) FROM=0.1m TO=1m
wrdata {results_dir}/{opamp_name}_power.txt v(in5) v(out5) p(Vdd) time

* Write summary results
echo "Summary Results for {opamp_name}:" > {results_dir}/{opamp_name}_summary.txt
echo "Differential Gain: " diff_gain_db " dB" >> {results_dir}/{opamp_name}_summary.txt
echo "GBW: " gbw " Hz" >> {results_dir}/{opamp_name}_summary.txt  
echo "CMRR: " cmrr " dB" >> {results_dir}/{opamp_name}_summary.txt
echo "Phase Margin: " phase_margin " degrees" >> {results_dir}/{opamp_name}_summary.txt
echo "Slew Rate: " slew_rate " V/s" >> {results_dir}/{opamp_name}_summary.txt
echo "Power: " avg_power " W" >> {results_dir}/{opamp_name}_summary.txt

quit
.endc

.end
"""

    def find_opamp_files(self, directory="."):
        """Find all SPICE netlist files in directory"""
        patterns = ["*.spice", "*.sp", "*.cir", "*.net"]
        files = []
        
        for pattern in patterns:
            files.extend(glob.glob(os.path.join(directory, pattern)))
            
        return files

    def extract_subckt_name(self, netlist_file):
        """Extract the main subcircuit name from SPICE file"""
        try:
            with open(netlist_file, 'r') as f:
                content = f.read()
                
            # Look for .subckt definitions
            subckt_matches = re.findall(r'\.subckt\s+(\w+)', content, re.IGNORECASE)
            
            if subckt_matches:
                # Return the first subcircuit (usually the main one)
                return subckt_matches[0]
            else:
                # If no subckt found, use filename without extension
                return Path(netlist_file).stem
                
        except Exception as e:
            print(f"Error reading {netlist_file}: {e}")
            return Path(netlist_file).stem

    def generate_test_file(self, netlist_file, opamp_name, output_file):
        """Generate test SPICE file for specific op-amp"""
        
        content = self.template_content.format(
            netlist_file=os.path.abspath(netlist_file),
            opamp_name=opamp_name,
            results_dir=self.results_dir
        )
        
        with open(output_file, 'w') as f:
            f.write(content)
            
        print(f"Generated test file: {output_file}")

    def run_simulation(self, test_file):
        """Run NGspice simulation"""
        print(f"Running simulation: {test_file}")
        
        try:
            # Run ngspice in batch mode
            result = subprocess.run(
                ['ngspice', '-b', test_file],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                print(f"✓ Simulation completed successfully")
                return True, result.stdout
            else:
                print(f"✗ Simulation failed:")
                print(f"STDOUT: {result.stdout}")
                print(f"STDERR: {result.stderr}")
                return False, result.stderr
                
        except subprocess.TimeoutExpired:
            print(f"✗ Simulation timed out")
            return False, "Timeout"
        except Exception as e:
            print(f"✗ Error running simulation: {e}")
            return False, str(e)

    def parse_results(self, opamp_name):
        """Parse simulation results from output files"""
        summary_file = os.path.join(self.results_dir, f"{opamp_name}_summary.txt")
        
        results = {
            'name': opamp_name,
            'diff_gain_db': 'N/A',
            'gbw_hz': 'N/A', 
            'cmrr_db': 'N/A',
            'phase_margin_deg': 'N/A',
            'slew_rate_v_per_s': 'N/A',
            'power_w': 'N/A'
        }
        
        if os.path.exists(summary_file):
            try:
                with open(summary_file, 'r') as f:
                    content = f.read()
                    
                # Extract values using regex
                patterns = {
                    'diff_gain_db': r'Differential Gain:\s+([\d\.-]+)',
                    'gbw_hz': r'GBW:\s+([\d\.-e\+]+)',
                    'cmrr_db': r'CMRR:\s+([\d\.-]+)',
                    'phase_margin_deg': r'Phase Margin:\s+([\d\.-]+)',
                    'slew_rate_v_per_s': r'Slew Rate:\s+([\d\.-e\+]+)',
                    'power_w': r'Power:\s+([\d\.-e\+]+)'
                }
                
                for key, pattern in patterns.items():
                    match = re.search(pattern, content)
                    if match:
                        results[key] = match.group(1)
                        
            except Exception as e:
                print(f"Error parsing results for {opamp_name}: {e}")
                
        return results

    def run_characterization(self, directory=".", file_pattern="*.spice"):
        """Run complete characterization suite"""
        
        print("🔍 Finding op-amp netlists...")
        netlist_files = self.find_opamp_files(directory)
        
        if not netlist_files:
            print(f"No netlist files found in {directory}")
            return
            
        print(f"Found {len(netlist_files)} netlist files:")
        for f in netlist_files:
            print(f"  - {f}")
            
        print(f"\n🚀 Starting characterization...")
        
        for netlist_file in netlist_files:
            print(f"\n{'='*60}")
            print(f"Processing: {netlist_file}")
            print(f"{'='*60}")
            
            # Extract op-amp name
            opamp_name = self.extract_subckt_name(netlist_file)
            print(f"Op-Amp subcircuit: {opamp_name}")
            
            # Generate test file
            test_file = f"test_{opamp_name}.cir"
            self.generate_test_file(netlist_file, opamp_name, test_file)
            
            # Run simulation
            success, output = self.run_simulation(test_file)
            
            if success:
                # Parse results
                results = self.parse_results(opamp_name)
                self.results.append(results)
                print(f"✓ Results saved for {opamp_name}")
            else:
                print(f"✗ Simulation failed for {opamp_name}")
                # Still add to results with error status
                self.results.append({
                    'name': opamp_name,
                    'error': output,
                    'diff_gain_db': 'ERROR',
                    'gbw_hz': 'ERROR',
                    'cmrr_db': 'ERROR', 
                    'phase_margin_deg': 'ERROR',
                    'slew_rate_v_per_s': 'ERROR',
                    'power_w': 'ERROR'
                })
                
            # Clean up test file
            if os.path.exists(test_file):
                os.remove(test_file)

    def generate_report(self, output_file="characterization_report.csv"):
        """Generate CSV report with all results"""
        
        if not self.results:
            print("No results to report")
            return
            
        # Write CSV file
        fieldnames = ['name', 'diff_gain_db', 'gbw_hz', 'cmrr_db', 
                     'phase_margin_deg', 'slew_rate_v_per_s', 'power_w']
        
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in self.results:
                # Only write the main fields, skip error field if present
                row = {k: result.get(k, 'N/A') for k in fieldnames}
                writer.writerow(row)
                
        print(f"\n📊 Report generated: {output_file}")
        
        # Print summary table
        print(f"\n{'='*80}")
        print(f"CHARACTERIZATION SUMMARY")
        print(f"{'='*80}")
        print(f"{'Name':<20} {'Gain(dB)':<10} {'GBW(Hz)':<12} {'CMRR(dB)':<10} {'PM(°)':<8} {'SR(V/s)':<12} {'Power(W)':<12}")
        print(f"{'-'*80}")
        
        for result in self.results:
            print(f"{result['name']:<20} {result['diff_gain_db']:<10} {result['gbw_hz']:<12} "
                  f"{result['cmrr_db']:<10} {result['phase_margin_deg']:<8} "
                  f"{result['slew_rate_v_per_s']:<12} {result['power_w']:<12}")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Automated Op-Amp Characterization')
    parser.add_argument('-d', '--directory', default='.', 
                       help='Directory containing op-amp netlists (default: current directory)')
    parser.add_argument('-o', '--output', default='characterization_report.csv',
                       help='Output CSV file (default: characterization_report.csv)')
    parser.add_argument('-r', '--results-dir', default='results',
                       help='Results directory (default: results)')
    
    args = parser.parse_args()
    
    # Create characterizer instance
    char = OpAmpCharacterizer(results_dir=args.results_dir)
    
    # Run characterization
    char.run_characterization(directory=args.directory)
    
    # Generate report
    char.generate_report(output_file=args.output)
    
    print(f"\n🎉 Characterization complete!")
    print(f"   Results directory: {args.results_dir}/")
    print(f"   Summary report: {args.output}")


if __name__ == "__main__":
    main()
