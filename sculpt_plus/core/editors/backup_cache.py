from bl_ui.space_view3d import VIEW3D_HT_tool_header
from bpy.types import (
    VIEW3D_PT_tools_brush_select,
    VIEW3D_PT_tools_active,
    VIEW3D_PT_tools_brush_settings
)
from collections import defaultdict


classes_to_cache = (
    VIEW3D_PT_tools_active,
    VIEW3D_HT_tool_header,
    VIEW3D_PT_tools_brush_select,
    VIEW3D_PT_tools_brush_settings
)

_cache_reset = {}
_mod_cls_attributes = defaultdict(set)


def get_attr_from_cache(cls, attr, default=None):
    if cls_cache := _cache_reset.get(cls, None):
        if hasattr(cls_cache, attr):
            return cls_cache.get(attr, default)
    return default

def cache_cls_attributes(cls):
    _cache_reset[cls] = cls.__dict__.copy()
    

def set_cls_attribute(cls, attr, new_value):
    if cls not in _cache_reset:
        cache_cls_attributes(cls)
    _mod_cls_attributes[cls].add(attr)
    setattr(cls, 'old_' + attr, get_attr_from_cache(cls, attr))
    setattr(cls, attr, new_value)


def pre_register():
    for cls in classes_to_cache:
        cache_cls_attributes(cls)

def pre_unregister():
    for cls, mod_cls_attributes in _mod_cls_attributes.items():
        cache = _cache_reset[cls] # raises AttributeError on class without decorator
        for mod_attr in mod_cls_attributes:
            if not hasattr(cls, mod_attr) or mod_attr not in cache:
                # WTF! This should not happen...
                continue
            setattr(cls, mod_attr, cache[mod_attr])
            delattr(cls, 'old_' + mod_attr)
