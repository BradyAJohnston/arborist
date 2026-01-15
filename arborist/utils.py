from bpy.types import Context, NodeTree
import bpy


def active_nodetree(context: Context | None = None) -> NodeTree:
    if context is None:
        context = bpy.context
    return context.space_data.edit_tree  # type: ignore
