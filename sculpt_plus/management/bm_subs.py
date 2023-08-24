from brush_manager.api import BM_SUB, bm_types

from sculpt_plus.globals import G


default_layer_brush_set_brushes = (
    'SculptDraw',      # 1
    'Draw Sharp',       # 2
    'Clay Strips',      # 3
    'Blob',             # 4
    'Inflate/Deflate',  # 5
    'Crease',           # 6
    'Pinch/Magnify',    # 7
    'Grab',             # 8
    'Elastic Deform',   # 9
    'Scrape/Peaks',     # 0
)
_default_layer_brush_set_brushes = set(default_layer_brush_set_brushes)


if BM_SUB.AddonData.SAVE is None:
    raise Exception("OPS! Can't Subscribe to BM events.")


def on_addon_data_init(bm_data: bm_types.AddonDataByMode) -> None:
    if bm_data.mode != 'SCULPT':
        return

    def_cat = bm_data.brush_cats.get('DEFAULT')
    if def_cat is None:
        print("no cat")
        return

    def_layer = G.hm_data.layers.get('DEFAULT')
    if def_layer is None:
        print("no layer")
        return

    print("[Sculpt+] brush_manager data initialized... filling default hotbar layer...") #, def_layer, def_layer.name, def_layer.uuid)

    link_brush = def_layer.link_brush
    G.hm_data.layers.select(def_layer)
    for brush_item in def_cat.items:
        if brush_item.name in _default_layer_brush_set_brushes:
            link_brush(brush_item, default_layer_brush_set_brushes.index(brush_item.name))
        # print(brush_item.name, brush_item.hotbar_layers)

    G.hm_data.save()


def on_addon_data_save(bm_data: bm_types.AddonDataByMode) -> None:
    if bm_data.mode == 'SCULPT':
        G.hm_data.save()

BM_SUB.AddonData.INIT += on_addon_data_init
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
            if layer := G.hm_data.layers.get(layer_id):
                layer.unlink_brush(item_to_remove)


BM_SUB.Items.ADD += on_items_add
BM_SUB.Items.REMOVE += on_items_remove
