import bpy
from bpy.types import Brush, Property, BrushCapabilitiesSculpt, BrushCapabilities, BrushCurvesSculptSettings, BrushTextureSlot, Image, Texture
from bpy.app import timers
from bpy.types import PointerProperty, CollectionProperty
from bpy.app.handlers import load_post, persistent

import functools
from time import time
from typing import Union, Dict, Tuple, List, Set

from .exporter import export_brush


# brush_props_to_listen: List[str] = lambda : Brush.bl_rna.properties.values()
# brush_tex_slot_props_to_listen: List[str] = 
sculpt_brush_types: Tuple[Tuple[type, str]] = (
    (Brush, ''),
    (BrushCapabilitiesSculpt, 'brush_capabilities'),
    (BrushCapabilities, 'brush_capabilities'),
    (BrushCurvesSculptSettings, 'curves_sculpt_settings'),
    (BrushTextureSlot, 'texture_slot')
)
exclude_prop_types = (PointerProperty, CollectionProperty)

props_being_updated: Dict[str, float] = {}
# props_being_updated: set[str] = {}

def update_brush_after_time(brush: Brush, attr: str) -> Union[float, None]:
    if brush is None:
        return None
    if time() - props_being_updated[attr] < 2.0:
        # To avoid spamming updates when user
        # changes properties really quickly as from sliders.
        # Brushes will be exported in idle state.
        return .5
    print(f"Brush {brush.name} attribute {attr} is updated")
    export_brush(brush)
    del props_being_updated[attr]
    return None

def on_update_brush_prop(brush: Brush, attr: str, data_path: str) -> None:
    if bpy.context.mode != 'SCULPT':
        return
    if 'cat_id' not in brush:
        # Brush not in catalogue/category.
        return
    # Reset time.
    props_being_updated[attr] = time()
    if attr in props_being_updated:
        return
    brush['is_dirty'] = True
    timers.register(functools.partial(update_brush_after_time, brush, attr), first_interval=1.0)


subscribers = []

def new_owner():
    owner = object()
    subscribers.append(owner)
    return owner

def subscribe_rna(_type, key: str = '', data_path: str = None):
    bpy.msgbus.subscribe_rna(
        key=(_type, key),
        owner=new_owner(),
        args=(bpy.context.tool_settings.sculpt, key),
        notify=lambda _sculpt, _key: on_update_brush_prop(_sculpt.brush, _key, data_path),
        options={'PERSISTENT'})


@persistent
def on_load_post(dummy):
    for (_type, _datapath) in sculpt_brush_types:
        for key, prop_type in _type.bl_rna.properties.items():
            if isinstance(prop_type, exclude_prop_types) and not isinstance(prop_type.fixed_type, (Texture, Image)):
                # print(prop_type, prop_type.fixed_type, prop_type.__class__)
                continue
            subscribe_rna(_type, key, _datapath)


def register():
    load_post.append(on_load_post)

def unregister():
    if on_load_post in load_post:
        load_post.remove(on_load_post)

    if subscribers:
        for owner in subscribers:
            bpy.msgbus.clear_by_owner(owner)
        subscribers.clear()
