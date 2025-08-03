from typing import Dict, Any, Optional

class DocumentationGenerator:
    """Handles README generation with proper formatting"""
    
    @staticmethod
    def create_readme(folder: str, name: str, short: str, params: Dict[str, Dict[str, str]], 
                     results: Dict[str, Any], component_type: str = "Component",
                     units_map: Optional[Dict[str, str]] = None):
        """Create a comprehensive README for the variant"""
        
        with open(f"{folder}/README.md", "w") as f:
            f.write(f"# {name} {component_type} ({short})\n\n")
            
            # Parameters section
            f.write("## Parameters\n")
            for component, component_params in params.items():
                param_str = ", ".join([f"{k}={v}" for k, v in component_params.items()])
                f.write(f"- {component}: {param_str}\n")
            
            # Results section
            f.write("\n## Simulation Results\n")
            for test, res in results.items():
                f.write(f"### {test.replace('_', ' ').title()}\n")
                if isinstance(res, dict) and "error" not in res:
                    for metric, value in res.items():
                        unit = units_map.get(metric, '')
                        if unit:
                            f.write(f"- {metric}: {value:.6g} {unit}\n")
                        else:
                            f.write(f"- {metric}: {value:.6g}\n")
                else:
                    f.write(f"- Result: {res}\n")
                f.write("\n")


