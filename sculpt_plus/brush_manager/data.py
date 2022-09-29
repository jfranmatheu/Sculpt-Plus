from typing import List

from bpy.types import PropertyGroup, Brush, Context
from bpy.props import PointerProperty, IntProperty, StringProperty, BoolProperty, CollectionProperty

from sculpt_plus.core.data_common import SCULPTPLUS_PG_id, SCULPTPLUS_PG_collection


class SCULPTPLUS_PG_slot(PropertyGroup, SCULPTPLUS_PG_id):
    ''' Brush properties. '''
    def update_brush(self, context: Context) -> None:
        if self.brush is None:
            context.window_manager.sculpt_plus.sets.active_set.remove_slot(self)

    brush: PointerProperty(type=Brush, update=update_brush)


class SCULPTPLUS_PG_slot_set(PropertyGroup, SCULPTPLUS_PG_id, SCULPTPLUS_PG_collection):
    ''' Brush Set properties. '''
    collection_type = SCULPTPLUS_PG_slot
    collection_name = 'slots'
    slots: CollectionProperty(type=SCULPTPLUS_PG_slot)

    @property
    def brushes(self) -> List[Brush]:
        return [slot.brush for slot in self.slots if slot.brush]

    def new_slot(self) -> SCULPTPLUS_PG_slot: return self.new_item()
    def remove_slot(self, item) -> None: self.remove_item(item)


class SCULPTPLUS_PG_brush_manager(PropertyGroup, SCULPTPLUS_PG_collection):
    ''' Brush Manager properties. '''
    collection_type = SCULPTPLUS_PG_slot_set
    collection_name = 'sets'
    sets: CollectionProperty(type=SCULPTPLUS_PG_slot_set)

    def new_set(self) -> SCULPTPLUS_PG_slot_set: return self.new_item()
    def remove_set(self, item) -> None: self.remove_item(item)
