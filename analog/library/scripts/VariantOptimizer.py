#!/usr/bin/env python3
import os
import sys
import json
import time
import numpy as np
import concurrent.futures
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from scipy.optimize import differential_evolution

from XSchemInterface import XSchemInterface, VariantGenerator
from SimulationRunner import SimulationRunner

class VariantOptimizer:
    """
    Optimizer for circuit variants that leverages test results to find optimal parameters
    """
    def __init__(self, 
                template_base: str = "template",
                component_type: str = "TIA",
                build_dir: str = "../../build/schematic",
                results_dir: str = "results",
                units_map: Optional[Dict[str, str]] = None):
        """
        Initialize the circuit optimizer
        
        Args:
            template_base: Base directory with template files
            component_type: Component type (e.g., "TIA")
            build_dir: Directory for build outputs
            results_dir: Directory for storing optimization results
            units_map: Mapping of metrics to units for documentation
        """
        self.template_base = template_base
        self.component_type = component_type
        self.build_dir = build_dir
        self.results_dir = results_dir
        self.units_map = units_map or {}
        self.tests = {}
        self.param_ranges = {}
        self.base_params = {}
        self.targets = {}
        self.optimization_results = {}
        self.best_variants = {}
        
        # Fixed variant name for reuse
        self.variant_folder = f"{component_type}_Optimization"
        self.variant_short = "OPT"
        
        # Create results directory
        os.makedirs(results_dir, exist_ok=True)
    
    def set_tests(self, tests: Dict[str, Dict[str, Any]]) -> None:
        """Set test configurations for optimization"""
        self.tests = tests
    
    def set_param_ranges(self, param_ranges: Dict[str, Dict[str, Tuple[float, float]]]) -> None:
        """Set parameter ranges for optimization"""
        self.param_ranges = param_ranges
    
    def set_base_params(self, base_params: Dict[str, Dict[str, str]]) -> None:
        """Set base parameters for optimization"""
        self.base_params = base_params
    
    def set_targets(self, targets: Dict[str, Dict[str, float]]) -> None:
        """Set optimization targets"""
        self.targets = targets
    
    def load_config_from_file(self, config_file: str) -> None:
        """Load configuration from a JSON file"""
        with open(config_file, 'r') as f:
            config = json.load(f)
            
        if 'tests' in config:
            self.tests = config['tests']
        if 'param_ranges' in config:
            self.param_ranges = config['param_ranges']
        if 'base_params' in config:
            self.base_params = config['base_params']
        if 'targets' in config:
            self.targets = config['targets']
        if 'units_map' in config:
            self.units_map = config['units_map']
    
    def save_config_to_file(self, config_file: str) -> None:
        """Save configuration to a JSON file"""
        config = {
            'tests': self.tests,
            'param_ranges': self.param_ranges,
            'base_params': self.base_params,
            'targets': self.targets,
            'units_map': self.units_map
        }
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def _param_vector_to_dict(self, param_vector: List[float]) -> Dict[str, Dict[str, str]]:
        """Convert parameter vector to dictionary format"""
        params = {}
        
        for component, comp_params in self.base_params.items():
            params[component] = {}
            for param_name in comp_params.keys():
                if f"{component}.{param_name}" in self._param_index_map:
                    idx = self._param_index_map[f"{component}.{param_name}"]
                    params[component][param_name] = str(round(param_vector[idx], 3))
                else:
                    params[component][param_name] = self.base_params[component][param_name]
        
        return params
    
    def _create_param_index_map(self) -> Dict[str, int]:
        """Create mapping of parameter names to indices in parameter vector"""
        param_index_map = {}
        index = 0
        
        for component, comp_params in self.param_ranges.items():
            for param_name in comp_params.keys():
                param_index_map[f"{component}.{param_name}"] = index
                index += 1
                
        return param_index_map
    
    def _create_parameter_bounds(self) -> List[Tuple[float, float]]:
        """Create bounds for optimization parameters"""
        bounds = []
        
        for component, comp_params in self.param_ranges.items():
            for param_name, (min_val, max_val) in comp_params.items():
                bounds.append((min_val, max_val))
                
        return bounds
    
    def _run_simulation_test(self, test_name: str, testbench_path: str) -> Dict[str, Any]:
        """Run a single simulation test and return the results"""
        simulator = SimulationRunner(self.build_dir)
        return simulator.run_simulation(testbench_path)
    
    def _create_variant_and_testbenches(self, params: Dict[str, Dict[str, str]]) -> Dict[str, str]:
        """
        Create a variant with all required testbenches
        
        Args:
            params: Parameter dictionary
            
        Returns:
            Dictionary mapping test names to testbench paths
        """
        # Always use the same variant name to overwrite
        variant_info = {"short": self.variant_short, "params": params}
        
        # Create all testbenches
        generator = VariantGenerator(self.template_base, self.component_type)
        folder, short = generator.create_variant(self.variant_folder, variant_info, self.tests)
        
        # Build a map of test names to testbench paths
        testbench_paths = {}
        for test_name in self.tests.keys():
            testbench_path = f"{folder}/tb/{self.component_type}_{short}_{test_name}_tb.sch"
            testbench_paths[test_name] = testbench_path
            
        return testbench_paths
    
    def _run_all_tests_parallel(self, testbench_paths: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
        """
        Run all tests in parallel
        
        Args:
            testbench_paths: Dictionary mapping test names to testbench paths
            
        Returns:
            Dictionary of test results for each test
        """
        all_results = {}
        
        # Use ThreadPoolExecutor to run tests in parallel
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Submit all test simulations
            future_to_test = {
                executor.submit(self._run_simulation_test, test_name, path): test_name
                for test_name, path in testbench_paths.items()
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_test):
                test_name = future_to_test[future]
                try:
                    results = future.result()
                    all_results[test_name] = results
                except Exception as e:
                    print(f"Test {test_name} generated an exception: {e}")
                    all_results[test_name] = {}
        
        return all_results
    
    def _evaluate_variant(self, param_vector: List[float], target_name: str = None) -> float:
        """
        Evaluate a variant against all targets or a specific target
        
        Args:
            param_vector: Vector of parameter values
            target_name: Optional name of the target to evaluate (if None, evaluate against all targets)
            
        Returns:
            Cost (lower is better)
        """
        # Convert parameter vector to dictionary
        params = self._param_vector_to_dict(param_vector)
        
        # Create variant with all testbenches
        testbench_paths = self._create_variant_and_testbenches(params)
        
        # Run all tests in parallel
        all_test_results = self._run_all_tests_parallel(testbench_paths)
        
        # If target_name is specified, only compute cost for that target
        if target_name:
            target_metrics = self.targets.get(target_name, {})
            test_results = all_test_results.get(target_name, {})
            return self._compute_cost(target_metrics, test_results)
        
        # Otherwise, compute total cost across all targets
        total_cost = 0
        for target_name, target_metrics in self.targets.items():
            test_results = all_test_results.get(target_name, {})
            total_cost += self._compute_cost(target_metrics, test_results)
            
        return total_cost
    
    def _compute_cost(self, target_metrics: Dict[str, float], test_results: Dict[str, Any]) -> float:
        """
        Compute cost based on deviation from target metrics
        
        Args:
            target_metrics: Dictionary of target metric values
            test_results: Dictionary of simulation results
            
        Returns:
            Cost (lower is better)
        """
        cost = 0
        
        for metric, target_value in target_metrics.items():
            if metric in test_results:
                measured = float(test_results[metric])
                # Cost is relative error (%)
                relative_error = abs((measured - target_value) / target_value) * 100
                cost += relative_error
                # Print for debugging
                print(f"  Metric {metric}: Target={target_value}, Measured={measured}, Error={relative_error:.2f}%")
            else:
                # Missing metric is heavily penalized
                cost += 1000
                print(f"  Missing metric: {metric} (penalty cost: 1000)")
                
        return cost
    
    def optimize(self, max_iterations: int = 50, population_size: int = 15) -> Dict[str, Dict[str, Any]]:
        """
        Perform optimization for each target
        
        Args:
            max_iterations: Maximum number of iterations
            population_size: Population size for differential evolution
            
        Returns:
            Dictionary of optimized variants for each target
        """
        # Create parameter index mapping and bounds
        self._param_index_map = self._create_param_index_map()
        bounds = self._create_parameter_bounds()
        
        # Optimize for each target
        for target_name in self.targets.keys():
            print(f"Optimizing for target: {target_name}")
            
            # Define objective function for this target
            def objective(param_vector):
                return self._evaluate_variant(param_vector, target_name)
            
            # Run differential evolution
            result = differential_evolution(
                objective,
                bounds,
                maxiter=max_iterations,
                popsize=population_size,
                tol=0.01,
                mutation=(0.5, 1.0),
                recombination=0.7,
                disp=True
            )
            
            # Save results
            best_params = self._param_vector_to_dict(result.x)
            self.optimization_results[target_name] = {
                "best_params": best_params,
                "best_cost": result.fun,
                "success": result.success,
                "iterations": result.nit
            }
            
            # Create the best variant
            self.best_variants[target_name] = {
                "short": f"OPT_{target_name[:2].upper()}",
                "params": best_params
            }
            
            print(f"Optimization completed for {target_name}. Best cost: {result.fun}")
            
        # Save all optimization results
        self._save_optimization_results()
        
        return self.best_variants
    
    def _save_optimization_results(self) -> None:
        """Save optimization results to a file"""
        results_file = os.path.join(self.results_dir, "optimization_results.json")
        with open(results_file, 'w') as f:
            json.dump(self.optimization_results, f, indent=2)
    
    def create_and_simulate_best_variants(self) -> Dict[str, Dict[str, Any]]:
        """
        Create and simulate the best variants found during optimization
        
        Returns:
            Dictionary of simulation results for each variant
        """
        results = {}
        
        for target_name, variant_info in self.best_variants.items():
            # Create a unique name for the final variant
            variant_name = f"{self.component_type}_{target_name}"
            variant_info_copy = variant_info.copy()
            
            # Create variant with all tests
            generator = VariantGenerator(self.template_base, self.component_type)
            folder, short = generator.create_variant(variant_name, variant_info_copy, self.tests)
            
            # Run all tests for this variant
            test_results = {}
            simulator = SimulationRunner(self.build_dir)
            
            for test_name in self.tests:
                testbench_path = f"{folder}/tb/{self.component_type}_{short}_{test_name}_tb.sch"
                test_result = simulator.run_simulation(testbench_path)
                test_results[test_name] = test_result
            
            results[target_name] = {
                "params": variant_info_copy["params"],
                "results": test_results
            }
            
        return results
    
    def create_pareto_variants(self, metric_pairs: List[Tuple[str, str]], 
                             num_variants: int = 5) -> Dict[str, Dict[str, Any]]:
        """
        Create Pareto-optimal variants that balance trade-offs between metrics
        
        Args:
            metric_pairs: List of tuples with metrics to balance
            num_variants: Number of Pareto variants to create
            
        Returns:
            Dictionary of Pareto-optimal variants
        """
        pareto_variants = {}
        
        for i, (metric1, metric2) in enumerate(metric_pairs):
            variant_name = f"Pareto_{metric1}_{metric2}"
            short_name = f"P{i}"
            
            # Create parameter vector between the two optimized solutions
            # with different weights to get Pareto-optimal solutions
            params1 = self.optimization_results.get(metric1, {}).get("best_params", self.base_params)
            params2 = self.optimization_results.get(metric2, {}).get("best_params", self.base_params)
            
            # Create variants with different weights
            for j in range(num_variants):
                weight = (j + 1) / (num_variants + 1)  # Weights between 0 and 1, excluding endpoints
                
                # Interpolate between the parameters
                combined_params = {}
                for component, comp_params in params1.items():
                    if component in params2:
                        combined_params[component] = {}
                        for param_name, value1 in comp_params.items():
                            if param_name in params2[component]:
                                value2 = params2[component][param_name]
                                # Interpolate between the two values
                                try:
                                    val1 = float(value1)
                                    val2 = float(value2)
                                    combined_value = val1 * (1 - weight) + val2 * weight
                                    combined_params[component][param_name] = str(round(combined_value, 3))
                                except ValueError:
                                    # If not numeric, use one of the values
                                    combined_params[component][param_name] = value1
                            else:
                                combined_params[component][param_name] = value1
                    else:
                        combined_params[component] = comp_params
                
                variant_name_with_weight = f"{variant_name}_{j+1}"
                short_name_with_weight = f"{short_name}{j+1}"
                
                pareto_variants[variant_name_with_weight] = {
                    "short": short_name_with_weight,
                    "params": combined_params
                }
        
        return pareto_variants
    
    def compare_variants(self, variants: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Simulate and compare multiple variants
        
        Args:
            variants: Dictionary of variants to compare
            
        Returns:
            Dictionary of simulation results for each variant
        """
        results = {}
        
        # Create and simulate each variant
        for variant_name, variant_info in variants.items():
            # Create the variant with all tests
            generator = VariantGenerator(self.template_base, self.component_type)
            folder, short = generator.create_variant(variant_name, variant_info, self.tests)
            
            # Run all tests for this variant
            test_results = {}
            simulator = SimulationRunner(self.build_dir)
            
            for test_name in self.tests:
                testbench_path = f"{folder}/tb/{self.component_type}_{short}_{test_name}_tb.sch"
                test_result = simulator.run_simulation(testbench_path)
                test_results[test_name] = test_result
            
            results[variant_name] = {
                "params": variant_info["params"],
                "results": test_results
            }
        
        # Save comparison results
        results_file = os.path.join(self.results_dir, "comparison_results.json")
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
            
        return results
