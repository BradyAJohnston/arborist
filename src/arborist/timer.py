import bpy
from .props import props
from pathlib import Path
import ast
import sys
from io import StringIO

_lib_dir = str(Path(__file__).parent / "lib")


def execute_script():
    p = props()
    
    # Get source code based on import type
    if p.import_type == "file":
        if not p.file_path:
            print("No file path specified")
            return
        try:
            source_code = Path(p.file_path).read_text()
            source_name = p.file_path
        except Exception as e:
            print(f"Error reading file {p.file_path}: {e}")
            return
    elif p.import_type == "text":
        if not p.text_block:
            print("No text block specified")
            return
        source_code = p.text_block.as_string()
        source_name = p.text_block.name
    else:
        print("Invalid import type")
        return
    
    try:
        ast.parse(source_code)
    except SyntaxError as e:
        print(f"✗ Syntax error in {source_name}: {e}")
        return
    
    # Try to execute the code
    try:
        # Capture stdout during execution
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        
        # Create a namespace for execution
        exec_globals = {"__name__": "__main__", "bpy": bpy}
        
        # Execute the code
        exec(source_code, exec_globals)
        
        # Restore stdout and get captured output
        sys.stdout = old_stdout
        output = captured_output.getvalue()
        
        print(f"✓ Executed {source_name}")
        if output:
            print(f"Script output: {output}")
            
    except Exception as e:
        sys.stdout = old_stdout
        print(f"✗ Runtime error in {source_name}: {e}")
    finally:
        sys.stdout = old_stdout

def reload_timer():
    p = props()
    
    filepath = p.file_path
    
    if not p.is_updating or not filepath:
        return 1.0
    
    try:
        file_path = Path(filepath)
        if not file_path.exists():
            return 1.0
            
        current_mtime = int(file_path.stat().st_mtime)
        
        # Check if file has been modified since last check
        if current_mtime > p.file_last_modified:
            execute_script()
            p.file_last_modified = current_mtime
            
    except (OSError, ValueError) as e:
        print(f"Error checking file: {e}")
        return 1.0
    
    return 0.1

def register():
    if _lib_dir not in sys.path:
        sys.path.insert(0, _lib_dir)
    bpy.app.timers.register(reload_timer)

def unregister():
    bpy.app.timers.unregister(reload_timer)
    if _lib_dir in sys.path:
        sys.path.remove(_lib_dir)