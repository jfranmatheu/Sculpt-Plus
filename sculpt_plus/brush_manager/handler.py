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