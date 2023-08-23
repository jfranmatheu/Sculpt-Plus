'''
import bpy
from bpy.app import timers
from bpy.types import Context, Area, SpaceView3D

from .override_tools import accept_brush_tools
from .override_region import toolbar_hidden_brush_tools
from sculpt_plus.props import Props, CM_UIContext
from sculpt_plus.globals import G


def check_sculpt_tool_updates():
    context = bpy.context

    # INVALID MODE!
    if context.mode != 'SCULPT':
        return 1.0

    # INVALID WORKSPACE!
    workspace = Props.Workspace(context)
    if workspace is None or context.workspace != workspace:
        return 1.0

    active_tool_type, active_tool_id = Props.SculptTool.get_from_context(context)
    stored_tool_id = Props.SculptTool.get_stored()

    # TOOL IS NONE! IDK WHY...
    if active_tool_type == 'NONE':
        return .5

    # NOTHING CHANGED!
    if active_tool_id == stored_tool_id:
        return .5

    active_is_brush = active_tool_type == 'builtin_brush'
    stored_is_brush = stored_tool_type == 'builtin_brush'

    print(f"Info! Changed tool from {active_tool_id} to {stored_tool_id}.")

    # NO BRUSH TOOL!
    if not active_is_brush:
        # Props.SculptTool.set_stored(None)
        return .5

    # BRUSH TOOL BUT OF SPECIAL TYPE.
    if active_tool_id in accept_brush_tools and active_is_brush:
        # Props.SculptTool.update_stored(context)
        return .5

    hidden_brush_tool_selected = active_tool_id in toolbar_hidden_brush_tools

    if hidden_brush_tool_selected:
        Props.SculptTool.set_stored(active_tool_id)

    return .5



def register():
    if not timers.is_registered(check_sculpt_tool_updates):
        timers.register(check_sculpt_tool_updates, persistent=True, first_interval=1.0)


def unregister():
    if timers.is_registered(check_sculpt_tool_updates):
        timers.unregister(check_sculpt_tool_updates)
'''
