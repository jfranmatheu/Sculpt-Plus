from typing import List, Set, Dict, Any, Union

import bpy
from bpy.types import PropertyGroup, Context
from bpy.props import PointerProperty, IntProperty, StringProperty, BoolProperty, CollectionProperty, EnumProperty

from .data_brush_slot import SCULPTPLUS_PG_brush_slot
from .data_brush_category import SCULPTPLUS_PG_brush_category


def with_target_set_index(f):
    def wrapper(self, target_set, *args, **kwargs):
        if isinstance(target_set, SCULPTPLUS_PG_brush_category):
            for i, brush_set in enumerate(self.sets):
                if brush_set == target_set:
                    target_set = i
                    break
        if not isinstance(target_set, int):
            return None
        if target_set == -1:
            if self.active_set_index == -1:
                return None
            target_set = self.active_set_index
        return f(self, target_set, *args, **kwargs)
    return wrapper

def with_active_set(f):
    def wrapper(self, *args, **kwargs):
        if bpy.sculpt_hotbar._cv_instance:
            cv = bpy.sculpt_hotbar._cv_instance
            idx = self.alt_set_index if cv.hotbar.use_secondary and self.alt_set_index != -1 else self.active_set_index
        else:
            idx = self.active_set_index
        if idx == -1:
            return None
        # print(idx)
        return f(self, self.sets[idx], *args, **kwargs)
    return wrapper


class SCULPTPLUS_PG_brush_manager(PropertyGroup):
    ''' Brush Manager properties. '''
    active_index: IntProperty(default=-1) # , update=update_active)
    cats_coll: CollectionProperty(type=SCULPTPLUS_PG_brush_category)

    cats_enum: EnumProperty(
        name="Categories",
        items=lambda s, ctx: ((cat.uid, cat.name, "") for cat in s.collection),
        update=lambda s, ctx: s.set_active(s.enum_value)
    )

    @property
    def active(self) -> Union[SCULPTPLUS_PG_brush_category, None]:
        if self.active_index < 0 or self.active_index >= len(self.collection):
            return None
        return self.cats_coll[self.active_index]

    @property
    def collection(self) -> List[SCULPTPLUS_PG_brush_category]:
        return self.cats_coll

    @property
    def enum_value(self) -> str:
        return self.cats_enum

    @property
    def categories(self) -> List[SCULPTPLUS_PG_brush_category]:
        return [slot.brush for slot in self.slots if slot.brush]

    def get_cat(self, target_cat: Union[str, int]) -> Union[SCULPTPLUS_PG_brush_category, None]:
        if isinstance(target_cat, int):
            if target_cat < 0 or target_cat >= len(self.collection):
                return None
            return self.collection[target_cat]
        if isinstance(target_cat, str):
            for idx, cat in enumerate(self.collection):
                if cat.name == target_cat or cat.uid == target_cat:
                    return self.get_cat(idx)

    def get_cat_index(self, target_cat: Union[str, SCULPTPLUS_PG_brush_category]) -> int:
        if isinstance(target_cat, int):
            return target_cat
        if isinstance(target_cat, str):
            for idx, cat in enumerate(self.collection):
                if cat.name == target_cat or cat.uid == target_cat:
                    return idx
        if isinstance(target_cat, SCULPTPLUS_PG_brush_category):
            for idx, cat in enumerate(self.collection):
                if cat == target_cat:
                    return idx

    def set_active(self, target_cat: Union[str, int, SCULPTPLUS_PG_brush_category]) -> None:
        target_cat_index: int = self.get_cat_index(target_cat)
        if target_cat_index is not None:
            self.active_index = target_cat_index

    def new_cat(self, cat_name: str = "Untitled Cat") -> SCULPTPLUS_PG_brush_category:
        cat: SCULPTPLUS_PG_brush_category = self.collection.add()
        cat.name = cat_name
        cat.setup_id()
        cat.setup_date()

        self.active_index = len(self.collection) - 1
        return cat

    def remove_cat(self, target_cat: Union[SCULPTPLUS_PG_brush_category, int, str]) -> None:
        target_cat_index: int = self.get_cat_index(target_cat)
        if target_cat_index is None:
            return
        self.collection[target_cat_index].brush = None
        self.collection.remove(target_cat_index)
        # Fix index.
        if self.active_index == target_cat_index:
            self.active_index -= 1

    def clear_cats(self) -> None:
        {cat.clear() for cat in self.collection}
        self.collection.clear()

    def setup(self):
        print("Setup..")
        #if len(self.categories) > 0:
        #    return
        def_brushes = (
            'Clay Strips',
            'Blob', 'Inflate/Deflate',
            'Draw Sharp', 'Crease', 'Pinch/Magnify',

            'Grab',
            'Elastic Deform',
            'Snake Hook',

            'Scrape/Peaks',
            'Pose', 'Cloth',
            #'Mask', 'Draw Face Sets'
        )
        cat = self.new_cat()
        cat.name = "DEFAULT"
        for br_name in def_brushes:
            cat.add_brush(bpy.data.brushes.get(br_name, None))

    def init(self):
        self.setup()
