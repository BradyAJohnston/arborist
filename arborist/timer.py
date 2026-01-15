import bpy
from .props import props
from pathlib import Path

def some_function():
    """Function to call when file has changed"""
    print("File has been updated - processing changes...")
    # Add your custom logic here

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
            some_function()
            p.file_last_modified = current_mtime
            
    except (OSError, ValueError) as e:
        print(f"Error checking file: {e}")
        return 1.0
    
    return 0.1

def register():
    bpy.app.timers.register(reload_timer)

def unregister():
    bpy.app.timers.unregister(reload_timer)