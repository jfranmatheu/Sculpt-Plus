from brush_manager.api import BM_SUB, bm_types

from ..props import hm_data



def on_addon_data_save(bm_data: bm_types.AddonDataByMode) -> None:
    if bm_data.mode == 'SCULPT':
        hm_data.save()


BM_SUB.AddonData.SAVE += on_addon_data_save


def on_cats_add(new_cat: bm_types.Category) -> None:
    if isinstance(new_cat, bm_types.BrushCat):
        # Initialize new BrushSet for the new BrushCat.
        hm_data.brush_sets.add(new_cat)


def on_cats_remove(cat_to_remove: bm_types.Category) -> None:
    if isinstance(cat_to_remove, bm_types.BrushCat):
        # Ensure that we remove the BrushSet associated with the removed BrushCat.
        hm_data.brush_sets.remove(cat_to_remove.uuid)


BM_SUB.Cats.ADD += on_cats_add
BM_SUB.Cats.REMOVE += on_cats_remove


def on_items_remove(item_to_remove: bm_types.Item) -> None:
    if isinstance(item_to_remove, bm_types.BrushItem):
        brush_set = hm_data.brush_sets.get(item_to_remove.cat_id)
        brush_set.unasign_brush(item_to_remove)


BM_SUB.Items.REMOVE += on_items_remove
BM_SUB.Items.MOVE_PRE += on_items_remove
