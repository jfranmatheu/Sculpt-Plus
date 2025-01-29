# We're doing this as a HACK because of a Blender BUG: https://projects.blender.org/blender/blender/issues/98598
# Instead of using the Gizmo.draw to draw this...

import bpy
from bpy.types import SpaceView3D



draw_handler = None


def draw_callback():
    from .reg import Controller
    context= bpy.context
    if not Controller.poll(context):
        return
    bpy.sculpt_hotbar.get_cv(context).draw(context)


def register():
    global draw_handler
    draw_handler = SpaceView3D.draw_handler_add(draw_callback, (), 'WINDOW', 'POST_PIXEL')


def unregister():
    global draw_handler
    if draw_handler is not None:
        SpaceView3D.draw_handler_remove(draw_handler, 'WINDOW')
        draw_handler = None
