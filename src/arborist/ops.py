import bpy
from bpy.types import Operator


class ARBORIST_OT_dummy_operator(Operator):
    bl_idname = "arborist.dummy_operator"
    bl_label = "Dummy Operator"
    bl_description = "A placeholder operator for Arborist"

    def execute(self, context):
        self.report({"INFO"}, "Dummy operator executed")
        return {"FINISHED"}


CLASSES = (ARBORIST_OT_dummy_operator,)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
