import bpy
from bpy.types import Operator
from . import timer


class ARBORIST_OT_run_script(Operator):
    bl_idname = "arborist.run_script"
    bl_label = "Run Script"
    bl_description = "Manually execute the arborist script now"

    def execute(self, context):
        timer.execute_script()
        from .props import props

        p = props(context)
        if p.last_status == "error":
            self.report({"ERROR"}, p.last_error)
        else:
            self.report({"INFO"}, "Script executed successfully")
        return {"FINISHED"}


CLASSES = (ARBORIST_OT_run_script,)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
