import os
import sys
from pathlib import Path
from typing import List, Optional, Union, Dict, Any
import re

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
from XSchemWriter import XSchemWriter
from XSchemParser import XSchemParser
from SimulationRunner import SimulationRunner
from DocumentationGenerator import DocumentationGenerator
from Grammar import *


class XSchemInterface:
    def __init__(self, objects: Optional[List[XSchemObject]] = None):
        self.objects = objects or []
        self.parser = XSchemParser()
        self.writer = XSchemWriter()
    
    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> 'XSchemInterface':
        instance = cls()
        instance.objects = instance.parser.parse_file(file_path)
        return instance
    
    def save_to_file(self, file_path: Union[str, Path]) -> None:
        self.writer.write_file(self.objects, file_path)
    
    def find_component_by_reference(self, symbol_reference: str) -> Optional[Component]:
        for obj in self.objects:
            if isinstance(obj, Component) and obj.symbolReference == symbol_reference:
                return obj
        return None
    
    def find_components_by_reference(self, symbol_reference: str) -> List[Component]:
        return [obj for obj in self.objects 
                if isinstance(obj, Component) and obj.symbolReference == symbol_reference]
    
    def find_component_by_name(self, name: str) -> Optional[Component]:
        for obj in self.objects:
            if isinstance(obj, Component) and obj.properties.get("name") == name:
                return obj
        return None
    
    def find_components_by_name_pattern(self, pattern: str) -> List[Component]:
        regex = re.compile(pattern)
        components = []
        for obj in self.objects:
            if isinstance(obj, Component):
                name = obj.properties.get("name")
                if name and regex.search(name):
                    components.append(obj)
        return components
    
    def get_spice(self) -> Optional[Component]:
        corner_comp = self.find_component_by_reference("sky130_fd_pr/corner.sym")
        if not corner_comp:
            corner_comp = Component(
                symbolReference="sky130_fd_pr/corner.sym",
                x=300.0,
                y=-100.0,
                rotation=0,
                flip=0,
                properties={
                    "name": "CORNER",
                    "only_toplevel": "false",
                    "corner": "tt"
                }
            )
            self.objects.append(corner_comp)
        
        spice_comp = self.find_component_by_reference("devices/code_shown.sym")
        if not spice_comp:
            spice_comp = Component(
                symbolReference="devices/code_shown.sym",
                x=240.0,
                y=120.0,
                rotation=0,
                flip=0,
                properties={
                    "name": "s1",
                    "only_toplevel": "false",
                    "value": ""
                }
            )
            self.objects.append(spice_comp)
        return spice_comp
    
    # NEW METHODS FOR BATCH OPERATIONS
    
    @staticmethod
    def create_and_simulate_variants(variants: Dict[str, Dict[str, Any]], 
                                   tests: Dict[str, Dict[str, Any]], 
                                   component_type: str,
                                   template_base: str = "template",
                                   build_dir: str = "../../build/schematic",
                                   units_map: Optional[Dict[str, str]] = None) -> Dict[str, Dict[str, Any]]:
        """
        Complete workflow: create variants, run simulations, generate documentation
        
        Args:
            variants: Dictionary of variant definitions
            tests: Dictionary of test configurations  
            component_type: Type of component (e.g., "OpAmp", "TIA")
            template_base: Base template directory
            build_dir: Build directory for simulations
            units_map: Mapping of metrics to units for documentation
            
        Returns:
            Dictionary of simulation results for each variant
        """
        generator = VariantGenerator(template_base, component_type)
        simulator = SimulationRunner(build_dir)
        all_results = {}
        
        print(f"Creating {component_type} variants...")
        
        for name, info in variants.items():
            print(f"Creating {name} ({info['short']})...")
            
            # Create variant
            folder, short = generator.create_variant(name, info, tests)
            print(f"✓ Created {name} ({short})")
            
            # Run simulations
            simulation_results = {}
            for test_name in tests.keys():
                testbench_path = f"{folder}/tb/{component_type}_{short}_{test_name}_tb.sch"
                simulation_results[test_name] = simulator.run_simulation(testbench_path)
            
            # Generate documentation
            DocumentationGenerator.create_readme(
                folder, name, short, info["params"], simulation_results, 
                component_type, units_map
            )
            
            all_results[name] = simulation_results
            print(f"  ✓ Simulated and documented")
        
        print("Done!")
        return all_results
    
    def update_component_parameters(self, component_updates: Dict[str, Dict[str, Any]]) -> None:
        """Batch update component parameters"""
        for component_name, updates in component_updates.items():
            component = self.find_component_by_name(component_name)
            if component:
                component.properties.update(updates)
    
    def clone_with_modifications(self, modifications: Dict[str, Any]) -> 'XSchemInterface':
        """Create a copy of the interface with modifications applied"""
        # This would need deep copying of objects - simplified version
        new_interface = XSchemInterface(self.objects.copy())
        
        if "component_updates" in modifications:
            new_interface.update_component_parameters(modifications["component_updates"])
        
        return new_interface
    
    def get_all_components_by_type(self, symbol_pattern: str) -> List[Component]:
        """Get all components matching a symbol reference pattern"""
        regex = re.compile(symbol_pattern)
        return [obj for obj in self.objects 
                if isinstance(obj, Component) and regex.search(obj.symbolReference)]
    
    def replace_component_reference(self, old_reference: str, new_reference: str) -> int:
        """Replace all instances of a component reference, returns count of replacements"""
        count = 0
        for obj in self.objects:
            if isinstance(obj, Component) and obj.symbolReference == old_reference:
                obj.symbolReference = new_reference
                count += 1
        return count


