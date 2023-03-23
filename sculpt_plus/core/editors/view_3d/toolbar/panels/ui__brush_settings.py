from ._dummy import DummyPanel

from bl_ui.space_toolsystem_common import ToolSelectPanelHelper
from bl_ui.properties_paint_common import brush_settings, brush_settings_advanced, brush_texture_settings, StrokePanel, FalloffPanel, SmoothStrokePanel
from bpy.types import UILayout

from sculpt_plus.props import Props


def draw_brush_settings_tabs(layout, context):
    # BRUSH SETTINGS.
    from sculpt_plus.core.data.wm import SCULPTPLUS_PG_ui_toggles
    ui_props: SCULPTPLUS_PG_ui_toggles = Props.UI(context)
    ui_section: str = ui_props.toolbar_brush_sections

    sculpt = context.tool_settings.sculpt
    act_brush = sculpt.brush

    col_2 = layout.column(align=True)
    col_2.use_property_split = True

    header = col_2.box().row(align=True)
    header.scale_y = 1.5
    header.use_property_split = False
    space_type, mode = ToolSelectPanelHelper._tool_key_from_context(context)
    cls = ToolSelectPanelHelper._tool_class_from_space_type(space_type)
    item, tool, icon_value = cls._tool_get_active(context, space_type, mode, with_icon=True)
    if item is None:
        return None
    label_text = act_brush.name # iface_(item.label, "Operator")
    # header.label(text="    " + label_text, icon_value=icon_value)
    header.label(text="", icon_value=icon_value)
    tri_icon = 'TRIA_DOWN' if ui_props.show_brush_settings_panel else 'TRIA_LEFT'
    header.prop(ui_props, 'show_brush_settings_panel', expand=True, text=label_text+" Brush", emboss=False)
    header.prop(ui_props, 'show_brush_settings_panel', expand=True, text="", icon=tri_icon, emboss=False)

    if not ui_props.show_brush_settings_panel:
        return

    selector = col_2.grid_flow(align=True, columns=0)
    selector.use_property_split = False
    selector.scale_y = 1.35
    selector.prop(ui_props, 'toolbar_brush_sections', text="", expand=True)

    selector_line_bot = col_2.box()#.column(align=True)
    selector_line_bot.ui_units_y = 0.1

    content = col_2.box().column(align=False if ui_section in {'BRUSH_SETTINGS', 'BRUSH_SETTINGS_FALLOFF'} else True)
    content.separator()

    if ui_section == 'BRUSH_SETTINGS':
        brush_settings(content, context, act_brush)
    elif ui_section == 'BRUSH_SETTINGS_ADVANCED':
        content.use_property_split = False
        brush_settings_advanced(content, context, act_brush)
    elif ui_section == 'BRUSH_SETTINGS_STROKE':
        StrokePanel.draw(DummyPanel(content), context)
        #SmoothStrokePanel.draw_header(dummy_panel, context)
        content.separator()
        content = content.column(align=True)
        row = content.box().row(align=True)
        row.use_property_split = False
        row.alignment = 'LEFT'
        row.prop(act_brush, "use_smooth_stroke", text="Stabilize Stroke")
        if act_brush.use_smooth_stroke: SmoothStrokePanel.draw(DummyPanel(content.box()), context)
    elif ui_section == 'BRUSH_SETTINGS_FALLOFF':
        FalloffPanel.draw(DummyPanel(content), context)
    elif ui_section == 'BRUSH_SETTINGS_TEXTURE':
        # content.template_icon(icon_value=UILayout.icon(act_brush.texture.image), scale=5.0)
        content.template_icon(icon_value=UILayout.icon(act_brush.texture), scale=5.0)
        brush_texture_settings(content, act_brush, sculpt=True)

    content.separator(factor=0.5)

