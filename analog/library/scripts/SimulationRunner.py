import os
import subprocess
import re
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from concurrent.futures import ThreadPoolExecutor, as_completed

class SimulationRunner:
    """Handles simulation execution and result parsing"""
    
    # Global build directory - always relative to this file
    BUILD_DIR = (Path(__file__).parent / "../../build/schematic").resolve()
    
    def convert_netlist_for_xyce(self, netlist_file: Path) -> Path:
        """Convert ngspice netlist to Xyce-compatible format"""
        xyce_file = netlist_file.with_suffix('.xyce.spice')
        
        try:
            with open(netlist_file, 'r') as f:
                content = f.read()
            
            # Basic conversions for Xyce compatibility
            converted_lines = []
            skip_control_block = False
            
            for line in content.split('\n'):
                line_lower = line.lower().strip()
                
                # Skip .control blocks entirely
                if line_lower.startswith('.control'):
                    skip_control_block = True
                    continue
                elif line_lower.startswith('.endc'):
                    skip_control_block = False
                    continue
                elif skip_control_block:
                    continue
                
                # Skip problematic commands
                if any(cmd in line_lower for cmd in ['let ', 'echo ', 'run', 'while', 'end']):
                    continue
                
                # Convert problematic syntax
                if 'vdb(' in line or 'db(' in line or '[' in line:
                    continue
                
                # Keep the line if it passes all filters
                converted_lines.append(line)
            
            # Add basic Xyce-compatible analysis if none exists
            has_analysis = any('.dc' in line.lower() or '.ac' in line.lower() or '.tran' in line.lower() 
                             for line in converted_lines)
            
            if not has_analysis:
                converted_lines.append('.DC V1 0 1.8 0.1')
            
            with open(xyce_file, 'w') as f:
                f.write('\n'.join(converted_lines))
            
            return xyce_file
            
        except Exception as e:
            print(f"Warning: Could not convert netlist for Xyce: {e}")
            return netlist_file

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
            
            # Time Xyce simulation (primary)
            xyce_start = time.time()
            xyce_result = subprocess.run(['Xyce', netlist_file], 
                                       capture_output=True, text=True, timeout=timeout)
            xyce_time = time.time() - xyce_start
            
            # Time ngspice simulation for comparison
            try:
                ngspice_start = time.time()
                ngspice_result = subprocess.run(['ngspice', '-b', netlist_file], 
                                              capture_output=True, text=True, timeout=timeout)
                ngspice_time = time.time() - ngspice_start
                
                # Print speed comparison
                speedup = ngspice_time / xyce_time if xyce_time > 0 else float('inf')
                faster_sim = "Xyce" if speedup > 1 else "ngspice"
                print(f"Speed comparison for {tb_basename}:")
                print(f"  Xyce:    {xyce_time:.4f}s")
                print(f"  ngspice: {ngspice_time:.4f}s")
                print(f"  Speedup: {speedup:.2f}x ({faster_sim} is faster)")
                print("-" * 50)
                
            except FileNotFoundError:
                print(f"ngspice not found - only Xyce timing available: {xyce_time:.4f}s")
            except subprocess.TimeoutExpired:
                print(f"ngspice timed out - Xyce time: {xyce_time:.4f}s")
            except Exception as e:
                print(f"ngspice error: {e} - Xyce time: {xyce_time:.4f}s")
            
            return self.parse_metrics(xyce_result.stdout, metric_keywords or [])
            
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
    
    def parse_metrics(self, stdout: str, metric_keywords: Optional[List[str]] = None, simulator: str = "ngspice") -> Dict[str, Any]:
        """Parse metrics from SPICE output using improved regex patterns"""
        metrics = {}
        
        if simulator.lower() == "xyce":
            # Xyce-specific output patterns
            # Xyce often outputs results in different format, look for common patterns
            metric_patterns = [
                r'([A-Z_]+):\s*([+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)\s*',  # Standard format
                r'(\w+)\s*=\s*([+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)',      # Assignment format
                r'Final value of (\w+):\s*([+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)'  # Final value format
            ]
        else:
            # ngspice patterns (original)
            metric_patterns = [
                r'([A-Z_]+):\s*([+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)\s*'
            ]
        
        # Try each pattern
        for pattern in metric_patterns:
            matches = re.findall(pattern, stdout)
            for metric_name, value_str in matches:
                try:
                    # Convert to float, handling scientific notation
                    metrics[metric_name.upper()] = float(value_str)
                except ValueError:
                    print(f"Warning: Could not parse metric value '{value_str}' for {metric_name}")
                    continue
        
        # If specific keywords were requested, filter to only those
        if metric_keywords:
            filtered_metrics = {k: v for k, v in metrics.items() if k in metric_keywords}
            metrics = filtered_metrics
        
        # Include simulator info and stdout for debugging
        metrics["simulator_used"] = simulator
        
        # Include stdout for debugging if no metrics found
        if not metrics or len(metrics) == 1:  # Only simulator_used
            return {"error": "No metrics found", "stdout": stdout, "simulator_used": simulator}
        
        # Include stdout for debugging (but don't treat as error since we found metrics)
        metrics["stdout"] = stdout
        return metrics
