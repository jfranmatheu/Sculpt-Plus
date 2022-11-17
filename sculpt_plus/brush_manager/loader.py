from sculpt_plus.path import SculptPlusPaths, brush_sets_dir
import json
import bpy
from typing import Dict, Union, List, Set
from pathlib import Path
from sculpt_plus.props import Props


def load_categories_and_brushes():
    context = bpy.context
    brush_manager = Props.BrushManager(context)

    cats_dict: Dict[str, Dict[str, Union[str, List[str]]]] = {}
    cat_brush_relationship: Dict[str, str] = {}

    cats_ids: List[str] = []
    brushes_ids: Set[str] = set()

    ''' Load categories ID and data. '''
    cats_json_path = brush_sets_dir / 'cats.json'
    with cats_json_path.open('r', encoding='utf-8') as cats_json:
        loaded_cats: dict = json.load(cats_json)
        if not loaded_cats:
            return

    ''' Process every category. '''
    for cat_id, cat_data in loaded_cats.items():
        cat_brushes = cat_data['brushes']
        cats_dict[cat_id] = {
            'name': cat_data['name'],
            'version': cat_data['version'],
            'brushes': cat_brushes
        }

        brushes_ids.update(set(cat_brushes))
        cats_ids.append(cat_id)

        ''' Relationship between cats IDs and brushes IDs. '''
        for brush_id in cat_data['brushes']:
            cat_brush_relationship[brush_id] = cat_id

    ''' Remove brushes if their IDs match.'''
    for brush in list(bpy.data.brushes):
        if not brush.use_paint_sculpt:
            continue
        if 'sculpt_plus_id' not in brush:
            continue
        if brush['sculpt_plus_id'] in brushes_ids:
            bpy.data.brushes.remove(brush)

    ''' Get brushes blend file path and load-link brushes.'''
    for cat_id in cats_ids:
        ''' Link brushes. '''
        cat_brushes_blend_path = brush_sets_dir / cat_id / 'brushes.blend'
        with bpy.data.libraries.load(str(cat_brushes_blend_path), link=True) as (data_from, data_to):
            data_to.brushes = data_from.brushes

        ''' Create category. '''
        cat_data = cats_dict[cat_id]
        cat = brush_manager.new_cat(cat_data['name'])
        cat.version = cat_data['version']

        ''' Operate directly on brushes datablocks to add brushes in an ordered way.'''
        for brush in sorted(data_to.brushes, key=lambda brush: cat_data['brushes'].index(brush['sculpt_plus_id'])):
            if brush is None:
                continue
            # Do anything with brush data.
            cat.add_brush(brush)

    ''' Write cats and brush loaded data to bpy global access prop. '''
    bpy['sculpt_plus'] = {
        'cats': cats_dict,
        'brushes': cat_brush_relationship
    }
