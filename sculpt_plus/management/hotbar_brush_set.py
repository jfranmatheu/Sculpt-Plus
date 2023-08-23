from typing import List

from brush_manager.api import bm_types, BM_DATA

bm_data = BM_DATA.SCULPT



class HotbarBrushSet:
    owner: object # 'BrushSet_Collection'

    brushes: List[bm_types.BrushItem]

    @property
    def layer(self): # -> 'BrushSet_Collection':
        from .hotbar_layer import HotbarLayer
        layer: HotbarLayer = self.owner
        return layer

    @property
    def brushes_ids(self) -> List[str]:
        return [b.uuid if b is not None else '' for b in self.brushes]

    def __init__(self, layer, set_size: int = 10, type: str = 'MAIN') -> None:
        self.owner = layer
        self.brushes: List[bm_types.BrushItem] = [None] * set_size
        self.type = type

    def __del__(self) -> None:
        self.brushes.clear()

    def switch(self, index_A: int, index_B: int) -> None:
        ''' Switch brushes at specified indices. '''
        self.brushes[index_A], self.brushes[index_B] = self.brushes[index_B], self.brushes[index_A]

    def asign_brush(self, brush: bm_types.BrushItem | str, at_index: int) -> None:
        # print("asign_brush '", brush.name, "' to index ", at_index)
        if at_index < 0 or at_index > 9:
            print("ERROR! Index out of range! Expected a value between 0 and 9")
            return

        if self.layer.uuid in brush.hotbar_layers:
            # BrushItem already in layer but in another Set.
            # IGNORE BY NOW...
            print("WARN! BrushItem already in target Layer OR in another Set of the same Layer!")
            return

        if self.brushes[at_index] is not None:
            self.unasign_brush(self.brushes[at_index])

        self.brushes[at_index] = brush
        brush.hotbar_layers[self.layer.uuid] = self.type

    def unasign_brush(self, brush: bm_types.BrushItem | str) -> None:
        ''' Call this function when detect that the brush is moved to another BrushCat or the BrushItem was removed. '''
        if brush not in self.brushes:
            return

        self.brushes[self.brushes.index(brush)] = None
        del brush.hotbar_layers[self.layer.uuid]

    # ---------------------------

    def clear_owners(self) -> None:
        self.owner = None
        # Convert BrushItem references to strings (UUIDs).
        self.brushes = [(brush.cat_id, brush.uuid) if brush is not None else ('', '') for brush in self.brushes]

    def ensure_owners(self, layer) -> None:
        self.owner = layer
        get_cat = bm_data.brush_cats.get
        # Convert brush UUIDs back to BrushItem references.
        self.brushes = [get_cat(cat_id).items.get(brush_uuid) if cat_id != '' else None for (cat_id, brush_uuid) in self.brushes]
