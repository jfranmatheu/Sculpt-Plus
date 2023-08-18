from brush_manager.api import BM_SUB, bm_types

from .manager import HotbarManager



def on_addon_data_save(bm_data: bm_types.AddonDataByMode) -> None:
    if bm_data.mode == 'SCULPT':
        HotbarManager.get().save()


BM_SUB.AddonData.SAVE += on_addon_data_save


def on_cats_remove(cat_to_remove: bm_types.Category) -> None:
    if isinstance(cat_to_remove, bm_types.BrushCat):
        HotbarManager.get().brush_sets.remove(cat_to_remove.uuid)


BM_SUB.Cats.REMOVE += on_cats_remove


def on_items_remove(item_to_remove: bm_types.Item) -> None:
    if isinstance(item_to_remove, bm_types.BrushItem):
        hm = HotbarManager.get()
        brush_set = hm.brush_sets.get(item_to_remove.cat_id)
        brush_set.unasign_brush(item_to_remove)


BM_SUB.Items.REMOVE += on_items_remove
BM_SUB.Items.MOVE_PREE += on_items_remove
