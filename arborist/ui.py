from bpy.types import Panel, Context, UILayout
from bpy.utils import register_class, unregister_class
from .utils import active_nodetree
from . import props

# class needs to be defined for the node editor
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
        layout.label(text="Arborist Add-on Panel")
        # row = layout.row(align=True)
        layout.props_enum(p, "import_type")
        layout.prop(p, "is_updating")
        match p.import_type:
            case "file":
                layout.prop(p, "file_path")
            case "text":
                layout.prop(p, "text_block")
        # Additional UI elements can be added here


CLASSES = (AR_PT_DefaultPanel,)


def register():
    for cls in CLASSES:
        register_class(cls)


def unregister():
    for cls in reversed(CLASSES):
        unregister_class(cls)
