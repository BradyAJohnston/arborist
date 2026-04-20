from bpy.props import StringProperty, IntProperty, BoolProperty, PointerProperty, EnumProperty
from bpy.types import PropertyGroup, Text, GeometryNodeTree
import bpy


class ArboristProperties(PropertyGroup):
    file_path: StringProperty(  # type: ignore
        name="File Path",
        description="Path to the file",
        default="",
        subtype="FILE_PATH",
    )
    file_last_modified: IntProperty(  # type: ignore
        name="File Last Modified",
        description="Timestamp of the last modification of the file",
        default=0,
    )
    is_updating: BoolProperty(  # type: ignore
        name="Is Updating",
        description="Indicates if an update is in progress",
        default=False,
    )
    text_block: PointerProperty( # type: ignore
        name="Text",
        type=Text
    )
    import_type: EnumProperty( # type: ignore
        name="Method",
        items=(
            ("text", "Text", "Use a text block from within Blender"),
            ("file", "File", "Look at a file on disk")
        )
    )
    node_group: PointerProperty( # type: ignore
        name="Node Group",
        type=bpy.types.GeometryNodeTree
    )


def props(context: bpy.types.Context | None = None) -> ArboristProperties:
    if context is None:
        context = bpy.context
    return context.scene.ar  # type: ignore

CLASSES = (ArboristProperties,)

def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Scene.ar = bpy.props.PointerProperty(type=ArboristProperties)  # type: ignore


def unregister():
    del bpy.types.Scene.ar  # type: ignore
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
