from bl_ui.space_toolsystem_toolbar import VIEW3D_PT_tools_active, _defs_sculpt, _defs_transform, _defs_annotate
from bl_ui.space_toolsystem_common import ToolSelectPanelHelper, ToolDef
from bl_ui.properties_paint_common import brush_settings, brush_settings_advanced, brush_texture_settings, StrokePanel, FalloffPanel
from bl_ui.space_view3d import _draw_tool_settings_context_mode
from bl_ui.properties_data_modifier import DATA_PT_modifiers
from bpy.types import UILayout, Modifier, VIEW3D_PT_sculpt_voxel_remesh, VIEW3D_PT_sculpt_dyntopo
from bpy.app.translations import pgettext_tip as tip_
from bpy.app.translations import pgettext_iface as iface_
from time import time

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
    using_multires: bool = [True for mod in context.sculpt_object.modifiers if mod.type == 'MULTIRES'] != []
    using_dyntopo : bool = context.sculpt_object.use_dynamic_topology_sculpting

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

    dyntopo_tools = {'SIMPLIFY'}
    anti_dyntopo_tools = {'DRAW_FACE_SETS', 'BOX_FACE_SET', 'LASSO_FACE_SET', 'FACE_SET_EDIT', 'COLOR_FILTER', 'PAINT', 'SMEAR', 'MASK_BY_COLOR'}
    multires_tools = {'MULTIRES_DISPLACEMENT_ERASER', 'MULTIRES_DISPLACEMENT_SMEAR'}
    skip_first_brush = {'MASK', 'DRAW_FACE_SETS', 'MULTIRES_DISPLACEMENT_ERASER', 'MULTIRES_DISPLACEMENT_SMEAR', 'SIMPLIFY'}
    skipped_brushes = set()

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

        tool_idname: str = item.idname.split('.')[1].replace(' ', '_').upper()
        # SKIP first mask and face sets draw brushes.
        if 'builtin_brush' in item.idname:
            # Check if object has multires modifier.
            if tool_idname in skipped_brushes:
                pass
            elif tool_idname in skip_first_brush:
                skipped_brushes.add(tool_idname)
                continue
            else:
                continue

            if tool_idname in multires_tools and not using_multires:
                continue
            if tool_idname in dyntopo_tools and not using_dyntopo:
                continue

        if using_dyntopo and tool_idname in anti_dyntopo_tools:
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


timer = time()
def draw_toolbar(self, context):
    if context.mode != 'SCULPT':
        self.draw_cls(self.layout, context)
        return
    
    prefs = context.preferences
    ui_scale = prefs.system.ui_scale # prefs.view.ui_scale

    # toolbar_is_wide_open
    if context.region.width <= (96 * ui_scale):
        draw_cls(VIEW3D_PT_tools_active, self.layout, context, spacing=0.1)
        return

    layout = self.layout
    '''
    global timer
    if (preview := context.sculpt_object.id_data.preview) is None:
        preview = context.sculpt_object.id_data.preview_ensure()
        timer = time()
    elif not preview.is_icon_custom:
        if (time() - timer) > 1.0:
            preview.reload()
            timer = time()
    layout.box().template_icon(preview.icon_id, scale=10)
    '''

    space_type = context.space_data.type
    tool_active = VIEW3D_PT_tools_active._tool_active_from_context(context, space_type)
    tool_active_id: str = getattr(tool_active, "idname", None,)
    tool_active_type, tool_active_id = tool_active_id.split('.')
    tool_active_id = tool_active_id.replace(' ', '_').upper()

    # TOOLBAR LAYOUT.
    layout = self.layout
    factor = 1.0 - (context.region.width - (96*ui_scale)/2) / context.region.width
    row = layout.split(align=False, factor=factor)

    col_1 = row.column(align=False)

    # DYN-SEP.
    # prefs = context.preferences
    reg = context.region
    view_scroll_y = -reg.view2d.region_to_view(0, reg.height-1)[1]
    # ui_scale = prefs.system.ui_scale # prefs.view.ui_scale
    line_height_px = 40 * ui_scale
    offset_factor_y = view_scroll_y / line_height_px
    sep = col_1.column(align=True)
    sep.label(text='', icon='BLANK1')
    sep.scale_y = (offset_factor_y-.05) * 2.0

    # TOOLBAR.
    toolbar = col_1.column(align=True)
    draw_cls(VIEW3D_PT_tools_active, toolbar, context, spacing=1.0) # row, context, detect_layout=False, default_layout='ROW', scale_y=1.35

    if tool_active is None:
        return
    
    col_2 = row.column(align=False)

    # brush settings sections.
    if tool_active_type == 'builtin_brush':
        draw_brush_settings_tabs(col_2, context)
    else:
        draw_tool_settings(col_2, context, tool_active, tool_active_id)
    
    col_2.separator()
 
    draw_sculpt_sections(col_2, context)


