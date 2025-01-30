from bl_ui.space_toolsystem_toolbar import VIEW3D_PT_tools_active, _defs_sculpt, _defs_transform, _defs_annotate
from bl_ui.space_toolsystem_common import ToolSelectPanelHelper, ToolDef

from ....props import Props


def draw_tool_settings(layout, context, active_tool, active_tool_id: str):
    ui_props = Props.UI(context)
    '''
    print(active_tool)
    print(dir(active_tool))
    print(dir(_defs_sculpt))
    print(dir(_defs_sculpt.cloth_filter))
    print(type(_defs_sculpt.cloth_filter))
    '''
    tool_type, tool_idname = active_tool.idname.split('.')
    if tool_type == 'builtin':
        if 'annotate' in tool_idname:
            defs_type = _defs_annotate
        elif tool_idname in {'move', 'scale', 'rotate', 'transform'}:
            defs_type = _defs_transform
        else:
            defs_type = _defs_sculpt
    else:
        defs_type = _defs_sculpt

    draw_settings = None
    for attr in dir(defs_type):
        if attr.startswith('_'):
            continue
        item = getattr(defs_type, attr)
        if type(item) != ToolDef:
            continue
        if item.idname != active_tool.idname:
            continue
        draw_settings = getattr(item, 'draw_settings', None)
        break

    section = layout.column(align=True)

    header = section.box().row(align=True)
    header.scale_y = 1.5
    header.emboss = 'NONE'
    space_type, mode = ToolSelectPanelHelper._tool_key_from_context(context)
    cls = ToolSelectPanelHelper._tool_class_from_space_type(space_type)
    item, tool, icon_value = cls._tool_get_active(context, space_type, mode, with_icon=True)
    if item is None:
        return None
    # header.label(text="    " + item.label, icon_value=icon_value)
    if draw_settings is None:
        header.label(text="    " + item.label, icon_value=icon_value)
        return
    
    header.label(text="", icon_value=icon_value)
    tri_icon = 'TRIA_DOWN' if ui_props.show_brush_settings_panel else 'TRIA_LEFT'
    header.prop(ui_props, 'show_brush_settings_panel', expand=True, text=item.label, emboss=False)
    header.prop(ui_props, 'show_brush_settings_panel', expand=True, text="", icon=tri_icon, emboss=False)

    if not ui_props.show_brush_settings_panel:
        return

    '''
    header = section.row(align=True)
    header.use_property_split = False
    header.box().label(text='', icon='SETTINGS')
    header_toggle = header.box().row(align=True)
    header_toggle.emboss = 'NONE'
    header_toggle.label(text="Tool Settings")
    '''
    content = section.box().column()
    draw_settings(context, content, active_tool)
