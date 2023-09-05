from brush_manager.api import bm_types, GLOBALS as BM_GLOBALS
from sculpt_plus.management.hotbar_manager import HotbarManager



class _Globals:
    bm_data: bm_types.AddonDataByMode
    hm_data: HotbarManager

    @property
    def bm_data(self):
        return BM_GLOBALS.BM_DATA.SCULPT

    @property
    def hm_data(self):
        return HotbarManager.get()

G = _Globals()
