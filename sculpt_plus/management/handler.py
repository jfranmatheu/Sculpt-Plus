import atexit

from bpy.app.handlers import load_post, persistent

goodbye_check = False

@atexit.register
def goodbye():
    global goodbye_check
    if goodbye_check:
        return
    print("Goodbye!")
    from sculpt_plus.props import Props
    # print("atexit:", Props.BrushManager())
    Props.BrushManager().save_all()
    goodbye_check = True

@persistent
def on_load_post(dummy):
    from sculpt_plus.props import Props
    if Props.BrushManagerExists():
        # print("on_load_post:", Props.BrushManager())
        print("[Sculpt +] Skipping database load. Brush Manager already exists!")
        return
    print("[Sculpt+] Loading database...")
    # print("on_load_post:", Props.BrushManager())
    Props.BrushManager().load_brushes_from_db()

def register():
    load_post.append(on_load_post)

def unregister():
    if on_load_post in load_post:
        load_post.remove(on_load_post)
