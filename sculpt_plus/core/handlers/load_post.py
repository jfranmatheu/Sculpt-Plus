import bpy
from bpy.app.handlers import load_post, persistent
from bl_ui.space_toolsystem_toolbar import VIEW3D_PT_tools_active
from bl_ui.space_toolsystem_common import ToolDef

from typing import List, Dict

sculpt_tool_VS_brush_name: Dict[str, str] = {}

@persistent
def on_post_load(dummy):
    # global sculpt_tool_VS_brush_name
    # sculpt_tool_VS_brush_name = {b.sculpt_tool: b.name for b in bpy.data.brushes if b.use_paint_sculpt}


    from sculpt_plus.prefs import get_prefs
    if not get_prefs(bpy.context).first_time:
        return
    print("[Sculpt+] Installation complete!")
    get_prefs(bpy.context).first_time = False
    return
    print("[Sculpt+] Unregistering Sculpt brush tools...")
    from bpy.utils import unregister_tool
    tools: List[ToolDef] = list(VIEW3D_PT_tools_active.tools_from_context(bpy.context, mode='SCULPT'))
    for tool in tools:
        if 'builtin_brush' in tool.idname:
            # Unregister brush tools.
            unregister_tool(tool)
            unregistered_tools.append(tool)

def register():
    load_post.append(on_post_load)

def unregister():
    if on_post_load in load_post:
        load_post.remove(on_post_load)
