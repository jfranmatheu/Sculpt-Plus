from bl_ui.space_toolsystem_toolbar import VIEW3D_PT_tools_active
from bl_ui.space_toolsystem_common import ToolSelectPanelHelper
from bl_ui.properties_paint_common import brush_settings, brush_settings_advanced, brush_texture_settings, StrokePanel, FalloffPanel

from sculpt_plus.props import Props


def _layout_generator_single_row(layout, scale_y):
    col = layout.row(align=True)
    #col.scale_y = scale_y
    is_sep = False
    while True:
        if is_sep is True:
            col = layout.row(align=True)
            col.scale_y = scale_y
        elif is_sep is None:
            yield None
            return
        is_sep = yield col

def draw_cls(cls, layout, context, detect_layout=True, default_layout='COL', scale_y=1.75, spacing=0.25):
    # Use a classmethod so it can be called outside of a panel context.

    # XXX, this UI isn't very nice.
    # We might need to create new button types for this.
    # Since we probably want:
    # - tool-tips that include multiple key shortcuts.
    # - ability to click and hold to expose sub-tools.

    space_type = context.space_data.type
    tool_active_id = getattr(
        ToolSelectPanelHelper._tool_active_from_context(context, space_type),
        "idname", None,
    )

    if detect_layout:
        ui_gen, show_text = cls._layout_generator_detect_from_region(layout, context.region, scale_y)
    else:
        if default_layout == 'COL':
            ui_gen = ToolSelectPanelHelper._layout_generator_single_column(layout, scale_y)
        else:
            ui_gen = _layout_generator_single_row(layout, scale_y)
        show_text = True

    # Start iteration
    ui_gen.send(None)

    skip_draw_mask = True
    skip_draw_face_sets = True

    for item in cls.tools_from_context(context):
        if item is None:
            ui_gen.send(True)
            layout.separator(factor=spacing)
            continue

        if type(item) is tuple:
            is_active = False
            i = 0
            for i, sub_item in enumerate(item):
                if sub_item is None:
                    continue
                is_active = (sub_item.idname == tool_active_id)
                if is_active:
                    index = i
                    break
            del i, sub_item

            if is_active:
                # not ideal, write this every time :S
                cls._tool_group_active[item[0].idname] = index
            else:
                index = cls._tool_group_active_get_from_item(item)

            item = item[index]
            use_menu = True
        else:
            index = -1
            use_menu = False

        # SKIP first mask and face sets draw brushes.
        if 'builtin_brush' in item.idname:
            
            brush_name: str = item.idname.split('.')[1].replace(' ', '_').upper()
            if brush_name == 'MASK':
                if skip_draw_mask:
                    skip_draw_mask = False
                    continue
            elif brush_name == 'DRAW_FACE_SETS':
                if skip_draw_face_sets:
                    skip_draw_face_sets = False
                    continue
            else:
                continue

        is_active = (item.idname == tool_active_id)
        icon_value = ToolSelectPanelHelper._icon_value_from_icon_handle(item.icon)

        sub = ui_gen.send(False)

        if use_menu:
            sub.operator_menu_hold(
                "wm.tool_set_by_id",
                text=item.label if show_text else "",
                depress=is_active,
                menu="WM_MT_toolsystem_submenu",
                icon_value=icon_value,
            ).name = item.idname
        else:
            sub.operator(
                "wm.tool_set_by_id",
                text=item.label if show_text else "",
                depress=is_active,
                icon_value=icon_value,
            ).name = item.idname
    # Signal to finish any remaining layout edits.
    ui_gen.send(None)

def draw_toolbar(self, context):
    if context.mode != 'SCULPT':
        self.draw_cls(self.layout, context)
        return

    # toolbar_is_wide_open
    if context.region.width <= 96:
        draw_cls(VIEW3D_PT_tools_active, self.layout, context, spacing=0.1)
        return

    from sculpt_plus.core.data.wm import SCULPTPLUS_PG_ui_toggles
    ui_props: SCULPTPLUS_PG_ui_toggles = Props.UI(context)

    sculpt = context.tool_settings.sculpt
    act_brush = sculpt.brush

    layout = self.layout
    factor = 1.0 - (context.region.width - 96/2) / context.region.width
    row = layout.split(align=False, factor=factor)

    col_1 = row.column(align=False)

    # DYN-SEP.
    prefs = context.preferences
    reg = context.region
    view_scroll_y = -reg.view2d.region_to_view(0, reg.height-1)[1]
    ui_scale = prefs.view.ui_scale
    line_height_px = 40 * ui_scale
    offset_factor_y = view_scroll_y / line_height_px
    sep = col_1.column(align=True)
    sep.label(text='', icon='BLANK1')
    sep.scale_y = (offset_factor_y-.05) * 2.0

    # TOOLBAR.
    toolbar = col_1.column(align=True)
    draw_cls(VIEW3D_PT_tools_active, toolbar, context, spacing=1.0) # row, context, detect_layout=False, default_layout='ROW', scale_y=1.35

    # BRUSH SETTINGS.
    col_2 = row.column()
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
        header.box().label(text='', icon='PROP_CON')
        header_toggle = header.box().row(align=True)
        header_toggle.emboss = 'NONE'
        header_toggle.prop(ui_props, 'show_brush_settings_advanced', text="Advanced", toggle=False)
        header_toggle.prop(ui_props, 'show_brush_settings_advanced', text="", icon=icon, toggle=False)
        if ui_props.show_brush_settings_advanced:
            brush_settings_advanced(section.box(), context, act_brush)

    class DummyPanel(StrokePanel):
        def __init__(self, layout):
            self.layout = layout

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


def register():
    VIEW3D_PT_tools_active.draw = draw_toolbar

def unregister():
    pass
