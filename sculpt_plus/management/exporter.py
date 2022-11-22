from uuid import uuid4

import bpy

from sculpt_plus.path import SculptPlusPaths


def export_brush(brush) -> None:
    if 'cat_id' not in brush:
        return
    cat_id: str = brush['cat_id']
    if 'id' not in brush:
        brush['id'] = uuid4().hex
    brush_id: str = brush['id'] 
    blendlib_path = SculptPlusPaths.DATA_CATS(cat_id, brush_id + '.blend')
    bpy.data.libraries.write(blendlib_path, {brush})
