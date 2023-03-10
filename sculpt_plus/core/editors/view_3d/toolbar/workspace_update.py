import bpy
from  bpy.types import Window, WorkSpace

from .override_tools import toggle_toolbar_tools


def on_workspace_change():
    context = bpy.context
    window: Window = context.window
    workspace: WorkSpace = window.workspace
    toggle_toolbar_tools(use_legacy='sculpt_plus' not in workspace)

owner = object()

def register():
    bpy.msgbus.subscribe_rna(
        key=(Window, 'workspace'),
        owner=owner,
        args=(),
        notify=on_workspace_change,
        options={'PERSISTENT'}
    )
    
def unregister():
    bpy.msgbus.clear_by_owner(owner)
