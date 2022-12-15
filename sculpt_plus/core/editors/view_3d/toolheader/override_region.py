from bl_ui.space_view3d import VIEW3D_HT_tool_header

from ...backup_cache import get_attr_from_cache


def draw_toolheader(self: VIEW3D_HT_tool_header, context):
    # Override in Sculpt Mode.
    if context.mode != 'SCULPT':
        # Used cached method.
        get_attr_from_cache(VIEW3D_HT_tool_header, 'draw_tool_settings')(self, context)
        return

def register():
    # Here we override cls methods and properties as we need.
    VIEW3D_HT_tool_header.draw_tool_settings = draw_toolheader

def unregister():
    pass
