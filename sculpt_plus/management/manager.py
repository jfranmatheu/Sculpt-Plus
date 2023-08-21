import json
from os.path import exists, isfile
from typing import Iterator, List
from collections import OrderedDict
from pathlib import Path
import pickle

from sculpt_plus.path import SculptPlusPaths

from brush_manager.api import bm_types, BM_DATA

bm_data = BM_DATA.SCULPT


builtin_brush_names = ('Blob', 'Boundary', 'Clay', 'Clay Strips', 'Clay Thumb', 'Cloth', 'Crease', 'Draw Face Sets', 'Draw Sharp', 'Elastic Deform', 'Fill/Deepen', 'Flatten/Contrast', 'Grab', 'Inflate/Deflate', 'Layer', 'Mask', 'Multi-plane Scrape', 'Multires Displacement Eraser', 'Multires Displacement Smear', 'Nudge', 'Paint', 'Pinch/Magnify', 'Pose', 'Rotate', 'Scrape/Peaks', 'SculptDraw', 'Simplify', 'Slide Relax', 'Smooth', 'Snake Hook', 'Thumb')
exclude_brush_names = {'Mask', 'Draw Face Sets', 'Simplify', 'Multires Displacement Eraser', 'Multires Displacement Smear'}
filtered_builtin_brush_names = tuple(b for b in builtin_brush_names if b not in exclude_brush_names)


class BrushSet:
    uuid: int
    owner: 'BrushSet_Collection'

    cat_id: str
    brushes: List[bm_types.BrushItem]
    brushes_alt: List[bm_types.BrushItem]

    @property
    def collection(self) -> 'BrushSet_Collection':
        return self.owner

    @property
    def cat_id(self) -> str:
        return self.uuid

    @property
    def cat(self) -> bm_types.BrushCat:
        return bm_data.get_brush_cat(self.cat_id)

    def __init__(self, collection: 'BrushSet_Collection', cat_id: str) -> None:
        self.owner = collection
        self.uuid = cat_id
        self.brushes: List[bm_types.BrushItem] = [None] * 10
        self.brushes_alt: List[bm_types.BrushItem] = [None] * 10

    def __del__(self) -> None:
        self.brushes.clear()
        self.brushes_alt.clear()

    def switch(self, index_A: int, index_B: int) -> None:
        ''' Switch brushes at specified indices. '''
        if self.collection.hotbar_manager.use_alt:
            self.brushes_alt[index_A], self.brushes_alt[index_B] = self.brushes_alt[index_B], self.brushes_alt[index_A]
        else:
            self.brushes[index_A], self.brushes[index_B] = self.brushes[index_B], self.brushes[index_A]

    def asign_brush(self, brush: bm_types.BrushItem | str, at_index: int) -> None:
        # print("asign_brush '", brush.name, "' to index ", at_index)
        cat = self.cat
        if cat is None:
            print("Can't asign Brush! BrushSet could not find its associated BrushCat with ID:", self.cat_id)
            return
        if at_index < 0 or at_index > 9:
            print("Index out of range! Expected a value between 0 and 9")
            return

        if 'HOTBAR' in brush.flags:
            self.unasign_brush(brush)
            return

        brush = cat.items.get(brush) if isinstance(brush, str) else brush
        if self.collection.hotbar_manager.use_alt:
            self.brushes_alt[at_index] = brush
        else:
            self.brushes[at_index] = brush
        brush.flags.add('HOTBAR')

    def unasign_brush(self, brush: bm_types.BrushItem | str) -> None:
        ''' Call this function when detect that the brush is moved to another BrushCat or the BrushItem was removed. '''
        cat = self.cat
        if cat is None:
            print("Can't un-asign Brush! BrushSet could not find its associated BrushCat with ID:", self.cat_id)
            return
        brush = cat.items.get(brush) if isinstance(brush, str) else brush
        if 'HOTBAR' not in brush.flags:
            return
        if brush in self.brushes:
            self.brushes[self.brushes.index(brush)] = None
            brush.flags.remove('HOTBAR')
        elif brush in self.brushes_alt:
            self.brushes_alt[self.brushes_alt.index(brush)] = None
            brush.flags.remove('HOTBAR')
        else:
            print("WARN! Trying to unasign a BrushItem that is not set for this BrushSet")

    # ---------------------------

    def clear_owners(self) -> None:
        self.owner = None
        # Convert BrushItem references to strings (UUIDs).
        self.brushes = [brush.uuid if brush is not None else '' for brush in self.brushes]
        self.brushes_alt = [brush.uuid if brush is not None else '' for brush in self.brushes_alt]

    def ensure_owners(self, collection: 'BrushSet_Collection') -> None:
        self.owner = collection
        # Convert brush UUIDs back to BrushItem references.
        if cat := self.cat:
            get_cat_item = cat.items.get
            self.brushes = [get_cat_item(brush_uuid) if brush_uuid != '' else None for brush_uuid in self.brushes]
            self.brushes_alt = [get_cat_item(brush_uuid) if brush_uuid != '' else None for brush_uuid in self.brushes_alt]
        else:
            print("BrushSet could not find its associated BrushCat with ID:", self.cat_id)
            print("Will remove this BrushSet from the HotbarManager.brush_sets Collection")
            self.collection.remove(self)