def add_component(self, name: str, symbol_path: str, properties: Dict[str, str] = None) -> None:
    """
    Add a component to a schematic
    
    Args:
        name: Name of the component (e.g., "X1")
        symbol_path: Path to the symbol file
        properties: Additional properties for the component
    """
    from XSchemObject import XSchemObject
    
    # Create a new component object
    comp_obj = XSchemObject(type="component")
    comp_obj.properties = {
        "name": name,
        "symbol": symbol_path
    }
    
    if properties:
        comp_obj.properties.update(properties)
    
    self.objects.append(comp_obj)

def add_source(self, name: str, value: str) -> None:
    """
    Add a voltage or current source to a schematic
    
    Args:
        name: Name of the source (e.g., "V1")
        value: Value of the source (e.g., "DC 5V")
    """
    # Determine source type from name
    source_type = "vsource" if name.startswith("V") else "isource"
    
    # Add the source as a component
    self.add_component(name, f"devices/{source_type}.sym", {"value": value})


class VariantGenerator:
    """Handles creation of circuit variants and their testbenches"""
    
    def __init__(self, template_base: str, component_type: str):
        self.template_base = template_base  # e.g., "template"
        self.component_type = component_type  # e.g., "OpAmp", "TIA"
        
    def create_variant(self, name: str, info: Dict[str, Any], tests: Dict[str, Dict[str, Any]]) -> tuple:
        """Create a variant with all its testbenches"""
        folder = f"{self.component_type}_{name}"
        short = info["short"]
        os.makedirs(f"{folder}/tb", exist_ok=True)
        
        # Create main schematic
        self._create_schematic(folder, short, info["params"])
        
        # Create symbol
        self._create_symbol(folder, short)
        
        # Create testbenches
        self._create_testbenches(folder, short, tests)
        
        return folder, short
    
    def _create_schematic(self, folder: str, short: str, params: Dict[str, Dict[str, str]]):
        """Create the main schematic with updated parameters"""
        sch = XSchemInterface.from_file(f"{self.template_base}/{self.component_type}.sch")
        
        for component, component_params in params.items():
            comp = sch.find_component_by_name(component)
            if comp:
                comp.properties.update(component_params)
        
        sch.save_to_file(f"{folder}/{self.component_type}_{short}.sch")
    
    def _create_symbol(self, folder: str, short: str):
        """Create the symbol (copy from template)"""
        sym = XSchemInterface.from_file(f"{self.template_base}/{self.component_type}.sym")
        sym.save_to_file(f"{folder}/{self.component_type}_{short}.sym")
    
    def _create_testbenches(self, folder: str, short: str, tests: Dict[str, Dict[str, Any]]):
        """Create all testbenches for the variant"""
        for test_name, test_config in tests.items():
            testbench = XSchemInterface.from_file(f"{self.template_base}/{self.component_type}_tb.sch")
            
            # Update component reference
            self._update_component_reference(testbench, folder, short)
            
            # Update test sources
            self._update_test_sources(testbench, test_config)
            
            # Update SPICE commands
            self._update_spice_commands(testbench, test_config)
            
            testbench.save_to_file(f"{folder}/tb/{self.component_type}_{short}_{test_name}_tb.sch")
    
    def _update_component_reference(self, testbench: 'XSchemInterface', folder: str, short: str):
        """Update the component reference to point to the new variant"""
        # Try to find component by reference pattern
        old_ref = f"{self.component_type}s/{self.template_base}/{self.component_type}.sym"
        component = testbench.find_component_by_reference(old_ref)
        
        if component:
            component.symbolReference = f"{self.component_type}s/{folder}/{self.component_type}_{short}.sym"
    
    def _update_test_sources(self, testbench: 'XSchemInterface', test_config: Dict[str, Any]):
        """Update test source values"""
        for source_name, source_value in test_config.items():
            if source_name != "spice":  # Skip spice commands
                # Extract component name (everything after the last underscore)
                component_name = source_name.split('_')[-1].upper()
                if len(source_name.split('_')) > 1:
                    component_name = source_name.split('_')[0].upper()
                
                component = testbench.find_component_by_name(component_name)
                if component:
                    component.properties["value"] = source_value
    
    def _update_spice_commands(self, testbench: 'XSchemInterface', test_config: Dict[str, Any]):
        """Update SPICE simulation commands"""
        if "spice" in test_config:
            spice_component = testbench.get_spice()
            if spice_component:
                spice_component.properties["value"] = test_config["spice"]