def draw_brush_settings_expandable(layout, context):
    # BRUSH SETTINGS.
    from sculpt_plus.core.data.wm import SCULPTPLUS_PG_ui_toggles
    ui_props: SCULPTPLUS_PG_ui_toggles = Props.UI(context)

    sculpt = context.tool_settings.sculpt
    act_brush = sculpt.brush

    col_2 = layout.column()
    col_2.use_property_split = True

    section = col_2.column(align=True)
    header = section.row(align=True)
    header.use_property_split = False
    header.box().label(text='', icon='BRUSH_DATA')
    icon = 'TRIA_DOWN' if ui_props.show_brush_settings else 'TRIA_RIGHT'
    header_toggle = header.box().row(align=True)
    header_toggle.emboss = 'NONE'
    header_toggle.prop(ui_props, 'show_brush_settings', text="Brush Settings", toggle=False)
    header_toggle.prop(ui_props, 'show_brush_settings', text="", icon=icon, toggle=False)
    if ui_props.show_brush_settings:
        brush_settings(section.box(), context, act_brush)
        icon = 'TRIA_DOWN' if ui_props.show_brush_settings_advanced else 'TRIA_RIGHT'
        header = section.row(align=True)
        header.use_property_split = False
        header.box().label(text='', icon='GHOST_ENABLED') # PROP_CON')
        header_toggle = header.box().row(align=True)
        header_toggle.emboss = 'NONE'
        header_toggle.prop(ui_props, 'show_brush_settings_advanced', text="Advanced", toggle=False)
        header_toggle.prop(ui_props, 'show_brush_settings_advanced', text="", icon=icon, toggle=False)
        if ui_props.show_brush_settings_advanced:
            brush_settings_advanced(section.box(), context, act_brush)

    col_2.separator()

    section = col_2.column(align=True)
    header = section.row(align=True)
    header.use_property_split = False
    header.box().label(text='', icon='GP_SELECT_STROKES')
    icon = 'TRIA_DOWN' if ui_props.show_brush_settings_stroke else 'TRIA_RIGHT'
    header_toggle = header.box().row(align=True)
    header_toggle.emboss = 'NONE'
    header_toggle.prop(ui_props, 'show_brush_settings_stroke', text="Stroke Settings", toggle=False)
    header_toggle.prop(ui_props, 'show_brush_settings_stroke', text="", icon=icon, toggle=False)
    if ui_props.show_brush_settings_stroke:
        StrokePanel.draw(DummyPanel(section.box()), context)

    col_2.separator()

    section = col_2.column(align=True)
    header = section.row(align=True)
    header.use_property_split = False
    header.box().label(text='', icon='SMOOTHCURVE')
    icon = 'TRIA_DOWN' if ui_props.show_brush_settings_falloff else 'TRIA_RIGHT'
    header_toggle = header.box().row(align=True)
    header_toggle.emboss = 'NONE'
    header_toggle.prop(ui_props, 'show_brush_settings_falloff', text="Falloff Settings", toggle=False)
    header_toggle.prop(ui_props, 'show_brush_settings_falloff', text="", icon=icon, toggle=False)
    if ui_props.show_brush_settings_falloff:
        FalloffPanel.draw(DummyPanel(section.box()), context)
    if act_brush.texture is None:
        return

    col_2.separator()

    section = col_2.column(align=True)
    header = section.row(align=True)
    header.use_property_split = False
    header.box().label(text='', icon='TEXTURE_DATA')
    icon = 'TRIA_DOWN' if ui_props.show_brush_settings_texture else 'TRIA_RIGHT'
    header_toggle = header.box().row(align=True)
    header_toggle.emboss = 'NONE'
    header_toggle.prop(ui_props, 'show_brush_settings_texture', text="Texture Settings", toggle=False)
    header_toggle.prop(ui_props, 'show_brush_settings_texture', text="", icon=icon, toggle=False)
    if ui_props.show_brush_settings_texture:
        brush_texture_settings(section.box(), act_brush, sculpt=True)
