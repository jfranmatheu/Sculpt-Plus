from bl_ui.space_view3d import VIEW3D_HT_tool_header
from bpy.types import (
    VIEW3D_PT_tools_brush_select,
    VIEW3D_PT_tools_active,
    VIEW3D_PT_tools_brush_settings
)
from collections import defaultdict

_cache_reset = {}
_mod_cls_attributes = defaultdict(set)


def get_attr_from_cache(cls, attr, default=None):
    global _cache_reset

    if cls_cache := _cache_reset.get(cls, None):
        if value := cls_cache.get(attr, default):
            return value
        else:
            print(f"No cache attr '{attr}' for cls '{cls}'")
    else:
        print(f"No cache for cls:", cls)
    if default is not None:
        return default
    if value := getattr(cls, attr, default):
        return value
    return None

def cache_cls_attributes(cls) -> dict:
    global _cache_reset
    _cache_reset[cls] = cls.__dict__.copy()
    return _cache_reset[cls]


def set_cls_attribute(cls, attr: str, new_value):
    ## print("CLS ATTR:", cls, attr, getattr(cls, attr))
    global _mod_cls_attributes
    global _cache_reset

    if cache := _cache_reset.get(cls, None):
        pass
    else:
        cache = {}

    if attr not in cache:
        cache[attr] = cls.__dict__.copy().get(attr, None)
        _cache_reset[cls] = cache

    setattr(cls, attr, new_value)

    _mod_cls_attributes[cls].add(attr)

    setattr(cls, 'old_' + attr, cache[attr])


def unregister_pre():
    global _mod_cls_attributes

    for cls, mod_cls_attributes in _mod_cls_attributes.items():
        cache = _cache_reset[cls] # raises AttributeError on class without decorator
        for mod_attr in mod_cls_attributes:
            if not hasattr(cls, mod_attr) or mod_attr not in cache:
                # WTF! This should not happen...
                continue
            setattr(cls, mod_attr, cache[mod_attr])
            old_attr = 'old_' + mod_attr
            if not hasattr(cls, old_attr) or old_attr not in cache:
                continue
            delattr(cls, old_attr)
