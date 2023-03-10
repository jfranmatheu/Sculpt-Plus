from bl_ui.space_toolsystem_toolbar import VIEW3D_PT_tools_active
from bl_ui.space_toolsystem_common import ToolSelectPanelHelper, ToolDef

from time import time

from sculpt_plus.props import Props, toolbar_hidden_brush_tools
from sculpt_plus.prefs import get_prefs
from sculpt_plus.core.data.cy_structs import CyBlStruct
from .panels import *


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
    
    use_legacy_sculpt = 'sculpt_plus' not in context.workspace

    # XXX, this UI isn't very nice.
    # We might need to create new button types for this.
    # Since we probably want:
    # - tool-tips that include multiple key shortcuts.
    # - ability to click and hold to expose sub-tools.
    using_multires: bool = [True for mod in context.sculpt_object.modifiers if mod.type == 'MULTIRES'] != []
    using_dyntopo : bool = context.sculpt_object.use_dynamic_topology_sculpting

    space_type = context.space_data.type
    active_tool = ToolSelectPanelHelper._tool_active_from_context(context, space_type)
    tool_active_id = getattr(
        active_tool,
        "idname", None,
    )
    # active_tool_label = getattr(active_tool, 'label', None)
    manager_active_sculpt_tool = Props.BrushManager().active_sculpt_tool
    toolbar_active_sculpt_tool = tool_active_id.split('.')[1].replace(' ', '_').upper()

    active_is_brush = tool_active_id.split('.')[0] == 'builtin_brush'
    active_id = tool_active_id.split('.')[1].replace(' ', '_').upper()
    hidden_brush_tool_selected = active_id in toolbar_hidden_brush_tools

    manager_selected_brush = manager_active_sculpt_tool == toolbar_active_sculpt_tool
    # print(manager_active_sculpt_tool, toolbar_active_sculpt_tool)
    # print(manager_selected_brush, hidden_brush_tool_selected)
    #all_brush_active = manager_active_sculpt_tool == 'ALL_BRUSH' and toolbar_active_sculpt_tool == manager_active_sculpt_tool

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

    tools_from_context = cls.tools_from_context(context)
    for item in tools_from_context:
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

        is_active = (item.idname == tool_active_id)

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
                if tool_idname == 'ALL_BRUSH':
                    if not is_active and manager_active_sculpt_tool and manager_selected_brush and hidden_brush_tool_selected:
                        is_active = True
                else:
                    continue

            if tool_idname in multires_tools and not using_multires:
                continue
            if tool_idname in dyntopo_tools and not using_dyntopo:
                continue

        if using_dyntopo and tool_idname in anti_dyntopo_tools:
            continue

        icon_value = ToolSelectPanelHelper._icon_value_from_icon_handle(item.icon)

        sub = ui_gen.send(False)

        if tool_idname == 'ALL_BRUSH':
            sub.scale_y = 1.75
            sub.operator(
                "sculpt_plus.all_brush_tool",
                text=" ",
                depress=is_active,
                icon_value=icon_value,
                emboss=True
            )
        elif use_menu:
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
    if context.mode != 'SCULPT' or 'sculpt_plus' not in context.workspace:
        VIEW3D_PT_tools_active.draw_cls(self.layout, context)
        return

    use_legacy_sculpt = 'sculpt_plus' not in context.workspace

    prefs = context.preferences
    ui_scale = prefs.system.ui_scale # prefs.view.ui_scale

    sculpt_plus_prefs = get_prefs(context)

    # toolbar_is_wide_open
    if context.region.width <= (96 * ui_scale) or use_legacy_sculpt:
        self.layout.operator('sculpt_plus.expand_toolbar', text="", icon='RIGHTARROW', emboss=False)
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

    if sculpt_plus_prefs.toolbar_position == 'LEFT':
        factor = 1.0 - (context.region.width - (96*ui_scale)/2) / context.region.width
        row = layout.split(align=False, factor=factor)
        col_1 = row.column(align=False)
        if tool_active:
            col_2 = row.column(align=False)
    else:
        factor = (context.region.width - (96*ui_scale)/2) / context.region.width
        row = layout.split(align=False, factor=factor)
        if tool_active:
            col_2 = row.column(align=False)
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
    #cy_toolbar = CyBlStruct.UI_LAYOUT(toolbar)
    #print(cy_toolbar.x, cy_toolbar.y, cy_toolbar.w, cy_toolbar.h)

    if tool_active is None:
        return

    ui_props = Props.UI(context)

    color_scale = 0.19
    color_bot_scale = 0.2

    # brush settings sections.
    panel_tool = col_2.column(align=True)
    col = panel_tool.row(align=True)
    col.scale_y = color_scale
    col.prop(ui_props, 'color_toolbar_panel_tool', text="")
    if tool_active_type == 'builtin_brush':
        draw_brush_settings_tabs(panel_tool, context)
    else:
        draw_tool_settings(panel_tool, context, tool_active, tool_active_id)
    col = panel_tool.row(align=True)
    col.scale_y = color_bot_scale
    col.enabled = False
    col.prop(ui_props, 'color_toolbar_panel_emboss_bottom', text="")

    col_2.separator()

    panel_maskfacesets = col_2.column(align=True)
    col = panel_maskfacesets.row(align=True)
    col.scale_y = color_scale
    col.prop(ui_props, 'color_toolbar_panel_maskfacesets', text="")
    draw_mask_facesets(panel_maskfacesets, context)
    col = panel_maskfacesets.row(align=True)
    col.scale_y = color_bot_scale
    col.enabled = False
    col.prop(ui_props, 'color_toolbar_panel_emboss_bottom', text="")

    col_2.separator()

    panel_sculptmesh = col_2.column(align=True)
    col = panel_sculptmesh.row(align=True)
    col.scale_y = color_scale
    col.prop(ui_props, 'color_toolbar_panel_sculptmesh', text="")
    draw_sculpt_sections(panel_sculptmesh, context)
    col = panel_sculptmesh.row(align=True)
    col.scale_y = color_bot_scale
    col.enabled = False
    col.prop(ui_props, 'color_toolbar_panel_emboss_bottom', text="")



def register():
    VIEW3D_PT_tools_active.draw = draw_toolbar

def unregister():
    pass
