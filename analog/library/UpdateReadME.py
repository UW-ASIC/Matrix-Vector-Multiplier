#!/usr/bin/env python3
"""
================================================================================
WARNING: DO NOT CALL THIS SCRIPT EXPLICITLY!
================================================================================
This script is automatically run by GitHub Actions on every push.
Manual execution may result in unintended changes to README.md.

If you need to test this script locally, ensure you understand the consequences
and are prepared to review the generated README.md carefully.
================================================================================

This script generates the top-level README.md by:
1. Aggregating README.md files from all module directories (excluding tools/)
2. Appending the tools/README.md content verbatim at the bottom
"""

import os
from pathlib import Path
from typing import List, Tuple


def get_module_directories(root_dir: Path) -> List[Path]:
    """
    Get all module directories (directories containing README.md).
    Excludes: .git, .github, tools, and any hidden directories.
    
    Args:
        root_dir: Root directory to search
        
    Returns:
        List of module directory paths
    """
    module_dirs = []
    excluded = {'.git', '.github', 'tools'}
    
    for item in sorted(root_dir.iterdir()):
        # Skip excluded directories and hidden directories
        if not item.is_dir() or item.name in excluded or item.name.startswith('.'):
            continue
            
        # Check if directory has a README.md
        readme_path = item / 'README.md'
        if readme_path.exists():
            module_dirs.append(item)
    
    return module_dirs


def read_readme_content(readme_path: Path) -> str:
    """
    Read content from a README.md file.
    
    Args:
        readme_path: Path to README.md file
        
    Returns:
        Content of the README file, or empty string if file is empty/unreadable
    """
    try:
        content = readme_path.read_text(encoding='utf-8').strip()
        return content
    except Exception as e:
        print(f"Warning: Could not read {readme_path}: {e}")
        return ""


def generate_readme(root_dir: Path) -> str:
    """
    Generate the complete README.md content.
    
    Args:
        root_dir: Root directory of the library
        
    Returns:
        Generated README content
    """
    sections = []
    
    # Header section
    header = """### Official Analog Library for UWASIC

This repository exists as the official library that UWASIC's analog team will be using.

> **Note**: This README is auto-generated. Module information is aggregated from individual module READMEs.
> To update this file, modify the respective module's README.md and push your changes.

---

## Modules
"""
    sections.append(header.strip())
    
    # Get and process module directories
    module_dirs = get_module_directories(root_dir)
    
    if module_dirs:
        for module_dir in module_dirs:
            readme_path = module_dir / 'README.md'
            content = read_readme_content(readme_path)
            
            # Create section for this module
            module_section = f"\n### {module_dir.name}\n"
            
            if content:
                module_section += f"\n{content}\n"
            else:
                module_section += "\n*Documentation coming soon...*\n"
            
            sections.append(module_section.strip())
    else:
        sections.append("\n*No modules found*")
    
    sections.append("\n---\n")
    
    # Tools section (verbatim from tools/README.md)
    tools_readme = root_dir / 'tools' / 'README.md'
    sections.append("## Tools\n")
    
    if tools_readme.exists():
        tools_content = read_readme_content(tools_readme)
        if tools_content:
            sections.append(tools_content)
        else:
            sections.append("*Tools documentation coming soon...*")
    else:
        sections.append("*No tools/README.md found*")
    
    # Combine all sections
    return "\n\n".join(sections) + "\n"


def main():
    """Main entry point for the script."""
    # Get the script's directory (library root)
    script_dir = Path(__file__).parent.resolve()
    
    # Generate README content
    readme_content = generate_readme(script_dir)
    
    # Write to README.md
    readme_path = script_dir / 'README.md'
    readme_path.write_text(readme_content, encoding='utf-8')
    
    print(f"✓ Successfully updated {readme_path}")
    print(f"  - Found {len(get_module_directories(script_dir))} module(s)")


if __name__ == '__main__':
    main()
