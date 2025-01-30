from bl_ui.space_toolsystem_toolbar import VIEW3D_PT_tools_active
from bl_ui.space_toolsystem_common import ToolSelectPanelHelper

from sculpt_plus.props import Props, toolbar_hidden_brush_tools, SculptTool
from sculpt_plus.prefs import get_prefs

# from sculpt_plus.core.data.cy_structs import CyBlStruct

from ..toolbar_panels import *
from .backup_cache import set_cls_attribute



def draw_toolbar(self, context):
    if context.mode != 'SCULPT' or 'sculpt_plus' not in context.workspace:
        VIEW3D_PT_tools_active.draw_cls(self.layout, context)
        return

    prefs = context.preferences
    ui_scale = prefs.system.ui_scale # prefs.view.ui_scale

    sculpt_plus_prefs = get_prefs(context)
    if sculpt_plus_prefs is None:
        # Probablt user disabled the addon... and it wasn't returned so well to its original state.
        VIEW3D_PT_tools_active.draw_cls(self.layout, context)
        return

    # toolbar_is_wide_open
    if context.region.width <= (96 * ui_scale):
        # self.layout.operator('sculpt_plus.expand_toolbar', text="", icon='RIGHTARROW', emboss=False)
        # draw_cls(VIEW3D_PT_tools_active, self.layout, context, spacing=0.1)
        VIEW3D_PT_tools_active.draw_cls(self.layout, context)
        return

    layout = self.layout

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
    view_scroll_y = abs(reg.view2d.region_to_view(0, reg.height)[1])

    # ui_scale = prefs.system.ui_scale # prefs.view.ui_scale
    line_height_px = 20 * ui_scale # widget_unit is 20 in 72 DPI by default.
    offset_factor_y = view_scroll_y / line_height_px
    sep = col_1.column(align=True)
    sep.label(text='', icon='BLANK1')
    sep.scale_y = offset_factor_y * 1.0333

    # print(context.area.height, reg.height, view_scroll_y, offset_factor_y)

    # TOOLBAR.
    toolbar = col_1.column(align=False)
    # draw_cls(VIEW3D_PT_tools_active, toolbar, context, spacing=1.0) # row, context, detect_layout=False, default_layout='ROW', scale_y=1.35
    VIEW3D_PT_tools_active.draw_cls(toolbar, context)
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
    set_cls_attribute(VIEW3D_PT_tools_active, 'draw', draw_toolbar)
