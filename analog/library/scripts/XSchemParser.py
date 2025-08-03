from Grammar import *
from typing import List, Dict, Union, Optional

from pathlib import Path
import re

class XSchemParser:
    def __init__(self):
        pass
    
    def parse_properties(self, prop_str: str) -> Dict[str, str]:
        """Parse properties from a string like {key=value key2="quoted value"}"""
        if not prop_str or prop_str.strip() == "{}":
            return {}
        
        # Remove outer braces
        prop_str = prop_str.strip()
        if prop_str.startswith('{') and prop_str.endswith('}'):
            prop_str = prop_str[1:-1]
        
        properties = {}
        # Simple regex to find key=value pairs - now handles multiline
        pairs = re.findall(r'(\w+)\s*=\s*([^"\s}\n]+|"[^"]*")', prop_str, re.MULTILINE | re.DOTALL)
        for key, value in pairs:
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]  # Remove quotes
            properties[key] = value.strip()
        
        return properties
    
    def parse_content(self, content: str) -> List[XSchemObject]:
        """Parse the entire content of an XSchem file"""
        objects = []
        i = 0
        lines = content.split('\n')
        
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                i += 1
                continue
            
            # Check if this line starts a multi-line block (has unmatched braces)
            if '{' in line and line.count('{') != line.count('}'):
                # Collect the complete multi-line block
                full_content = line
                brace_count = line.count('{') - line.count('}')
                i += 1
                
                while i < len(lines) and brace_count > 0:
                    current_line = lines[i]
                    full_content += '\n' + current_line
                    brace_count += current_line.count('{') - current_line.count('}')
                    i += 1
                
                # Parse the complete block
                obj = self.parse_line(full_content)
                if obj:
                    objects.append(obj)
                i -= 1  # Adjust since we'll increment at the end
            else:
                # Single line - parse normally
                obj = self.parse_line(line)
                if obj:
                    objects.append(obj)
            
            i += 1
        
        return objects
    
    def parse_line(self, line: str) -> Optional[XSchemObject]:
        """Parse a single line (which may contain newlines if it was a multi-line block)"""
        line = line.strip()
        if not line:
            return None
            
        parts = line.split(None, 1)  # Split into command and rest
        if not parts:
            return None
        
        cmd = parts[0]
        rest = parts[1] if len(parts) > 1 else ""
        
        if cmd == 'v':
            # Version: v {xschem version=3.4.4 file_version=1.2 ...}
            match = re.match(r'\{(.*)\}', rest, re.DOTALL)
            if not match:
                return None
            
            content = match.group(1).strip()
            version_match = re.search(r'xschem\s+version=([0-9.A-Z]+)\s+file_version=([0-9.]+)', content)
            
            if version_match:
                return Version(
                    version=version_match.group(1),
                    fileVersion=version_match.group(2),
                    license=content
                )
        
        elif cmd == 'G':
            # VHDL: G {...}
            match = re.match(r'\{(.*)\}', rest, re.DOTALL)
            if match:
                return VHDL(content=match.group(1).strip())

        elif cmd == 'V':
            # Verilog: V {...}
            match = re.match(r'\{(.*)\}', rest, re.DOTALL)
            if match:
                return Verilog(content=match.group(1).strip())

        elif cmd == 'E':
            # TEDAx: E {...}
            match = re.match(r'\{(.*)\}', rest, re.DOTALL)
            if match:
                return TEDAx(content=match.group(1).strip())

        elif cmd == 'S':
            # Spice: S {...}
            match = re.match(r'\{(.*)\}', rest, re.DOTALL)
            if match:
                return Spice(content=match.group(1).strip())
        
        elif cmd in ['L', 'B', 'N']:
            # Line, Rectangle, Wire: cmd params {properties}
            parts = line.split()
            if cmd == 'L' and len(parts) >= 6:
                props_start = line.find('{')
                props = self.parse_properties(line[props_start:] if props_start != -1 else "{}")
                return Line(
                    layer=int(parts[1]),
                    x1=float(parts[2]),
                    y1=float(parts[3]),
                    x2=float(parts[4]),
                    y2=float(parts[5]),
                    properties=props
                )
            elif cmd == 'B' and len(parts) >= 6:
                props_start = line.find('{')
                props = self.parse_properties(line[props_start:] if props_start != -1 else "{}")
                return Rectangle(
                    layer=int(parts[1]),
                    x1=float(parts[2]),
                    y1=float(parts[3]),
                    x2=float(parts[4]),
                    y2=float(parts[5]),
                    properties=props
                )
            elif cmd == 'N' and len(parts) >= 5:
                props_start = line.find('{')
                props = self.parse_properties(line[props_start:] if props_start != -1 else "{}")
                return Wire(
                    x1=float(parts[1]),
                    y1=float(parts[2]),
                    x2=float(parts[3]),
                    y2=float(parts[4]),
                    properties=props
                )
        
        elif cmd == 'T':
            # Text: T {text} x y rotation mirror hSize vSize {properties}
            text_match = re.match(r'\{([^}]*)\}\s*(.*)', rest, re.DOTALL)
            if text_match:
                text_content = text_match.group(1)
                remaining = text_match.group(2)
                
                # Find last { for properties
                props_start = remaining.rfind('{')
                if props_start != -1:
                    coords_part = remaining[:props_start].strip()
                    props_part = remaining[props_start:]
                    coords = coords_part.split()
                    
                    if len(coords) >= 6:
                        props = self.parse_properties(props_part)
                        return Text(
                            text=text_content,
                            x=float(coords[0]),
                            y=float(coords[1]),
                            rotation=int(coords[2]),
                            mirror=int(coords[3]),
                            hSize=float(coords[4]),
                            vSize=float(coords[5]),
                            properties=props
                        )
        
        elif cmd == 'C':
            # Component: C {reference} x y rotation flip {properties}
            ref_match = re.match(r'\{([^}]*)\}\s*(.*)', rest, re.DOTALL)
            if ref_match:
                reference = ref_match.group(1)
                remaining = ref_match.group(2)
                
                # Find last { for properties
                props_start = remaining.rfind('{')
                if props_start != -1:
                    coords_part = remaining[:props_start].strip()
                    props_part = remaining[props_start:]
                    coords = coords_part.split()
                    
                    if len(coords) >= 4:
                        props = self.parse_properties(props_part)
                        return Component(
                            symbolReference=reference,
                            x=float(coords[0]),
                            y=float(coords[1]),
                            rotation=int(coords[2]),
                            flip=int(coords[3]),
                            properties=props
                        )
                else:
                    # No properties
                    coords = remaining.split()
                    if len(coords) >= 4:
                        return Component(
                            symbolReference=reference,
                            x=float(coords[0]),
                            y=float(coords[1]),
                            rotation=int(coords[2]),
                            flip=int(coords[3]),
                            properties={}
                        )
        
        elif cmd == 'K':
            # Global properties: K {properties}
            props_start = line.find('{')
            props = self.parse_properties(line[props_start:] if props_start != -1 else "{}")
            return GlobalProperties(properties=props)
        
        return None
    
    def parse_file(self, file_path: str) -> List[XSchemObject]:
        """Parse an XSchem file from disk"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return self.parse_content(content)
