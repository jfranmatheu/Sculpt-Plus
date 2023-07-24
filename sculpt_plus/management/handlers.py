import atexit
from bpy.app.handlers import load_post, persistent


goodbye_check = False

@atexit.register
def goodbye():
    print("__goodbye__")
    global goodbye_check
    if goodbye_check:
        return
    goodbye_check = True

    from sculpt_plus.props import Props
    if Props.HotbarExists():
        # print("atexit:", Props.BrushManager())
        Props.HotbarSave()
        Props.HotbarDestroy()
        print("Goodbye!")


@persistent
def on_load_post(dummy):
    from sculpt_plus.props import Props
    if Props.HotbarExists():
        # print("on_load_post:", Props.BrushManager())
        print("[Sculpt +] Skipping database load. Brush Manager already exists!")
        return
    print("[Sculpt+] Loading database...")
    # print("on_load_post:", Props.BrushManager())

    # Init Workspace.
    # Props.Workspace()

    # Load Database.
    Props.HotbarLoad()


def register():
    load_post.append(on_load_post)

def unregister():
    if on_load_post in load_post:
        load_post.remove(on_load_post)
