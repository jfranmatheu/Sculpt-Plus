from typing import List
from pathlib import Path
import pickle

from sculpt_plus.path import SculptPlusPaths
from .hotbar_layer import HotbarLayer_Collection

from brush_manager.api import bm_types, BM_DATA

bm_data = BM_DATA.SCULPT


class HotbarManager:
    # Singleton.
    # ------------------------------------------
    _instance = None

    @classmethod
    def get(cls) -> 'HotbarManager':
        # Try to load data from file.
        data_filepath: Path = SculptPlusPaths.HOTBAR_DATA(as_path=True)

        if not data_filepath.exists():
            cls._instance = HotbarManager()
        else:
            with data_filepath.open('rb') as data_file:
                data: HotbarManager = pickle.load(data_file)
                cls._instance = data

        return cls._instance


    def save(self) -> None:
        data_filepath: Path = SculptPlusPaths.HOTBAR_DATA(as_path=True)

        # Avoid multiple references to objects since pickle doesn't work really well with that.
        self.layers.clear_owners()

        with data_filepath.open('wb') as data_file:
            pickle.dump(self, data_file)

        # Restore references...
        self.layers.ensure_owners(self)


    # Properties
    # ------------------------------------------
    layers: HotbarLayer_Collection


    use_alt: bool


    @property
    def brushes(self) -> List[bm_types.BrushItem]:
        if act_layer := self.layers.active:
            return act_layer.brushes
        return []

    @property
    def brushes_ids(self) -> List[str]:
        return [b.uuid if b else '' for b in self.brushes]


    # Constructor and free.
    # ------------------------------------------
    def __init__(self):
        self.active_cat_id = ''
        self.layers = HotbarLayer_Collection(self)

        self.use_alt: bool = False

        self.layers.add('Default')

    def __del__(self):
        del self.layers
        HotbarManager._instance = None

    # Util methods.
    # ------------------------------------------
    def toggle_alt(self) -> None:
        self.use_alt = not self.use_alt
