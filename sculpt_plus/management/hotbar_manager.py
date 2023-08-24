from typing import List
from pathlib import Path
import pickle

from sculpt_plus.path import SculptPlusPaths
from .hotbar_layer import HotbarLayer_Collection
from sculpt_plus.utils.decorators import singleton

from brush_manager.api import bm_types


_hm_data = None

@singleton
class HotbarManager:
    # Singleton.
    # ------------------------------------------
    @classmethod
    def get(cls):
        global _hm_data
        if _hm_data is not None:
            return _hm_data
        print(f"[Sculpt+] Instance? HM_DATA@[{id(_hm_data) if _hm_data is not None else None}]")
        # Try to load data from file.
        data_filepath: Path = SculptPlusPaths.HOTBAR_DATA(as_path=True)

        from ..management.hotbar_manager import HotbarManager

        if not data_filepath.exists() or data_filepath.stat().st_size == 0:
            print(f"[Sculpt+] HotbarManager not found in path: '{str(data_filepath)}'")
            _hm_data = HotbarManager()
        else:
            with data_filepath.open('rb') as data_file:
                data: HotbarManager = pickle.load(data_file)
                data.ensure_owners()
                _hm_data = data
            print(f"[Sculpt+] Loaded HM_DATA@[{id(data)}] from file: '{str(data_filepath)}'")
        return _hm_data


    def save(self) -> None:
        data_filepath: Path = SculptPlusPaths.HOTBAR_DATA(as_path=True)

        print(f"[Sculpt+] Saving HM_DATA@[{id(self)}] to file: '{str(data_filepath)}'")

        # Avoid multiple references to objects since pickle doesn't work really well with that.
        self.clear_owners()

        with data_filepath.open('wb') as data_file:
            pickle.dump(self, data_file)

        # Restore references...
        self.ensure_owners()


    def clear_owners(self) -> None:
        self.layers.clear_owners()

    def ensure_owners(self) -> None:
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
        if act_layer := self.layers.active:
            return act_layer.brushes_ids
        return []


    # Constructor and free.
    # ------------------------------------------
    def __init__(self):
        print(f"[Sculpt+] New HM_DATA@[{id(self)}]")

        self.active_cat_id = ''
        self.layers = HotbarLayer_Collection(self)

        self.use_alt: bool = False

        self.layers.add('Default', custom_uuid='DEFAULT')


    def __del__(self):
        print(f"[Sculpt+] Remove HM_DATA@[{id(self)}]")

        del self.layers
        global _hm_data
        _hm_data = None

    # Util methods.
    # ------------------------------------------
    def toggle_alt(self) -> None:
        self.use_alt = not self.use_alt
