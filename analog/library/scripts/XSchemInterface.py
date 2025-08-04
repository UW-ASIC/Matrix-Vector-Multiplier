import os
import sys
import re
from pathlib import Path
from typing import List, Optional, Dict, Any

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CURRENT_DIR)
from XSchemWriter import XSchemWriter
from XSchemParser import XSchemParser
from SimulationRunner import SimulationRunner
from DocumentationGenerator import DocumentationGenerator
from Grammar import *


class XSchemInterface:
    """Main interface for working with XSchem schematic files"""
    
    def __init__(self, components: Optional[List[XSchemObject]] = None):
        self.components = components or []
        self._parser = XSchemParser()
        self._writer = XSchemWriter()
    
    @classmethod
    def load(cls, file_path: Path) -> 'XSchemInterface':
        """Load schematic from file"""
        instance = cls()
        instance.components = instance._parser.parse_file(file_path)
        return instance
    
    def save(self, file_path: Path) -> None:
        """Save schematic to file"""
        self._writer.write_file(self.components, file_path)
    
    def find_component_by_symbol(self, symbol_ref: str) -> Optional[Component]:
        """Find first component with matching symbol reference"""
        for comp in self.components:
            if isinstance(comp, Component) and comp.symbolReference == symbol_ref:
                return comp
        return None
    
    def find_component_by_name(self, name: str) -> Optional[Component]:
        """Find component by name"""
        for comp in self.components:
            if isinstance(comp, Component) and comp.properties.get("name") == name:
                return comp
        return None
    
    def find_components_by_pattern(self, pattern: str) -> List[Component]:
        """Find components whose names match the regex pattern"""
        compiled_pattern = re.compile(pattern)
        return [comp for comp in self.components 
                if isinstance(comp, Component) and 
                comp.properties.get("name") and 
                compiled_pattern.search(comp.properties["name"])]
    
    def ensure_spice_setup(self) -> Component:
        """Ensure required SPICE simulation components exist"""
        SPICE_CORNER_SYMBOL = "sky130_fd_pr/corner.sym"
        SPICE_CODE_SYMBOL = "devices/code_shown.sym"
        # Check corner component
        if not self.find_component_by_symbol(SPICE_CORNER_SYMBOL):
            corner = Component(
                symbolReference=SPICE_CORNER_SYMBOL,
                x=300.0, y=-100.0, rotation=0, flip=0,
                properties={"name": "CORNER", "only_toplevel": "false", "corner": "tt"}
            )
            self.components.append(corner)
        
        # Check SPICE code component
        spice_code = self.find_component_by_symbol(SPICE_CODE_SYMBOL)
        if not spice_code:
            spice_code = Component(
                symbolReference=SPICE_CODE_SYMBOL,
                x=240.0, y=120.0, rotation=0, flip=0,
                properties={"name": "s1", "only_toplevel": "false", "value": ""}
            )
            self.components.append(spice_code)
        
        return spice_code
    
    def update_component_properties(self, component_name: str, new_properties: Dict[str, str]) -> bool:
        """Update properties of a named component"""
        component = self.find_component_by_name(component_name)
        if component:
            component.properties.update(new_properties)
            return True
        return False
    
    def add_component(self, name: str, symbol_path: str, x: float = 0, y: float = 0, 
                     properties: Optional[Dict[str, str]] = None) -> Component:
        """Add a new component to the schematic"""
        comp_properties = {"name": name, **(properties or {})}
        
        component = Component(
            symbolReference=symbol_path, x=x, y=y, rotation=0, flip=0,
            properties=comp_properties
        )
        
        self.components.append(component)
        return component


def create_variant(circuit_type: str, variant_name: str, config: Dict[str, Any], 
                   tests: Dict[str, Dict[str, Any]], template_dir: str) -> tuple[str, str]:
    """Create complete circuit variant with testbenches"""
    folder = f"{circuit_type}_{variant_name}"
    short = config["short"]
    
    os.makedirs(f"{folder}/tb", exist_ok=True)
    
    # Build main schematic
    template = Path(f"{template_dir}/{circuit_type}.sch")
    schematic = XSchemInterface.load(template)
    for comp_name, properties in config["params"].items():
        schematic.update_component_properties(comp_name, properties)
    schematic.save(Path(f"{folder}/{circuit_type}_{short}.sch"))
    
    # Copy symbol
    symbol_template = Path(f"{template_dir}/{circuit_type}.sym")
    symbol = XSchemInterface.load(symbol_template)
    symbol.save(Path(f"{folder}/{circuit_type}_{short}.sym"))
    
    # Build testbenches
    template_tb = Path(f"{template_dir}/{circuit_type}_tb.sch")
    
    for test_name, test_config in tests.items():
        testbench = XSchemInterface.load(template_tb)
        
        # Update DUT reference
        old_ref = f"{circuit_type}s/template/{circuit_type}.sym"
        new_ref = f"{circuit_type}s/{folder}/{circuit_type}_{short}.sym"
        dut = testbench.find_component_by_symbol(old_ref)
        if dut:
            dut.symbolReference = new_ref
        
        # Configure test setup
        for key, value in test_config.items():
            if key == "spice":
                spice_comp = testbench.ensure_spice_setup()
                spice_comp.properties["value"] = value
            else:
                comp_name = key.split('_')[-1].upper() if '_' in key else key.upper()
                testbench.update_component_properties(comp_name, {"value": value})
        
        # Save testbench
        tb_file = f"{folder}/tb/{circuit_type}_{short}_{test_name}_tb.sch"
        testbench.save(Path(tb_file))
    
    return folder, short


def build_and_simulate_variants(variants: Dict[str, Dict[str, Any]], 
                               tests: Dict[str, Dict[str, Any]], 
                               circuit_type: str,
                               template_dir: str,
                               units_map: Dict[str, str],
                               with_documentation: bool = True) -> Dict[str, Dict[str, Any]]:
    """
    Complete workflow: build variants, simulate, and generate docs
    
    Args:
        variants: Variant specifications {name: {short: str, params: dict}}
        tests: Test configurations {test_name: {config}}
        circuit_type: Circuit type (e.g., "OpAmp", "TIA")
        template_dir: Template directory
        units_map: Metric units mapping for documentation
        with_documentation: Whether to generate documentation

    Returns:
        Simulation results for all variants
    """
    simulator = SimulationRunner()
    results = {}
    metric_keywords = list(units_map.keys())
    
    for name, info in variants.items():
        folder, short = create_variant(circuit_type, name, info, tests, template_dir)

        variant_results = {}
        for test_name in tests:
            tb_file = f"{folder}/tb/{circuit_type}_{short}_{test_name}_tb.sch"
            variant_results[test_name] = simulator.run_simulation(tb_file, metric_keywords=metric_keywords)
        
        # Generate documentation
        if with_documentation:
            DocumentationGenerator.create_readme(
                folder, name, short, info["params"], variant_results, 
                circuit_type, units_map
            )
        
        results[name] = variant_results
    
    return results
