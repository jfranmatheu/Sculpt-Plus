from os import path, listdir, mkdir, rename, remove
from typing import List, Set, Dict, Any, Union
from uuid import uuid4

import bpy
from bpy.types import PropertyGroup, Brush, Context, Image
from bpy.props import PointerProperty, IntProperty, StringProperty, BoolProperty, CollectionProperty, EnumProperty

from sculpt_plus.core.data.common import PG_id_date
from sculpt_plus.prefs import get_prefs
from sculpt_plus.props import Props

from .data_brush_slot import SCULPTPLUS_PG_brush_slot


class SCULPTPLUS_PG_brush_category(PropertyGroup, PG_id_date):
    ''' Brush Set properties. '''
    icon: PointerProperty(type=Image)
    brushes_coll: CollectionProperty(type=SCULPTPLUS_PG_brush_slot)
    # brushes_enum: EnumProperty()

    version: IntProperty(default=0)

    @property
    def collection(self) -> List[SCULPTPLUS_PG_brush_slot]:
        return self.brushes_coll

    @property
    def enum_value(self) -> str:
        return self.brushes_enum

    @property
    def brushes(self) -> List[Brush]:
        return [slot.brush for slot in self.slots if slot.brush]

    def add_brush(self, brush: Brush = None) -> SCULPTPLUS_PG_brush_slot:
        if brush is None or not isinstance(brush, Brush) or not brush.use_paint_sculpt:
            return
        brush_slot: SCULPTPLUS_PG_brush_slot = self.collection.add()
        brush_slot.brush = brush
        brush_slot.name = brush.name if brush else 'NULL'
        brush_slot.setup_id()
        brush.use_fake_user = False
        if 'cat_id' in brush:
            other_cat: SCULPTPLUS_PG_brush_category = Props.GetBrushCat(bpy.context, brush['cat_id'])
            if other_cat:
                other_cat.remove_brush(brush)
        brush['cat_id'] = self.uid
        if 'sculpt_plus_id' in brush:
            brush_slot.uid = brush['sculpt_plus_id']
        else:
            brush['sculpt_plus_id'] = brush_slot.uid
        return brush_slot

    def replace_brush(self, brush: Brush, slot_index: int) -> None:
        ''' Safe brush asignation to an existing slot. '''
        if brush is None or not isinstance(brush, Brush) or not brush.use_paint_sculpt:
            return
        if slot_index < 0 or slot_index >= len(self.slots):
            return
        self.slots[slot_index].brush = brush
        if 'cat_id' in brush:
            other_cat: SCULPTPLUS_PG_brush_category = Props.GetBrushCat(bpy.context, brush['cat_id'])
            if other_cat:
                other_cat.remove_brush(brush)
        brush['cat_id'] = self.uid

    def remove_brush(self, brush_slot: Union[SCULPTPLUS_PG_brush_slot, int, str, Brush]) -> None:
        if isinstance(brush_slot, int):
            if brush_slot < 0 or brush_slot >= len(self.collection):
                return
            brush = self.collection[brush_slot].brush
            if brush:
                if 'cat_id' in brush:
                    del brush['cat_id']
            self.collection[brush_slot].tag_to_remove = True # Avoid the update callback.
            self.collection[brush_slot].brush = None
            self.collection.remove(brush_slot)
            return

        if isinstance(brush_slot, Brush):
            for idx, slot in enumerate(self.collection):
                if slot.brush == brush_slot:
                    return self.remove_brush(idx)

        if isinstance(brush_slot, str):
            for idx, slot in enumerate(self.collection):
                if slot.name == brush_slot or slot.uid == brush_slot:
                    return self.remove_brush(idx)

        if isinstance(brush_slot, SCULPTPLUS_PG_brush_slot):
            for idx, slot in enumerate(self.collection):
                if slot != brush_slot:
                    continue
                return self.remove_brush(idx)

    def clear(self) -> None:
        self.collection.clear()

    def destroy(self, context) -> None:
        self.clear()
        Props.BrushManager(context).remove_cat(self)

    def save(self, context) -> None:
        from .io import export_brush_category
        export_brush_category(self, context)

    def serialize(self) -> Dict[str, Any]:
        return {
            'id': self.uid,
            'name': self.name,
            'version': self.version,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'brushes': [
                brush['sculpt_plus_id'] for brush in self.brushes
            ]
        }
