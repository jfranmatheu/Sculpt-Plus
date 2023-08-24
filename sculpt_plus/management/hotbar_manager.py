from typing import List
from pathlib import Path
import pickle

from sculpt_plus.path import SculptPlusPaths
from .hotbar_layer import HotbarLayer_Collection

from brush_manager.api import bm_types


class HotbarManager:
    # Singleton.
    # ------------------------------------------
    _instance = None

    @classmethod
    def get(cls) -> 'HotbarManager':
        if cls._instance is not None:
            return cls._instance
        # Try to load data from file.
        data_filepath: Path = SculptPlusPaths.HOTBAR_DATA(as_path=True)

        if not data_filepath.exists():
            print(f"[Sculpt+] HM_DATA not found in path: '{str(data_filepath)}'")
            cls._instance = HotbarManager()
        else:
            with data_filepath.open('rb') as data_file:
                data: HotbarManager = pickle.load(data_file)
                data.ensure_owners()
                cls._instance = data
            print(f"[Sculpt+] Loaded HM_DATA@[{id(data)}] from file: '{str(data_filepath)}'")
        return cls._instance


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
        HotbarManager._instance = None

    # Util methods.
    # ------------------------------------------
    def toggle_alt(self) -> None:
        self.use_alt = not self.use_alt
