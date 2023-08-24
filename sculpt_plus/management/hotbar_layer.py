from collections import OrderedDict
from typing import List, Iterator
from uuid import uuid4

from brush_manager.api import bm_types
from .hotbar_brush_set import HotbarBrushSet


class HotbarLayer:
    owner: 'HotbarLayer_Collection'
    uuid: str
    name: str

    brush_set: HotbarBrushSet
    brush_set_alt: HotbarBrushSet

    @property
    def collection(self) -> 'HotbarLayer_Collection':
        return self.owner

    @property
    def active_set(self) -> HotbarBrushSet:
        return self.brush_set_alt if self.collection.hotbar_manager.use_alt else self.brush_set

    @property
    def brushes(self) -> List[bm_types.BrushItem]:
        ''' Wrapper. '''
        return self.active_set.brushes

    @property
    def brushes_ids(self) -> List[str]:
        ''' Wrapper. '''
        return self.active_set.brushes_ids

    def __init__(self, collection: 'HotbarLayer_Collection', name: str = 'Layer', custom_uuid: str | None = None) -> None:
        self.owner = collection
        self.uuid = uuid4().hex if custom_uuid is None else custom_uuid
        self.name = name
        self.brush_set = HotbarBrushSet(self, set_size=10, type='MAIN')
        self.brush_set_alt = HotbarBrushSet(self, set_size=10, type='ALT')

        #### print("Creating new Layer for hotbar:", collection, collection.hotbar_manager)

    def __del__(self) -> None:
        del self.brush_set
        del self.brush_set_alt

    def switch(self, index_A: int, index_B: int) -> None:
        ''' Wrapper. '''
        self.active_set.switch(index_A, index_B)

    def link_brush(self, brush: bm_types.BrushItem, at_index: int) -> None:
        ''' Wrapper. '''
        self.active_set.asign_brush(brush, at_index)

    def unlink_brush(self, brush: bm_types.BrushItem) -> None:
        set_type = brush.hotbar_layers[self.uuid]
        if set_type == 'MAIN':
            self.brush_set.unasign_brush(brush)
        elif set_type == 'ALT':
            self.brush_set_alt.unasign_brush(brush)

    # ---------------------------

    def clear_owners(self) -> None:
        self.owner = None
        # Convert BrushItem references to strings (UUIDs).
        self.brush_set.clear_owners()
        self.brush_set_alt.clear_owners()

    def ensure_owners(self, collection: 'HotbarLayer_Collection') -> None:
        self.owner = collection
        self.brush_set.ensure_owners(self)
        self.brush_set_alt.ensure_owners(self)



class HotbarLayer_Collection:
    active: HotbarLayer
    layers: OrderedDict[str, HotbarLayer]
    owner: object

    @property
    def hotbar_manager(self):
        return self.owner

    @property
    def count(self) -> int:
        return len(self.layers)

    @property
    def active(self) -> HotbarLayer | None:
        return self.get(self._active)

    @property
    def active_id(self) -> str:
        return self._active

    @active.setter
    def active(self, layer: str | HotbarLayer) -> None:
        if layer is None:
            self._active = ''
            return
        if not isinstance(layer, (str, HotbarLayer)):
            raise TypeError("Expected an HotbarLayer instance or a string (uuid)")
        self._active = layer if isinstance(layer, str) else layer.uuid

    def __init__(self, hm: object) -> None:
        self.layers = OrderedDict()
        self._active = ''
        self.owner = hm

    def __iter__(self) -> Iterator[HotbarLayer]:
        return iter(self.layers.values())

    def __getitem__(self, uuid_or_index: str | int) -> HotbarLayer | None:
        if isinstance(uuid_or_index, str):
            return self.layers.get(uuid_or_index, None)
        elif isinstance(uuid_or_index, int):
            index: int = uuid_or_index
            if index < 0 or index >= len(self.layers):
                return None
            return list(self.layers.values())[index]
        raise TypeError("Expected int (index) or string (uuid)")

    def get(self, uuid: str) -> HotbarLayer | None:
        # Wrapper for __getitem__ method.
        return self[uuid]

    def select(self, layer: str | HotbarLayer | int) -> None:
        if isinstance(layer, HotbarLayer):
            return self.select(layer.uuid)
        if isinstance(layer, int):
            index: int = layer
            return self.select(list(self.layers.keys())[index])
        if isinstance(layer, str) and layer in self.layers:
            self._active = layer

    def add(self, name: str = 'New Layer', custom_uuid: str | None = None) -> HotbarLayer:
        # Construct a new BrushSet.
        layer = HotbarLayer(self, name, custom_uuid=custom_uuid)
        self.layers[layer.uuid] = layer
        self._active = layer.uuid
        return layer

    def remove(self, layer: HotbarLayer | str) -> None | HotbarLayer:
        if isinstance(layer, str):
            if layer == self.active:
                self.active = None
            del self.layers[layer]
            # Ensure there is an active layer.
            if self.active is None:
                if self.count == 0:
                    self.add('Default', 'DEFAULT')
                else:
                    self.select(0)
        elif isinstance(layer, HotbarLayer):
            return self.remove(layer.uuid)
        raise TypeError("Expected int (index) or string (uuid)")

    def clear(self) -> None:
        self.layers.clear()
        self._active = ''

    def __del__(self) -> None:
        for layer in reversed(self.layers):
            del layer
        self.owner = None
        self.clear()

    # ---------------------------

    def clear_owners(self) -> None:
        self.owner = None
        for layer in self:
            layer.clear_owners()

    def ensure_owners(self, hm: object) -> None:
        self.owner = hm
        for layer in self:
            layer.ensure_owners(self)
