from contextlib import contextmanager
import json
from os import path
from os import mkdir, remove, rename, listdir
from typing import List, Set
from uuid import uuid4

import bpy
from bpy.types import Brush

from sculpt_plus.prefs import get_prefs
from sculpt_plus.path import SculptPlusPaths, brush_sets_dir
from sculpt_plus.props import Props
from sculpt_plus.brush_manager.data_brush_category import SCULPTPLUS_PG_brush_category


def get_cat_path(brush_set_uid: str):
    return brush_sets_dir / brush_set_uid


''' I/O Utils for brush-set managements. '''
def get_cat_config_path(brush_set_uid: str) -> str:
    return (brush_sets_dir / brush_set_uid / "info.json").name


''' I/O FILE Helpers for brush-set management. '''
def write_cat_config(brush_cat: SCULPTPLUS_PG_brush_category) -> None:
    config_path: str = get_cat_config_path(brush_cat.uid)
    config_data: dict = brush_cat.serialize()
    with open(config_path, 'w+', encoding='utf-8') as config_file:
        json.dump(config_data, config_file)

def read_cat_config(cat_idname: str) -> dict:
    config_path: str = get_cat_config_path(cat_idname)
    if not path.exists(config_path):
        return None

    with open(config_path, 'r', encoding='utf-8') as config_file:
        config_data: dict = json.load(config_file)
        return config_data

''' Export brush category data. '''
def export_brush_category(brush_cat: SCULPTPLUS_PG_brush_category, context) -> None:
    brush_lib_path: str = get_prefs(context).brush_lib_path
    num_backups: int = get_prefs(context).num_backup_versions
    cat_idname: str = brush_cat.uid
    cat_version: str = str(brush_cat.version)
    brush_category_path: str = path.join(brush_lib_path, cat_idname)
    brushes_blendfile: str = path.join(brush_category_path, 'brushes.blend')

    # Create folder if doesn't exist.
    if not path.exists(brush_category_path):
        mkdir(brush_category_path)

    # Create backup (rename file).
    if num_backups > 0:
        # Detect how many backup files are stored.
        backup_filecount: int = 1 # Counts current (future) backup file.
        older_backup_file: str = ''
        for file_name in listdir(brush_category_path):
            name, extension = file_name.split('.')
            if name == 'backup' and extension.startswith('blend'):
                if not older_backup_file:
                    older_backup_file = file_name
                backup_blendfile += 1

        # If backup count is greater than user-specified, remove the older backup.
        if older_backup_file and backup_filecount > num_backups:
            backup_to_remove: str = path.join(brush_category_path, older_backup_file)
            remove(backup_to_remove)

        # Rename original brushes.blend to backup.blendX
        backup_blendfile: str = path.join(brush_category_path, 'backup.blend%i' % backup_filecount)
        rename(brushes_blendfile, backup_blendfile)

    # Save new brushes library file.
    brush_list: List[Brush] = brush_cat.brushes
    for brush in brush_list:
        if 'sculpt_plus_id' not in brush:
            brush['sculpt_plus_id'] = uuid4().hex
    brushes: Set[Brush] = set(brush_cat.brushes)
    bpy.data.libraries.write(brushes_blendfile, brushes, fake_user=False)

    # Save update
    brush_cat.version += 1
    brush_cat.update_date()
    write_cat_config(brush_cat)


''' Import brush category data. '''
def import_brush_category(cat_idname: str, context) -> None:
    cat_config = read_cat_config(cat_idname)

    brush_lib_path: str = get_prefs(context).brush_lib_path
    brush_category_path: str = path.join(brush_lib_path, cat_idname)
    brushes_blendfile: str = path.join(brush_category_path, 'brushes.blend')

    # bpy.data.libraries.load(brushes_blendfile)

    # the loaded objects can be accessed from 'data_to' outside of the context
    # since loading the data replaces the strings for the datablocks or None
    # if the datablock could not be loaded.
    data_brushes = bpy.data.brushes

    existing_brushes = []
    with bpy.data.libraries.load(brushes_blendfile) as (data_from, data_to):
        # data_to.brushes = data_from.brushes
        brushes_to_load = []
        for name in data_from.brushes:
            if data_brushes.get(name, None):
                existing_brushes.append(name)
            else:
                brushes_to_load.append(name)

        data_to.brushes = brushes_to_load

    # now operate directly on the loaded data
    brushes = [data_brushes.get(name) for name in existing_brushes] + [brush for brush in data_to.brushes if brush is not None]
    brushes_dict = {
        brush['sculpt_plus_id']: brush for brush in brushes
    }

    # sort brushes based in the cat config order.
    sorted_brushes = [
        brushes_dict[slot_id] for slot_id in cat_config['brushes']
    ]

    brush_manager = Props.BrushManager(context)
    cat = brush_manager.new_set(cat_config['name'])
    cat.version = cat_config['version']
    for brush in sorted_brushes:
        cat.add_brush(brush) 


def import_all_brush_categories(context) -> None:
    brush_lib_path: str = get_prefs(context).brush_lib_path
    categories_ids: List[str] = []
    for file_name in listdir(brush_lib_path):
        dir_path = path.join(brush_lib_path, file_name)
        if not path.isdir(dir_path):
            continue
        categories_ids.append(file_name)
    
    if not categories_ids:
        return
    
    for cat_id in categories_ids:
        import_brush_category(cat_id, context)
