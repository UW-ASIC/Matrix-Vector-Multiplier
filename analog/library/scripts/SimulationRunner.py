import os
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Union, Optional

class SimulationRunner:
    """Handles simulation execution and result parsing"""
    
    def __init__(self, build_dir: str = "../../build/schematic"):
        self.build_dir = Path(build_dir)
        
    def run_simulation(self, tb_file: Union[str, Path], timeout: int = 30) -> Dict[str, Any]:
        """Run a single simulation and return parsed metrics"""
        original_dir = os.getcwd()
        tb_file = Path(tb_file)
        
        try:
            os.chdir(self.build_dir)
            
            # Generate netlist
            subprocess.run(['xschem', '--netlist', '-q', tb_file], 
                         capture_output=True, text=True)
            
            # Run simulation
            tb_basename = Path(tb_file).stem
            netlist_file = f"spice/{tb_basename}.spice"
            
            result = subprocess.run(['ngspice', '-b', netlist_file], 
                                  capture_output=True, text=True, timeout=timeout)
            
            return self.parse_metrics(result.stdout)
            
        except subprocess.TimeoutExpired:
            return {"error": f"Simulation timed out after {timeout} seconds"}
        except Exception as e:
            return {"error": f"Exception: {str(e)}"}
        finally:
            os.chdir(original_dir)
    
    def parse_metrics(self, stdout: str, metric_keywords: List[str]) -> Dict[str, Any]:
        """Parse metrics from ngspice output"""
        metrics = {}
        for line in stdout.split('\n'):
            line = line.strip()
            if any(line.startswith(keyword) for keyword in metric_keywords):
                try:
                    key, val = line.split(':', 1)
                    numeric_value = val.strip().split()[0]
                    metrics[key.strip()] = float(numeric_value)
                except (ValueError, IndexError) as e:
                    print(f"Warning: Could not parse metric line '{line}': {e}")
        
        return metrics if metrics else {"error": "No metrics found", "stdout": stdout}


