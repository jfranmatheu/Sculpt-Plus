from typing import List
from pathlib import Path
import pickle

from sculpt_plus.path import SculptPlusPaths
from .hotbar_layer import HotbarLayer_Collection
from sculpt_plus.utils.decorators import singleton

from brush_manager.api import bm_types



@singleton
class HotbarManager:
    # Singleton.
    # ------------------------------------------
    @classmethod
    def get(cls):
        hm = cls.get_instance()
        if hm is not None:
            return hm
        print(f"[Sculpt+] Instance? HM_DATA@[{id(hm) if hm is not None else None}]")
        # Try to load data from file.
        data_filepath: Path = SculptPlusPaths.HOTBAR_DATA(as_path=True)

        from ..management.hotbar_manager import HotbarManager

        if not data_filepath.exists() or data_filepath.stat().st_size == 0:
            print(f"[Sculpt+] HotbarManager not found in path: '{str(data_filepath)}'")
            hm = HotbarManager()
        else:
            with data_filepath.open('rb') as data_file:
                hm: HotbarManager = pickle.load(data_file)
                hm.ensure_owners()
            print(f"[Sculpt+] Loaded HM_DATA@[{id(hm)}] from file: '{str(data_filepath)}'")

        cls.set_instance(hm)
        print(f"[Sculpt+] Created/Loaded? HM_DATA@[{id(hm) if hm is not None else None}]")
        hm = cls.get_instance()
        print(f"[Sculpt+] StoredInstance? HM_DATA@[{id(hm) if hm is not None else None}]")
        return hm


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
    
    
    def select_brush(self, context, brush_index: int) -> None:
        if layer := self.layers.active:
            if brush_item := layer.active_set.brushes[brush_index]:
                brush_item.set_active(context)


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
