import bpy
from  bpy.types import Window, WorkSpace

def on_workspace_change():
    context = bpy.context
    window: Window = context.window
    workspace: WorkSpace = window.workspace

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
