from bl_ui.space_view3d import VIEW3D_HT_tool_header
from bpy.types import Brush as BlBrush

from ...backup_cache import get_attr_from_cache, VIEW3D_PT_tools_active, UnifiedPaintPanel


def draw_toolheader(self: VIEW3D_HT_tool_header, context):
    # Override in Sculpt Mode.
    if context.mode != 'SCULPT':
        # Used cached method.
        get_attr_from_cache(VIEW3D_HT_tool_header, 'draw_tool_settings')(self, context)
        return

    space_type = context.space_data.type
    tool_active = VIEW3D_PT_tools_active._tool_active_from_context(context, space_type)
    if not tool_active:
        return None
    tool_active_id: str = getattr(tool_active, "idname", None,)
    tool_active_type, tool_active_id = tool_active_id.split('.')
    is_brush: bool = tool_active_type == 'builtin_brush'

    item, tool, icon_value = VIEW3D_PT_tools_active._tool_get_active(context, space_type, 'SCULPT', with_icon=True)
    if item is None:
        return None

    layout = self.layout
    layout.label(text="    " + item.label, icon_value=icon_value)

    if is_brush:
        brush: BlBrush = context.tool_settings.sculpt.brush
        '''
        UnifiedPaintPanel.prop_unified(layout, context, brush, 'size', 'size', 'use_pressure_size', text="Radius", slider=True, header=True)
        UnifiedPaintPanel.prop_unified(layout, context, brush, 'strength', 'strength', 'use_pressure_strength', text="Strength", slider=True, header=True)
        if not brush.sculpt_capabilities.has_direction:
            layout.prop(brush, 'direction', expand=True, text="")
        '''
        tool_settings = context.tool_settings
        capabilities = brush.sculpt_capabilities

        ups = tool_settings.unified_paint_settings

        if capabilities.has_color:
            row = layout.row(align=True)
            row.ui_units_x = 4
            UnifiedPaintPanel.prop_unified_color(row, context, brush, "color", text="")
            UnifiedPaintPanel.prop_unified_color(row, context, brush, "secondary_color", text="")
            row.separator()
            layout.prop(brush, "blend", text="", expand=False)

        size = "size"
        size_owner = ups if ups.use_unified_size else brush
        if size_owner.use_locked_size == 'SCENE':
            size = "unprojected_radius"

        UnifiedPaintPanel.prop_unified(
            layout,
            context,
            brush,
            size,
            pressure_name="use_pressure_size",
            unified_name="use_unified_size",
            text="Radius",
            slider=True,
            header=True,
        )

        # strength, use_strength_pressure
        pressure_name = "use_pressure_strength" if capabilities.has_strength_pressure else None
        UnifiedPaintPanel.prop_unified(
            layout,
            context,
            brush,
            "strength",
            pressure_name=pressure_name,
            unified_name="use_unified_strength",
            text="Strength",
            header=True,
        )

        # direction
        if not capabilities.has_direction:
            layout.row().prop(brush, "direction", expand=True, text="")

    else:
        get_attr_from_cache(VIEW3D_HT_tool_header, 'draw_tool_settings')(self, context)


def register():
    # Here we override cls methods and properties as we need.
    VIEW3D_HT_tool_header.draw_tool_settings = draw_toolheader

def unregister():
    pass
