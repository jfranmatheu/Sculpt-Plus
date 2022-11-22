from bpy.app.handlers import load_post, persistent


@persistent
def on_load_post(dummy):
    from sculpt_plus.props import Props
    print("[Sculpt+] Initializing brush categories...")
    # Props.BrushManager.get().init()
    print("[Sculpt+] Initializing texture categories...")
    # Props.TextureManager.get().init()


def register():
    load_post.append(on_load_post)
    
def unregister():
    if on_load_post in load_post:
        load_post.remove(on_load_post)
