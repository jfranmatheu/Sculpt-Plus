from contextlib import contextmanager
import json

from sculpt_plus.path import SculptPlusPaths, brush_sets_dir
from .data import SCULPTPLUS_PG_slot_set


''' I/O Utils for brush-set managements. '''
def get_set_config_path(brush_set_uid: str) -> str:
    return (brush_sets_dir / brush_set_uid / "info.json").name


''' I/O FILE Helpers for brush-set management. '''
def write_slotset_config(slot_set: SCULPTPLUS_PG_slot_set) -> None:
    config_path: str = get_set_config_path(slot_set.uid)
    config_data: dict = slot_set.serialize()
    with open(config_path, 'w+', encoding='utf-8') as config_file:
        json.dump(config_data, config_file)

def save_slotset(slot_set: SCULPTPLUS_PG_slot_set) -> None:
    
