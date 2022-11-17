import bpy
from bpy.types import Brush


def remove_brush_from_category(brush: Brush) -> None:
    cat_id: str = brush['cat_id']
    brush_id: str = brush['id']
    bpy['sculpt_plus']['cats'][cat_id]['brushes'].remove(brush_id)
    del bpy['sculpt_plus']['brushes'][brush_id]
    del brush['cat_id']

def add_brush_to_category(brush: Brush, cat_id: str) -> None:
    if 'cat_id' in brush:
        remove_brush_from_category(brush)
    brush_id: str = brush['id']
    bpy['sculpt_plus']['cats'][cat_id]['brushes'].add(brush_id)
    bpy['sculpt_plus']['brushes'][brush_id] = cat_id
    brush['id'] = cat_id