def draw_tool_settings(layout, context, active_tool, active_tool_id: str):
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

    if draw_settings is None:
        print("nope")
        return

    section = layout.column(align=True)
    header = section.row(align=True)
    header.use_property_split = False
    header.box().label(text='', icon='SETTINGS')
    header_toggle = header.box().row(align=True)
    header_toggle.emboss = 'NONE'
    header_toggle.label(text="Tool Settings")
    content = section.box().column()
    draw_settings(context, content, active_tool)


class DummyPanel(StrokePanel):
    def __init__(self, layout):
        self.layout = layout


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
    space_type, mode = ToolSelectPanelHelper._tool_key_from_context(context)
    cls = ToolSelectPanelHelper._tool_class_from_space_type(space_type)
    item, tool, icon_value = cls._tool_get_active(context, space_type, mode, with_icon=True)
    if item is None:
        return None
    label_text = act_brush.name # iface_(item.label, "Operator")
    header.label(text="    " + label_text, icon_value=icon_value)

    selector = col_2.grid_flow(align=True, columns=0)
    selector.use_property_split = False
    selector.scale_y = 1.5
    selector.prop(ui_props, 'toolbar_brush_sections', text="", expand=True)

    content = col_2.box().column(align=False if ui_section in {'BRUSH_SETTINGS', 'BRUSH_SETTINGS_FALLOFF'} else True)
    content.separator()

    if ui_section == 'BRUSH_SETTINGS':
        brush_settings(content, context, act_brush)
    elif ui_section == 'BRUSH_SETTINGS_ADVANCED':
        brush_settings_advanced(content, context, act_brush)
    elif ui_section == 'BRUSH_SETTINGS_STROKE':
        StrokePanel.draw(DummyPanel(content), context)
    elif ui_section == 'BRUSH_SETTINGS_FALLOFF':
        FalloffPanel.draw(DummyPanel(content), context)
    elif ui_section == 'BRUSH_SETTINGS_TEXTURE':
        brush_texture_settings(content, act_brush, sculpt=True)

    content.separator()

def draw_brush_settings(layout, context):
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


def draw_sculpt_sections(layout: UILayout, context):
    ui = Props.UI(context)
    active_section: str = ui.toolbar_sculpt_sections
    header_label: str = UILayout.enum_item_description(ui, 'toolbar_sculpt_sections', active_section)
    header_icon: int = UILayout.enum_item_icon(ui, 'toolbar_sculpt_sections', active_section)

    section = layout.column(align=True)

    header = section.box().row(align=True)
    header.scale_y = 1.5
    header.label(text=header_label, icon_value=header_icon)

    selector = section.row(align=True)
    selector.use_property_split = False
    selector.scale_y = 1.5
    selector.prop(ui, 'toolbar_sculpt_sections', expand=True)

    content = section.box().column(align=False)
    content.separator()
    content.use_property_split = True
    content_args = (DummyPanel(content), context)

    if active_section == 'VOXEL_REMESH':
        VIEW3D_PT_sculpt_voxel_remesh.draw(*content_args)
    elif active_section == 'DYNTOPO':
        if not context.sculpt_object.use_dynamic_topology_sculpting:
            msg = content.box()
            msg.scale_y = 1.5
            msg.label(text="You should enable Dyntopo!", icon='INFO')
            msg.operator("sculpt.dynamic_topology_toggle", text="Enable Dyntopo")
            return
        else:
            VIEW3D_PT_sculpt_dyntopo.draw(*content_args)
            content.separator()
            op = content.row()
            op.scale_y = 1.5
            op.alert = True
            op.operator("sculpt.dynamic_topology_toggle", text="Disable Dyntopo")
    else:
        # content.template_modifiers()
        ob = context.sculpt_object
        # print([m.type for m in ob.modifiers])
        md: Modifier = None
        for mod in ob.modifiers:
            if mod.type == 'MULTIRES':
                md: Modifier = mod
                break

        if md is None:
            msg = content.box()
            msg.scale_y = 1.5
            msg.label(text="No Multires Modifier", icon='INFO')
            msg.operator('object.modifier_add', text="Add Multires Modifier").type = 'MULTIRES'
            return
        
        mod: Modifier = mod
        
        levels_col = content.column(align=True)
        levels_col.prop(mod, 'levels')
        levels_col.prop(mod, 'sculpt_levels')
        levels_col.prop(mod, 'render_levels')
        
        content.prop(mod, 'use_sculpt_base_mesh')
        content.separator()
        content.prop(mod, 'show_only_control_edges')

        # DATA_PT_modifiers.draw(*content_args)
        


    content.separator()


def register():
    VIEW3D_PT_tools_active.draw = draw_toolbar

def unregister():
    pass
