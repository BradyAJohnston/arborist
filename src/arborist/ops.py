from pathlib import Path

import bpy
from bpy.props import EnumProperty
from bpy.types import Operator

from . import live, utils
from .props import props


class ARBORIST_OT_export_to_code(Operator):
    """Write nodebpy code for the open node tree into the script source"""

    bl_idname = "arborist.export_to_code"
    bl_label = "Export to Code"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        p = props(context)
        if p.selected_tree_only:
            return utils.selected_node_tree(context) is not None
        return utils.node_tree(context) is not None

    def execute(self, context):
        from nodebpy.export import to_python

        p = props(context)
        if p.selected_tree_only:
            tree = utils.selected_node_tree(context)
        else:
            tree = utils.node_tree(context)
        if tree is None:
            self.report({"ERROR"}, "No node tree to export")
            return {"CANCELLED"}

        try:
            code = to_python(
                tree,
                min_chain_length=p.min_chain_length,
                snapshot_positions=p.snapshot_positions,
                keep_reroutes=p.keep_reroutes,
                strict=p.strict,
                top_level="class" if p.selected_tree_only else "with",
                in_place=not p.selected_tree_only,
            )
        except Exception as e:
            self.report({"ERROR"}, f"Export failed: {e}")
            return {"CANCELLED"}

        if p.source == "FILE":
            if not p.file_path:
                self.report({"ERROR"}, "Choose a file path to export into")
                return {"CANCELLED"}
            path = Path(bpy.path.abspath(p.file_path))
            try:
                path.write_text(code)
            except OSError as e:
                self.report({"ERROR"}, f"Could not write {path}: {e}")
                return {"CANCELLED"}
            target = str(path)
        else:
            if p.text_block is None:
                p.text_block = bpy.data.texts.new(f"{tree.name}.py")
            p.text_block.from_string(code)
            target = p.text_block.name

        # The export is the current state of the tree; don't re-run it.
        live.mark_seen(p)
        context.window_manager.clipboard = code
        self.report(
            {"INFO"},
            f"Exported '{tree.name}' ({len(code.splitlines())} lines) to {target}",
        )
        return {"FINISHED"}


class ARBORIST_OT_run_script(Operator):
    """Run the script and show the node tree it produces"""

    bl_idname = "arborist.run_script"
    bl_label = "Run Script"
    bl_options = {"REGISTER", "UNDO"}

    mode: EnumProperty(  # type: ignore
        name="Show As",
        items=(
            ("TREE", "Tree", "Open the produced tree in the editor"),
            (
                "GROUP",
                "Node Group",
                "Drop the produced tree into the open editor as a group node attached to the mouse cursor",
            ),
        ),
        default="TREE",
        options={"SKIP_SAVE"},
    )

    _mouse: tuple[int, int] | None = None

    def invoke(self, context, event):
        self._mouse = (event.mouse_x, event.mouse_y)
        return self.execute(context)

    def execute(self, context):
        p = props(context)
        result = live.execute(context)
        if result is None:
            self.report({"ERROR"}, p.last_error.strip().splitlines()[-1])
            return {"CANCELLED"}
        tree = result.tree
        if tree is None:
            self.report({"INFO"}, "Ran script (no node tree produced)")
            return {"FINISHED"}

        if self.mode == "GROUP":
            error = utils.drop_as_group(context, tree, self._mouse)
            if error:
                self.report({"ERROR"}, error)
                return {"CANCELLED"}
            self.report({"INFO"}, f"Dropped '{tree.name}' as a node group")
            return {"FINISHED"}

        if tree.bl_idname == "GeometryNodeTree":
            # Without this a geometry group built from Python never shows up
            # in the modifier's node-group selector.
            tree.is_modifier = True
        applied = utils.apply_to_object(context, tree) if p.apply_to_object else None
        utils.open_in_editor(context, tree, pin=applied is None)
        message = f"Ran script, showing '{tree.name}'"
        if applied is not None:
            message += f", applied to '{applied.name}'"
        elif p.apply_to_object:
            self.report(
                {"WARNING"},
                "Couldn't apply: needs a geometry tree and an object with modifiers",
            )
        self.report({"INFO"}, message)
        return {"FINISHED"}


class ARBORIST_OT_new_text(Operator):
    """Create a new text block for the script"""

    bl_idname = "arborist.new_text"
    bl_label = "New Script"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        p = props(context)
        text = bpy.data.texts.new("nodebpy_script.py")
        text.from_string("from nodebpy import geometry as g\n\n")
        p.text_block = text
        return {"FINISHED"}


CLASSES = (ARBORIST_OT_export_to_code, ARBORIST_OT_run_script, ARBORIST_OT_new_text)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
