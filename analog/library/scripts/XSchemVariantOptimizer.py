import os
import sys
import numpy as np
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from scipy.optimize import minimize, differential_evolution
import time
import shutil

# Add current directory to path
CURRENT_DIR = Path(__file__).parent
sys.path.insert(0, str(CURRENT_DIR))
from XSchemInterface import XSchemInterface, build_and_simulate_variants
from SimulationRunner import SimulationRunner

@dataclass
class OptimizationTarget:
    metric: str
    target_value: float
    weight: float = 1.0
    constraint_type: str = "min"

@dataclass
class ParameterBound:
    component: str
    parameter: str
    min_value: float
    max_value: float

class CircuitOptimizer:
    """Circuit optimizer with efficient adaptive step sizing"""
    
    def __init__(self, circuit_type: str, tests: Dict[str, Dict[str, Any]], 
                 template_dir: Path):
        self.circuit_type = circuit_type
        self.tests = tests
        self.template_dir = template_dir
        self.targets: List[OptimizationTarget] = []
        self.bounds: List[ParameterBound] = []
        self.simulator = SimulationRunner()
        self.eval_count = 0
        self.previous_folder = None
        
        # Adaptive tracking (simplified)
        self.recent_scores = []
        self.stagnation_count = 0
        self.best_score_seen = 0.0
    
    def _apply_sky130_drc(self, x: np.ndarray) -> np.ndarray:
        """Apply SKY130 design rules for 1.8V devices"""
        x_corrected = x.copy()
        
        for i, bound in enumerate(self.bounds):
            # Quantize to 5nm grid
            x_corrected[i] = round(x[i] / 0.005) * 0.005
            
            # Apply SKY130 minimums
            if 'L' in bound.parameter:  # Length: 0.15μm minimum
                x_corrected[i] = max(x_corrected[i], 0.15)
            elif 'W' in bound.parameter:  # Width: 0.42μm minimum  
                x_corrected[i] = max(x_corrected[i], 0.42)
                
            x_corrected[i] = np.clip(x_corrected[i], bound.min_value, bound.max_value)
        
        return x_corrected

    def add_target(self, metric: str, target_value: float, weight: float = 1.0, 
                   constraint_type: str = "min") -> None:
        self.targets.append(OptimizationTarget(metric, target_value, weight, constraint_type))
    
    def add_bound(self, component: str, parameter: str, min_value: float, max_value: float) -> None:
        self.bounds.append(ParameterBound(component, parameter, min_value, max_value))
    
    def optimize(self, initial_params: Dict[str, Dict[str, str]], units_map: Dict[str, str], 
                 max_iterations: int = 20, target_precision: float = 0.99) -> Dict[str, Dict[str, str]]:
        """Main optimization function - much more efficient"""
        self.units_map = units_map
        self.target_precision = target_precision
        
        initial_score = self._evaluate_parameters(initial_params)
        if initial_score <= 0:
            return initial_params
        
        x0 = np.array([float(initial_params[b.component][b.parameter]) for b in self.bounds])
        bounds_array = [(b.min_value, b.max_value) for b in self.bounds]
        
        print(f"Initial score: {initial_score:.6f}")
        print(f"Target precision: {target_precision}")
        
        # Check if we're already close to target
        if initial_score >= target_precision:
            print("Already at target precision!")
            return initial_params
        
        def adaptive_objective(x):
            x = self._apply_sky130_drc(x)  # Apply DRC first
            self.eval_count += 1
            params = self._vector_to_params(x, initial_params)
            
            print(f"Evaluation {self.eval_count}:")
            for i, bound in enumerate(self.bounds):
                print(f"  {bound.component}.{bound.parameter}: {x[i]:.6f}")
            
            score = self._evaluate_parameters(params)
            print(f"  Score: {score:.6f}")
            
            # Track progress for adaptive behavior
            self.recent_scores.append(score)
            if len(self.recent_scores) > 5:
                self.recent_scores.pop(0)
            
            # Update best score
            if score > self.best_score_seen:
                self.best_score_seen = score
                self.stagnation_count = 0
                print(f"  *** NEW BEST: {score:.6f} ***")
            else:
                self.stagnation_count += 1
            
            # Early termination if target reached
            if score >= target_precision:
                print(f"  *** TARGET PRECISION REACHED: {score:.6f} >= {target_precision} ***")
                return float('-inf')  # Signal to stop optimization
            
            print()
            return -score
        
        # Try multiple strategies, but stop early if target is reached
        strategies = [
            {
                'name': 'Adaptive Differential Evolution',
                'method': 'differential_evolution',
                'options': {
                    'maxiter': max_iterations,
                    'seed': 42,
                    'popsize': min(8, len(self.bounds) * 2),  # Smaller population
                    'atol': 1e-3,  # Less strict tolerance
                    'tol': 1e-2,
                    'updating': 'deferred',  # More efficient updating
                    'polish': True  # Fine-tune final result
                }
            },
            {
                'name': 'Adaptive L-BFGS-B', 
                'method': 'L-BFGS-B',
                'options': {
                    'maxiter': max_iterations,
                    'eps': self._calculate_adaptive_eps(bounds_array),
                    'ftol': 1e-3,  # Less strict tolerance
                    'gtol': 1e-2,
                    'maxfun': max_iterations * 2
                }
            }
        ]
        
        best_result = None
        best_score = initial_score
        
        for strategy in strategies:
            print(f"=== {strategy['name']} ===")
            
            try:
                if strategy['method'] == 'differential_evolution':
                    result = differential_evolution(
                        adaptive_objective, bounds_array,
                        **strategy['options']
                    )
                else:
                    result = minimize(
                        adaptive_objective, x0,
                        method=strategy['method'],
                        bounds=bounds_array,
                        options=strategy['options']
                    )
                
                final_score = -result.fun if result.fun != float('inf') else self.best_score_seen
                print(f"{strategy['name']} final score: {final_score:.6f}")
                
                if final_score > best_score:
                    best_result = result
                    best_score = final_score
                
                # Stop if we've reached our target
                if final_score >= target_precision:
                    print(f"Target precision {target_precision} reached! Stopping optimization.")
                    break
                    
                # Stop if we're stagnating badly
                if self.stagnation_count > max_iterations // 2:
                    print(f"Optimization stagnating after {self.stagnation_count} evaluations without improvement.")
                    break
                
            except Exception as e:
                print(f"{strategy['name']} failed: {e}")
                continue
        
        # Clean up final folder
        if self.previous_folder and Path(self.previous_folder).exists():
            shutil.rmtree(self.previous_folder)
        
        if best_result is None:
            print("No optimization strategy succeeded, returning initial parameters")
            return initial_params
        
        final_params = self._vector_to_params(best_result.x, initial_params)
        print(f"\nOptimization complete. Best score: {best_score:.6f}")
        return final_params
    
    def _calculate_adaptive_eps(self, bounds_array: List[tuple]) -> float:
        """Calculate adaptive epsilon based on parameter scales"""
        ranges = [b[1] - b[0] for b in bounds_array]
        avg_range = np.mean(ranges)
        # Adaptive epsilon: smaller for smaller parameter ranges
        return max(1e-8, avg_range * 1e-6)
    
    def _vector_to_params(self, x: np.ndarray, base_params: Dict[str, Dict[str, str]]) -> Dict[str, Dict[str, str]]:
        """Convert optimization vector to parameter dictionary"""
        params = {}
        for comp, comp_params in base_params.items():
            params[comp] = comp_params.copy()
        
        # Ensure all components exist
        for bound in self.bounds:
            if bound.component not in params:
                params[bound.component] = {}
        
        for i, bound in enumerate(self.bounds):
            # Adaptive precision based on parameter range
            param_range = bound.max_value - bound.min_value
            if param_range > 100:
                precision = 3  # Large values
            elif param_range > 1:
                precision = 6  # Medium values  
            else:
                precision = 9  # Small values need more precision
            
            params[bound.component][bound.parameter] = f"{x[i]:.{precision}f}"
        
        return params
    
    def _evaluate_parameters(self, params: Dict[str, Dict[str, str]]) -> float:
        """Evaluate parameter set"""
        try:
            # Clean up previous iteration folder
            if self.previous_folder and Path(self.previous_folder).exists():
                shutil.rmtree(self.previous_folder)
            
            variant_name = f"opt_{int(time.time()*1000) % 100000}_{self.eval_count}"
            folder = f"{self.circuit_type}_{variant_name}"
            
            variant = {
                variant_name: {
                    "short": variant_name, 
                    "params": params
                }
            }
            
            results = build_and_simulate_variants(
                variants=variant,
                tests=self.tests,
                circuit_type=self.circuit_type,
                template_dir=str(self.template_dir),
                units_map=self.units_map
            )
            
            score = self._calculate_score(results)
            
            # Store current folder for cleanup in next iteration
            self.previous_folder = folder
            
            return score
            
        except Exception:
            return 0.1
    
    def _calculate_score(self, results: Dict[str, Dict[str, Any]]) -> float:
        """Calculate optimization score"""
        total_score = 0.0
        total_weight = 0.0
        
        for target in self.targets:
            value = self._find_metric(results, target.metric)
            
            if value is not None:
                if target.constraint_type == "min":
                    score = min(1.0, value / target.target_value) if target.target_value > 0 else 0.0
                elif target.constraint_type == "max":
                    score = min(1.0, target.target_value / value) if value > 0 else 0.0
                else:  # exact
                    rel_error = abs(value - target.target_value) / target.target_value
                    score = max(0.0, 1.0 - rel_error)
                
                total_score += score * target.weight
                total_weight += target.weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _find_metric(self, results: Dict[str, Dict[str, Any]], metric: str) -> Optional[float]:
        """Find metric value in simulation results"""
        for variant_results in results.values():
            for test_result in variant_results.values():
                # Direct result check
                if metric in test_result and isinstance(test_result[metric], (int, float)):
                    return float(test_result[metric])
                
                # Parse from stdout
                if "stdout" in test_result:
                    stdout = test_result["stdout"]
                    patterns = [
                        rf"{metric}:\s*([+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)",
                        rf"echo\s+'{metric}:'\s+\$&([^\s]+)",
                        rf"{metric}\s*=\s*([+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)",
                        rf"{metric.lower()}:\s*([+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)",
                    ]
                    
                    for pattern in patterns:
                        matches = re.findall(pattern, stdout, re.IGNORECASE)
                        if matches:
                            try:
                                return float(matches[0])
                            except ValueError:
                                continue
        
        return None


def optimize_circuit(circuit_type: str, initial_params: Dict[str, Dict[str, str]], 
                    tests: Dict[str, Dict[str, Any]], targets: List[Dict[str, Any]], 
                    bounds: List[Dict[str, Any]], template_dir: str = "template",
                    max_iterations: int = 20, target_precision: float = 0.95) -> Dict[str, Dict[str, str]]:
    """Optimize circuit parameters with adaptive step sizing and early stopping"""
    import inspect
    caller_file = Path(inspect.stack()[1].filename)
    template_path = caller_file.parent / template_dir
    
    optimizer = CircuitOptimizer(circuit_type, tests, template_path)
    
    unit_map = {}
    for target in targets:
        unit_map[target["metric"]] = target["UNIT"]
        del target["UNIT"]
    
    for target in targets:
        optimizer.add_target(**target)
    for bound in bounds:
        optimizer.add_bound(**bound)
    
    return optimizer.optimize(initial_params, unit_map, max_iterations, target_precision)
