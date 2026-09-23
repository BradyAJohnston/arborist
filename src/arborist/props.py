import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    IntProperty,
    PointerProperty,
    StringProperty,
)
from bpy.types import PropertyGroup, Text


class ArboristProperties(PropertyGroup):
    # ------------------------------------------------------------------ source
    source: EnumProperty(  # type: ignore
        name="Source",
        description="Where the nodebpy script lives",
        items=(
            ("TEXT", "Text", "A text block inside this .blend file"),
            ("FILE", "File", "A Python file on disk, editable from outside Blender"),
        ),
        default="TEXT",
    )
    text_block: PointerProperty(  # type: ignore
        name="Text",
        description="Text block holding the nodebpy script",
        type=Text,
    )
    file_path: StringProperty(  # type: ignore
        name="File",
        description="Python file holding the nodebpy script",
        default="",
        subtype="FILE_PATH",
    )
    auto_reload: BoolProperty(  # type: ignore
        name="Auto Reload",
        description="Re-run the script whenever the text block or file changes",
        default=False,
    )

    # ------------------------------------------------------------------ export
    selected_tree_only: BoolProperty(  # type: ignore
        name="Selected Group Only",
        description=(
            "Export the node tree referenced by the active selected group node "
            "as a reusable group class instead of the whole open tree"
        ),
        default=False,
    )
    min_chain_length: IntProperty(  # type: ignore
        name="Min Chain Length",
        description="Shortest run of nodes emitted as a >> pipeline",
        default=3,
        min=2,
        soft_max=20,
    )
    snapshot_positions: BoolProperty(  # type: ignore
        name="Snapshot Positions",
        description="Capture each node's authored location and restore it on rebuild",
        default=False,
    )
    keep_reroutes: BoolProperty(  # type: ignore
        name="Keep Reroutes",
        description="Preserve reroute nodes instead of collapsing them into direct links",
        default=False,
    )
    strict: BoolProperty(  # type: ignore
        name="Strict",
        description=(
            "Fail on nodes with no nodebpy equivalent; disable to emit "
            "placeholder comments and keep going"
        ),
        default=True,
    )

    # --------------------------------------------------------------------- run
    apply_to_object: BoolProperty(  # type: ignore
        name="Apply to Active Object",
        description=(
            "After running, add the produced geometry node tree as a Geometry "
            "Nodes modifier on the active object"
        ),
        default=False,
    )

    # ------------------------------------------------------------------ status
    last_executed_time: IntProperty(  # type: ignore
        name="Last Executed Time",
        description="Unix timestamp of the last script execution",
        default=0,
    )
    last_status: EnumProperty(  # type: ignore
        name="Last Status",
        items=(
            ("NONE", "Never Run", "Script has never been executed"),
            ("SUCCESS", "Success", "Last execution succeeded"),
            ("ERROR", "Error", "Last execution failed with an error"),
        ),
        default="NONE",
    )
    last_error: StringProperty(  # type: ignore
        name="Last Error",
        description="Traceback from the last failed execution",
        default="",
    )
    last_output: StringProperty(  # type: ignore
        name="Last Output",
        description="Captured stdout from the last execution",
        default="",
    )
    run_count: IntProperty(  # type: ignore
        name="Run Count",
        description="Number of times the script has been executed",
        default=0,
    )


def props(context: bpy.types.Context | None = None) -> ArboristProperties:
    if context is None:
        context = bpy.context
    return context.scene.arborist  # type: ignore


CLASSES = (ArboristProperties,)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Scene.arborist = PointerProperty(type=ArboristProperties)  # type: ignore


def unregister():
    del bpy.types.Scene.arborist  # type: ignore
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
