import time

from bpy.types import Context, Panel, UILayout
from bpy.utils import register_class, unregister_class

from .props import props

ERROR_LINES = 8


class ARBORIST_PT_main(Panel):
    bl_idname = "ARBORIST_PT_main"
    bl_label = "Arborist"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Arborist"

    def draw(self, context: Context):
        layout: UILayout = self.layout  # type: ignore
        p = props(context)

        # Source ---------------------------------------------------------
        col = layout.column(align=True)
        col.row(align=True).prop(p, "source", expand=True)
        if p.source == "FILE":
            col.prop(p, "file_path", text="")
        else:
            col.template_ID(p, "text_block", new="arborist.new_text")
        layout.prop(p, "auto_reload", icon="FILE_REFRESH")

        # Export ---------------------------------------------------------
        box = layout.box()
        box.operator("arborist.export_to_code", icon="EXPORT")
        col = box.column(align=True)
        col.prop(p, "selected_tree_only")
        col.prop(p, "min_chain_length")
        col.prop(p, "snapshot_positions")
        col.prop(p, "keep_reroutes")
        col.prop(p, "strict")

        # Run ------------------------------------------------------------
        box = layout.box()
        row = box.row(align=True)
        row.scale_y = 1.4
        row.operator("arborist.run_script", text="Run", icon="PLAY").mode = "TREE"
        row.operator(
            "arborist.run_script", text="Run as Group", icon="NODETREE"
        ).mode = "GROUP"
        if context.active_object is not None:
            box.prop(p, "apply_to_object")

        # Status ---------------------------------------------------------
        box = layout.box()
        if p.last_status == "NONE":
            box.label(text="Never run", icon="RADIOBUT_OFF")
            return

        elapsed = int(time.time()) - p.last_executed_time
        if elapsed < 60:
            when = f"{elapsed}s ago"
        elif elapsed < 3600:
            when = f"{elapsed // 60}m ago"
        else:
            when = time.strftime("%H:%M:%S", time.localtime(p.last_executed_time))
        if p.last_status == "SUCCESS":
            box.label(text=f"Success, {when} (run {p.run_count})", icon="CHECKMARK")
        else:
            box.alert = True
            box.label(text=f"Error, {when}", icon="ERROR")
            for line in p.last_error.strip().splitlines()[-ERROR_LINES:]:
                box.label(text=line.strip())
        if p.last_output:
            out = box.box()
            out.label(text="Output", icon="CONSOLE")
            for line in p.last_output.splitlines()[:ERROR_LINES]:
                out.label(text=line)


CLASSES = (ARBORIST_PT_main,)


def register():
    for cls in CLASSES:
        register_class(cls)


def unregister():
    for cls in reversed(CLASSES):
        unregister_class(cls)
