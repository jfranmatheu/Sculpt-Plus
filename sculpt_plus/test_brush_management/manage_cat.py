import bpy
from uuid import uuid4
from os import remove
from sculpt_plus.path import brush_sets_dir


def new_cat(cat_name: str) -> None:
    cat_id: str = uuid4().hex
    bpy['sculpt_plus']['cats'][cat_id] = {
        'name': cat_name,
        'version': 1,
        'brushes': set()
    }

def rename_cat(cat_id: str, new_name: str) -> None:
    bpy['sculpt_plus']['cats'][cat_id]['name'] = new_name

def remove_cat(cat_id: str) -> None:
    del bpy['sculpt_plus']['cats'][cat_id]
    for _br_id, _cat_id in bpy['sculpt_plus']['brushes'].items():
        if _cat_id == cat_id:
            del bpy['sculpt_plus']['brushes'][_br_id]
    cat_path = brush_sets_dir / cat_id
    remove(str(cat_path))
