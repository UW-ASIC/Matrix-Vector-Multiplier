import os
import subprocess
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from concurrent.futures import ThreadPoolExecutor, as_completed

class SimulationRunner:
    """Handles simulation execution and result parsing"""
    
    # Global build directory - always relative to this file
    BUILD_DIR = (Path(__file__).parent / "../../build/schematic").resolve()
    
    def run_simulation(self, tb_file: Union[str, Path], timeout: int = 30, 
                      metric_keywords: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run a single simulation and return parsed metrics"""
        original_dir = os.getcwd()
        tb_file = Path(tb_file)
        
        try:
            os.chdir(self.BUILD_DIR)
            
            # Generate netlist
            subprocess.run(['xschem', '--netlist', '-q', '-x', tb_file], 
                         capture_output=True, text=True)
            
            # Run simulation
            tb_basename = tb_file.stem
            netlist_file = f"spice/{tb_basename}.spice"
            
            result = subprocess.run(['ngspice', '-b', netlist_file], 
                                  capture_output=True, text=True, timeout=timeout)
            
            return self.parse_metrics(result.stdout, metric_keywords or [])
            
        except subprocess.TimeoutExpired:
            return {"error": f"Simulation timed out after {timeout} seconds"}
        except Exception as e:
            return {"error": f"Exception: {str(e)}"}
        finally:
            os.chdir(original_dir)
    
    def run_simulations(self, tb_files: List[Union[str, Path]], timeout: int = 30, 
                       max_workers: Optional[int] = None, 
                       metric_keywords: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Run multiple simulations in parallel and return list of parsed metrics"""
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all simulation tasks
            future_to_file = {
                executor.submit(self.run_simulation, tb_file, timeout, metric_keywords): tb_file 
                for tb_file in tb_files
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_file):
                tb_file = future_to_file[future]
                try:
                    result = future.result()
                    result['tb_file'] = str(tb_file)  # Add filename to result
                    results.append(result)
                except Exception as e:
                    results.append({
                        "error": f"Exception in parallel execution: {str(e)}",
                        "tb_file": str(tb_file)
                    })
        
        return results
    
    def parse_metrics(self, stdout: str, metric_keywords: Optional[List[str]] = None) -> Dict[str, Any]:
        """Parse metrics from ngspice output using improved regex patterns"""
        metrics = {}
        
        # Common metric patterns from SPICE echo statements
        # Pattern matches: METRIC_NAME: value (with optional scientific notation)
        metric_pattern = r'([A-Z_]+):\s*([+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)\s*'
        
        # Find all metrics in the output
        matches = re.findall(metric_pattern, stdout)
        
        for metric_name, value_str in matches:
            try:
                # Convert to float, handling scientific notation
                metrics[metric_name] = float(value_str)
            except ValueError:
                print(f"Warning: Could not parse metric value '{value_str}' for {metric_name}")
                continue
        
        # If specific keywords were requested, filter to only those
        if metric_keywords:
            filtered_metrics = {k: v for k, v in metrics.items() if k in metric_keywords}
            metrics = filtered_metrics
        
        # Include stdout for debugging if no metrics found
        if not metrics:
            return {"error": "No metrics found", "stdout": stdout}
        
        # Include stdout for debugging (but don't treat as error since we found metrics)
        metrics["stdout"] = stdout
        return metrics
