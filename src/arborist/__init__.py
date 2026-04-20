from . import ui, props, ops, timer


def register():
    for module in (props, ops, ui, timer):
        module.register()


def unregister():
    for module in (ui, ops, props, timer):
        module.unregister()
