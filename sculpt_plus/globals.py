from brush_manager.api import BM_DATA, bm_types
from .management.hotbar_manager import HotbarManager



class _Globals:
    bm_data: bm_types.AddonDataByMode
    hm_data: HotbarManager

    @property
    def bm_data(self):
        return BM_DATA.SCULPT

    @property
    def hm_data(self):
        return HotbarManager.get()

G = _Globals()
