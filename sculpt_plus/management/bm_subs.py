from brush_manager.api import BM_SUB, bm_types

from ..props import hm_data


if BM_SUB.AddonData.SAVE is None:
    raise Exception("OPS! Can't Subscribe to BM events.")


def on_addon_data_save(bm_data: bm_types.AddonDataByMode) -> None:
    if bm_data.mode == 'SCULPT':
        hm_data.save()


BM_SUB.AddonData.SAVE += on_addon_data_save


def on_cats_add(new_cat: bm_types.Category) -> None:
    if isinstance(new_cat, bm_types.BrushCat) and new_cat.collection.owner.mode == 'SCULPT':
        pass


def on_cats_remove(cat_to_remove: bm_types.Category) -> None:
    if isinstance(cat_to_remove, bm_types.BrushCat) and cat_to_remove.collection.owner.mode == 'SCULPT':
        # Ensure that we unlink the BrushCat's BrushItem from their HotbarLayers.
        for item in cat_to_remove.items:
            on_items_remove(item)


BM_SUB.Cats.ADD += on_cats_add
BM_SUB.Cats.REMOVE += on_cats_remove


def on_items_add(new_item: bm_types.Item) -> None:
    if isinstance(new_item, bm_types.BrushItem) and new_item.cat.collection.owner.mode == 'SCULPT':
        # Dict: Layer ID -> Set Type.
        new_item.hotbar_layers: dict[str, str] = {}


def on_items_remove(item_to_remove: bm_types.Item) -> None:
    if isinstance(item_to_remove, bm_types.BrushItem) and item_to_remove.cat.collection.owner.mode == 'SCULPT':
        for layer_id, set_type in item_to_remove.hotbar_layers.items():
            if layer := hm_data.layers.get(layer_id):
                if set_type == 'ALT':
                    layer.brush_set_alt.unasign_brush(item_to_remove)
                else:
                    layer.brush_set.asign_brush(item_to_remove)


BM_SUB.Items.ADD += on_items_add
BM_SUB.Items.REMOVE += on_items_remove
