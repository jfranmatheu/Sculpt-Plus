from bl_ui.space_toolsystem_toolbar import VIEW3D_PT_tools_active


def draw_toolbar_pre(self, context):
    return
    act_brush = context.tool_settings.sculpt.brush
    self.layout.label(text=act_brush.name)

    self.layout.separator()

def draw_toolbar_post(self, context):
    return
    act_brush = context.tool_settings.sculpt.brush

    self.layout.separator()

    self.layout.prop(act_brush, 'size', slider=True)


def register():
    VIEW3D_PT_tools_active.prepend(draw_func=draw_toolbar_pre)
    VIEW3D_PT_tools_active.append(draw_func=draw_toolbar_post)

def unregister():
    VIEW3D_PT_tools_active.remove(draw_func=draw_toolbar_pre)
    VIEW3D_PT_tools_active.remove(draw_func=draw_toolbar_post)
