from Grammar import *
from typing import List, Dict, Union
from pathlib import Path

class XSchemWriter:
    @staticmethod
    def format_number(value) -> str:
        """Format numeric values, removing .0 for integers"""
        if isinstance(value, (int, float)):
            if float(value).is_integer():
                return str(int(value))
            else:
                return str(value)
        return str(value)

    @staticmethod
    def format_properties(properties: Dict[str, str]) -> str:
        """Format properties dictionary into XSchem property string"""
        if not properties:
            return "{}"
        
        pairs = []
        for key, value in properties.items():
            # Quote values that contain spaces, special characters, or are empty
            if not value or ' ' in value or any(c in value for c in '{}="\\'):
                # Escape quotes and backslashes in the value
                escaped_value = value.replace('\\', '\\\\').replace('"', '\\"')
                pairs.append(f'{key}="{escaped_value}"')
            else:
                pairs.append(f"{key}={value}")
        
        if len(pairs) > 2:
            return "{" + "\n".join(pairs) + "\n}"
        else:
            return "{" + " ".join(pairs) + "}"
    
    @staticmethod
    def write_object(obj: XSchemObject) -> str:
        """Convert an XSchem object to its string representation"""
        
        if isinstance(obj, Version):
            # Version block can be multiline - include the license text properly
            version_line = f"xschem version={obj.version} file_version={obj.fileVersion}"
            if obj.license and obj.license.strip():
                # If there's additional license text beyond the version line
                return f"v {{{obj.license}\n}}"
            else:
                return f"v {{{version_line}\n}}"
        
        elif isinstance(obj, Line):
            props = XSchemWriter.format_properties(obj.properties)
            return f"L {obj.layer} {XSchemWriter.format_number(obj.x1)} {XSchemWriter.format_number(obj.y1)} {XSchemWriter.format_number(obj.x2)} {XSchemWriter.format_number(obj.y2)} {props}"
        
        elif isinstance(obj, Rectangle):
            props = XSchemWriter.format_properties(obj.properties)
            return f"B {obj.layer} {XSchemWriter.format_number(obj.x1)} {XSchemWriter.format_number(obj.y1)} {XSchemWriter.format_number(obj.x2)} {XSchemWriter.format_number(obj.y2)} {props}"
        
        elif isinstance(obj, Arc):
            props = XSchemWriter.format_properties(obj.properties)
            return f"A {obj.layer} {XSchemWriter.format_number(obj.centerX)} {XSchemWriter.format_number(obj.centerY)} {XSchemWriter.format_number(obj.radius)} {XSchemWriter.format_number(obj.startAngle)} {XSchemWriter.format_number(obj.sweepAngle)} {props}"
        
        elif isinstance(obj, Polygon):
            # Use the property method for pointCount
            coords = []
            for point in obj.points:
                coords.extend([XSchemWriter.format_number(point.x), XSchemWriter.format_number(point.y)])
            coord_str = " ".join(coords)
            props = XSchemWriter.format_properties(obj.properties)
            return f"P {obj.layer} {obj.pointCount} {coord_str} {props}"
        
        elif isinstance(obj, Wire):
            props = XSchemWriter.format_properties(obj.properties)
            return f"N {XSchemWriter.format_number(obj.x1)} {XSchemWriter.format_number(obj.y1)} {XSchemWriter.format_number(obj.x2)} {XSchemWriter.format_number(obj.y2)} {props}"
        
        elif isinstance(obj, Component):
            props = XSchemWriter.format_properties(obj.properties)
            return f"C {{{obj.symbolReference}}} {XSchemWriter.format_number(obj.x)} {XSchemWriter.format_number(obj.y)} {obj.rotation} {obj.flip} {props}"
        
        elif isinstance(obj, Text):
            props = XSchemWriter.format_properties(obj.properties)
            return f"T {{{obj.text}}} {XSchemWriter.format_number(obj.x)} {XSchemWriter.format_number(obj.y)} {obj.rotation} {obj.mirror} {obj.hSize} {obj.vSize} {props}"
        
        elif isinstance(obj, Spice):
            # Handle multiline content properly
            if '\n' in obj.content or '{' in obj.content or '}' in obj.content:
                return f"S {{{obj.content}}}"
            else:
                return f"S {{{obj.content}}}"
        
        elif isinstance(obj, Verilog):
            return f"V {{{obj.content}}}"
        
        elif isinstance(obj, VHDL):
            return f"G {{{obj.content}}}"
        
        elif isinstance(obj, TEDAx):
            return f"E {{{obj.content}}}"
        
        elif isinstance(obj, GlobalProperties):
            props = XSchemWriter.format_properties(obj.properties)
            return f"K {props}"
        
        elif isinstance(obj, EmbeddedSymbol):
            # Recursively write the embedded symbol
            embedded_content = []
            for sub_obj in obj.symbol:
                line = XSchemWriter.write_object(sub_obj)
                if line:
                    embedded_content.append(line)
            content = '\n'.join(embedded_content)
            return f"[\n{content}\n]"
        
        return ""
    
    @staticmethod
    def write_file(objects: List[XSchemObject], file_path: Union[str, Path]) -> None:
        """Write XSchem objects to a file"""
        content = XSchemWriter.write_content(objects)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    @staticmethod
    def write_content(objects: List[XSchemObject]) -> str:
        """Convert a list of XSchem objects to file content"""
        lines = []
        for obj in objects:
            line = XSchemWriter.write_object(obj)
            if line:
                lines.append(line)
        
        # Ensure file ends with a newline
        content = '\n'.join(lines)
        if content and not content.endswith('\n'):
            content += '\n'
        
        return content
