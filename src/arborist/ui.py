import time
from bpy.types import Panel, Context, UILayout
from bpy.utils import register_class, unregister_class
from . import props


class AR_PT_DefaultPanel(Panel):
    bl_idname = "ARBORIST_PT_main_panel"
    bl_label = "Arborist"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Arborist"

    @classmethod
    def poll(cls, context: Context) -> bool:
        return True

    def draw(self, context: Context):
        layout: UILayout = self.layout  # type: ignore
        p = props.props(context)

        layout.template_ID(p, "node_group", new="object.geometry_node_tree_copy_assign")

        layout.separator()

        # Source selection
        layout.label(text="Script Source")
        layout.props_enum(p, "import_type")
        match p.import_type:
            case "file":
                layout.prop(p, "file_path")
            case "text":
                layout.prop(p, "text_block")

        layout.separator()

        # Auto-reload toggle (only meaningful for file mode)
        row = layout.row()
        row.prop(p, "is_updating", text="Auto Reload")
        if p.import_type == "text":
            row.enabled = False

        layout.separator()

        # Manual run button
        run_row = layout.row()
        run_row.scale_y = 1.4
        run_row.operator("arborist.run_script", text="Run Script", icon="PLAY")

        layout.separator()

        # Execution status box
        box = layout.box()
        box.label(text="Last Execution", icon="INFO")

        if p.last_executed_time == 0:
            box.label(text="Never executed", icon="RADIOBUT_OFF")
        else:
            # Format timestamp relative to now
            elapsed = int(time.time()) - p.last_executed_time
            if elapsed < 60:
                time_str = f"{elapsed}s ago"
            elif elapsed < 3600:
                time_str = f"{elapsed // 60}m {elapsed % 60}s ago"
            else:
                time_str = time.strftime(
                    "%H:%M:%S", time.localtime(p.last_executed_time)
                )

            status_icon = "CHECKMARK" if p.last_status == "success" else "ERROR"
            status_text = "Success" if p.last_status == "success" else "Error"
            box.label(text=f"{status_text}  —  {time_str}", icon=status_icon)
            box.label(text=f"Run count: {p.run_count}")

            if p.last_status == "error" and p.last_error:
                err_box = box.box()
                err_box.alert = True
                # Word-wrap long error messages across multiple label rows
                for line in _wrap_text(p.last_error, 40):
                    err_box.label(text=line)

            if p.last_status == "success" and p.last_output:
                out_box = box.box()
                out_box.label(text="Output:", icon="OUTPUT")
                for line in p.last_output.splitlines()[:6]:
                    out_box.label(text=line)


def _wrap_text(text: str, width: int) -> list[str]:
    """Split text into lines no longer than width characters."""
    lines = []
    for paragraph in text.splitlines():
        while len(paragraph) > width:
            lines.append(paragraph[:width])
            paragraph = paragraph[width:]
        lines.append(paragraph)
    return lines or [""]


CLASSES = (AR_PT_DefaultPanel,)


def register():
    for cls in CLASSES:
        register_class(cls)


def unregister():
    for cls in reversed(CLASSES):
        unregister_class(cls)
