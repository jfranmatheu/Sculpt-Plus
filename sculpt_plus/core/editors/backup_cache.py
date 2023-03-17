from bl_ui.space_view3d import VIEW3D_HT_tool_header
from bl_ui.properties_paint_common import UnifiedPaintPanel, BrushSelectPanel, BrushPanel
from bpy.types import (
    VIEW3D_PT_tools_brush_select,
    VIEW3D_PT_tools_active,
    VIEW3D_PT_tools_brush_settings, VIEW3D_PT_tools_brush_settings_advanced,
    VIEW3D_PT_tools_brush_falloff, VIEW3D_PT_tools_brush_stroke,
    VIEW3D_PT_tools_brush_texture,
)


classes_to_reset = (
    VIEW3D_PT_tools_active,
    VIEW3D_HT_tool_header,
    #BrushPanel,
    #BrushSelectPanel,
    VIEW3D_PT_tools_brush_select,
    #VIEW3D_PT_tools_active,
    VIEW3D_PT_tools_brush_settings, #VIEW3D_PT_tools_brush_settings_advanced,
    #VIEW3D_PT_tools_brush_falloff, VIEW3D_PT_tools_brush_stroke,
    #VIEW3D_PT_tools_brush_texture
)

_cache_reset = {}


def get_attr_from_cache(cls, attr, default=None):
    return _cache_reset[cls.__name__].get(attr, default)


def register():
    for cls in classes_to_reset:
        _cache_reset[cls.__name__] = cls.__dict__.copy()

def unregister():
    for cls in classes_to_reset:
        cache = _cache_reset[cls.__name__] # raises AttributeError on class without decorator
        #for key in [key for key in cls.__dict__ if key not in cache]:
        #    delattr(cls, key)
        for key, value in cache.items():  # reset the items to original values
            try:
                setattr(cls, key, value)
            except AttributeError:
                pass
