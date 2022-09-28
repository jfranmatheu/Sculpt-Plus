def gizmo_display_ext(self, context):
    if context.mode != 'SCULPT':
        return
    self.layout.prop(context.scene.sculpt_hotbar, 'show_gizmo_sculpt_hotbar', text="Sculpt Hotbar")

def register():
    from bpy.types import VIEW3D_PT_gizmo_display
    VIEW3D_PT_gizmo_display.prepend(gizmo_display_ext)

def unregister():
    from bpy.types import VIEW3D_PT_gizmo_display
    VIEW3D_PT_gizmo_display.remove(gizmo_display_ext)
