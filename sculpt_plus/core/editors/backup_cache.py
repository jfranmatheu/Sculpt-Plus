from bl_ui.space_view3d import VIEW3D_HT_tool_header
from bl_ui.properties_paint_common import UnifiedPaintPanel, BrushSelectPanel, BrushPanel
from bpy.types import (
    VIEW3D_PT_tools_brush_select,
    VIEW3D_PT_tools_active,
    VIEW3D_PT_tools_brush_settings, VIEW3D_PT_tools_brush_settings_advanced,
    VIEW3D_PT_tools_brush_falloff, VIEW3D_PT_tools_brush_stroke,
    VIEW3D_PT_tools_brush_texture,
)
from collections import defaultdict


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
_mod_cls_attributes = defaultdict(set)


def get_attr_from_cache(cls, attr, default=None):
    if cls_cache := _cache_reset.get(cls.__name__, None):
        if hasattr(cls_cache, attr):
            return cls_cache.get(attr, default)
    return default

def cache_cls_attributes(cls):
    _cache_reset[cls.__name__] = cls.__dict__.copy()
    

def set_cls_attribute(cls, attr, new_value):
    if cls.__name__ not in _cache_reset:
        cache_cls_attributes(cls)
    _mod_cls_attributes[cls.__name__].add(attr)
    setattr(cls, 'old_' + attr, get_attr_from_cache(cls, attr))
    setattr(cls, attr, new_value)


def pre_register():
    for cls in classes_to_reset:
        cache_cls_attributes(cls)

def pre_unregister():
    for cls in classes_to_reset:
        if mod_cls_attributes := _mod_cls_attributes.get(cls.__name__, None):
            cache = _cache_reset[cls.__name__] # raises AttributeError on class without decorator
            for mod_attr in mod_cls_attributes:
                setattr(cls, mod_attr, cache[mod_attr])
                delattr(cls, 'old_' + mod_attr)