class BrushSet_Collection:
    active: BrushSet
    sets: OrderedDict[str, BrushSet]
    owner: 'HotbarManager'

    @property
    def hotbar_manager(self) -> 'HotbarManager':
        return self.owner

    @property
    def count(self) -> int:
        return len(self.sets)

    @property
    def active(self) -> BrushSet | None:
        if act_brush_set := self.get(self._active):
            return act_brush_set
        # No active brush set :-(
        # There's a valid active category???
        if act_cat := bm_data.brush_cats.active:
            # Look for the brush-set associated to this active category.
            if act_brush_set := self.get(act_cat.uuid):
                self._active = act_cat.uuid
                return act_brush_set
            # IF not... Create a new brush set for this category!
            return self.add(act_cat)
        return None

    @property
    def active_id(self) -> str:
        return self._active

    @active.setter
    def active(self, brush_set: str | BrushSet) -> None:
        if brush_set is None:
            self._active = ''
            return
        if not isinstance(brush_set, (str, BrushSet)):
            raise TypeError("Expected an BrushSet instance or a string (uuid)")
        self._active = brush_set if isinstance(brush_set, str) else brush_set.uuid

    def __init__(self, hm: 'HotbarManager') -> None:
        self.sets = OrderedDict()
        self._active = ''
        self.owner = hm

    def __iter__(self) -> Iterator[BrushSet]:
        return iter(self.sets.values())

    def __getitem__(self, uuid_or_index: str | int) -> BrushSet | None:
        if isinstance(uuid_or_index, str):
            return self.sets.get(uuid_or_index, None)
        elif isinstance(uuid_or_index, int):
            index: int = uuid_or_index
            if index < 0 or index >= len(self.sets):
                return None
            return list(self.sets.values())[index]
        raise TypeError("Expected int (index) or string (uuid)")

    def get(self, uuid: str) -> BrushSet | None:
        # Wrapper for __getitem__ method.
        return self[uuid]

    def select(self, brush_set: str | BrushSet | int) -> None:
        if isinstance(brush_set, BrushSet):
            return self.select(brush_set.uuid)
        if isinstance(brush_set, int):
            index: int = brush_set
            return self.select(list(self.sets.keys())[index])
        if isinstance(brush_set, str) and brush_set in self.sets:
            self._active = brush_set

    def add(self, cat: bm_types.BrushCat | str) -> BrushSet:
        if not isinstance(cat, (bm_types.BrushCat, str)):
            raise TypeError("Can't create BrushSet! Invalid BrushCat type: %s" % str(type(cat)))
        # Construct a new BrushSet.
        cat_id: str = cat if isinstance(cat, str) else cat.uuid
        if cat_id in self.sets:
            print("WARN! A BrushSet from this BrushCat already exists!")
            return self[cat_id]
        brush_set = BrushSet(self, cat_id)
        # Link the brush_set to this category.
        self.sets[brush_set.uuid] = brush_set
        self._active = brush_set.uuid
        return brush_set

    def remove(self, brush_set: BrushSet | str) -> None | BrushSet:
        ''' In case a category got removed, we need to remove the BrushSet that is associated. '''
        if isinstance(brush_set, str):
            if brush_set == self.active:
                self.active = None
            del self.sets[brush_set]
        elif isinstance(brush_set, BrushSet):
            return self.remove(brush_set.uuid)
        raise TypeError("Expected int (index) or string (uuid)")

    def clear(self) -> None:
        self.sets.clear()
        self._active = ''

    def __del__(self) -> None:
        for brush_set in reversed(self.sets):
            del brush_set
        self.owner = None
        self.clear()

    # ---------------------------

    def clear_owners(self) -> None:
        self.owner = None
        for brush_set in self.sets.values():
            brush_set.clear_owners()

    def ensure_owners(self, hm: 'HotbarManager') -> None:
        self.owner = hm
        for brush_set in self.sets.values():
            brush_set.ensure_owners(self)



