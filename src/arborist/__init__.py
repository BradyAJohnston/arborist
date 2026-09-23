from . import live, ops, props, ui

MODULES = (props, ops, ui, live)


def register():
    for module in MODULES:
        module.register()


def unregister():
    for module in reversed(MODULES):
        module.unregister()
