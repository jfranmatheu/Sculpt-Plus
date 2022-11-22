''' handler.py
@persistent
def on_load_post(dummy):
    SCULPTPLUS_PG_brush_manager.get_data(bpy.context).setup()

def register():
    load_post.append(on_load_post)

def unregister():
    if on_load_post in load_post:
        load_post.remove(on_load_post)
'''


import bpy
from bpy.app.handlers import load_post, persistent


@persistent
def bm_on_load_post(dummy):
    from sculpt_plus.props import Props
    print("[SculptPlus] Initializing brush categories...")
    Props.BrushManager(bpy.context).init()

def register():
    load_post.append(bm_on_load_post)
    
def unregister():
    if bm_on_load_post in load_post:
        load_post.remove(bm_on_load_post)