class HotbarManager:
    # Singleton.
    # ------------------------------------------
    _instance = None

    @classmethod
    def get(cls) -> 'HotbarManager':
        # Try to load data from file.
        data_filepath: Path = SculptPlusPaths.HOTBAR_DATA(as_path=True)

        if not data_filepath.exists():
            cls._instance = HotbarManager()
        else:
            with data_filepath.open('rb') as data_file:
                data: HotbarManager = pickle.load(data_file)
                cls._instance = data

        return cls._instance


    def save(self) -> None:
        data_filepath: Path = SculptPlusPaths.HOTBAR_DATA(as_path=True)

        # Avoid multiple references to objects since pickle doesn't work really well with that.
        self.brush_sets.clear_owners()

        with data_filepath.open('wb') as data_file:
            pickle.dump(self, data_file)

        # Restore references...
        self.brush_sets.ensure_owners(self)


    # Properties
    # ------------------------------------------
    brush_sets: BrushSet_Collection
    ## active_brush: bm_types.BrushItem

    use_alt: bool

    is_data_loaded: bool

    @property
    def active_brush_cat(self) -> bm_types.BrushCat:
        return bm_data.get_brush_cat(self.brush_sets.active.cat_id)

    @property
    def brushes(self) -> List[bm_types.BrushItem]:
        act_brush_set = self.brush_sets.active
        if act_brush_set is None:
            return []
        if self.use_alt:
            return act_brush_set.brushes_alt
        return act_brush_set.brushes

    @property
    def brushes_ids(self) -> List[str]:
        return [b.uuid if b else '' for b in self.brushes]

    ## @property
    ## def active_brush(self) -> bm_types.BrushItem | None:
    ##     cat_id, brush_id = self._active_brush
    ##     if cat_id == '' or brush_id == '':
    ##         return None
    ##     if cat := bm_data.brush_cats.get(cat_id):
    ##         return cat.items.get(brush_id)

    ## @active_brush.setter
    ## def active_brush(self, brush_item: bm_types.BrushItem) -> None:
    ##     self._active_brush = brush_item.cat_id, brush_item.uuid


    # Constructor and free.
    # ------------------------------------------
    def __init__(self):
        self.active_cat_id = ''
        ## self._active_brush = '', ''
        self.brush_sets = BrushSet_Collection(self)

        self.use_alt: bool = False

        self.is_data_loaded = False

    def __del__(self):
        del self.brush_sets
        HotbarManager._instance = None

    # Util methods.
    # ------------------------------------------
    def toggle_alt(self) -> None:
        self.use_alt = not self.use_alt
