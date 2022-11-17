from sculpt_plus.path import SculptPlusPaths, brush_sets_dir
import json
import bpy
from typing import Dict, Union, List


def load_categories_and_brushes():
    cats_dict: Dict[str, Dict[str, Union[str, List[str]]]] = {}
    cat_brush_relationship: Dict[str, str] = {}

    ''' Load categories ID and data. '''
    cats_json_path = brush_sets_dir / 'cats.json'
    with cats_json_path.open('r', encoding='utf-8') as cats_json:
        loaded_cats: dict = json.load(cats_json)
        if not loaded_cats:
            return

    ''' Process every category. '''
    for cat_id, cat_data in loaded_cats.items():
        cats_dict[cat_id] = {
            'name': cat_data['name'],
            'version': cat_data['version'],
            'brushes': set(cat_data['brushes'])
        }

        ''' Relationship between cats IDs and brushes IDs. '''
        for brush_id in cat_data['brushes']:
            cat_brush_relationship[brush_id] = cat_id

        ''' Get brushes blend file path and load-link brushes.'''
        cat_brushes_blend_path = brush_sets_dir / cat_id / 'brushes.blend'
        with bpy.data.libraries.load(str(cat_brushes_blend_path), link=True) as (data_from, data_to):
            data_to.brushes = data_from.brushes

        ''' Operate directly on brushes datablocks.'''
        # for brush in data_to.brushes:
        #     if brush is None:
        #         continue
        #     # Do anything with brush data.
    
    ''' Write cats and brush loaded data to bpy global access prop. '''
    bpy['sculpt_plus'] = {
        'cats': cats_dict,
        'brushes': cat_brush_relationship
    }
