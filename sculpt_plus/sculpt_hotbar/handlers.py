import bpy
from bpy.app.handlers import load_post, persistent


@persistent
def on_load_post(dummy):
    # print("ON LOAD POST - INIT BRUSHES!")
    bpy.context.scene.sculpt_hotbar.init_brushes()

def register():
    load_post.append(on_load_post)
    
def unregister():
    if on_load_post in load_post:
        load_post.remove(on_load_post)
