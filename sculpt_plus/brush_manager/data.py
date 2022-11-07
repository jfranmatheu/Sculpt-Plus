from os import path
from typing import List, Set, Dict, Any

import bpy
from bpy.app.handlers import load_post, persistent
from bpy.types import PropertyGroup, Brush, Context
from bpy.props import PointerProperty, IntProperty, StringProperty, BoolProperty, CollectionProperty, EnumProperty

from sculpt_plus.core.data.common import SCULPTPLUS_PG_id, SCULPTPLUS_PG_collection
from sculpt_plus.prefs import get_prefs


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
    version: IntProperty(default=0)

    @property
    def brushes(self) -> List[Brush]:
        return [slot.brush for slot in self.slots if slot.brush]

    def new_slot(self, brush: Brush = None) -> SCULPTPLUS_PG_slot:
        new_slot = self.new_item()
        new_slot.brush = brush
        new_slot.name = brush.name if brush else 'NULL'
        return new_slot

    def remove_slot(self, item) -> None: self.remove_item(item)

    def save_replace(self, context) -> None:
        br_lib_dir: str = get_prefs(context).brush_lib_directory
        set_idname: str = self.uid
        set_version: str = str(self.version)
        br_set_path: str = path.join(br_lib_dir, set_idname, set_version + '.blend')
        brushes: Set[Brush] = set(self.brushes)
        bpy.data.libraries.write(br_set_path, brushes, fake_user=False)

        self.version += 1
        self.update_date()

    def asign_brush(self, brush: Brush, slot_index: int) -> None:
        ''' Safe brush asignation to an slot. '''
        if brush is None or not isinstance(brush, Brush) or not brush.use_paint_sculpt:
            return
        if slot_index < 0 or slot_index >= len(self.slots):
            return
        self.slots[slot_index].brush = brush

    def serialize(self) -> Dict[str, Any]:
        return {
            'id': self.uid,
            'name': self.name,
            'version': self.version,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'brushes': [
                
            ]
        }



class SCULPTPLUS_PG_brush_manager(PropertyGroup, SCULPTPLUS_PG_collection):
    ''' Brush Manager properties. '''
    @staticmethod
    def get_data(ctx: Context) -> 'SCULPTPLUS_PG_brush_manager':
        from sculpt_plus.core.data.wm import SCULPTPLUS_PG_wm
        return SCULPTPLUS_PG_wm.get_data(ctx).manager

    collection_type = SCULPTPLUS_PG_slot_set
    collection_name = 'sets'
    sets: CollectionProperty(type=SCULPTPLUS_PG_slot_set)

    enum: EnumProperty(
        name="Sets",
        items=SCULPTPLUS_PG_collection.get_enum_items,
        update=SCULPTPLUS_PG_collection.update_enum
    )

    def new_set(self, title: str = 'New Set') -> SCULPTPLUS_PG_slot_set:
        new_set = self.new_item()
        new_set.name = title
        return new_set

    def remove_set(self, item) -> None:
        self.remove_item(item)

    def setup(self):
        if len(self.sets) > 0:
            return
        def_brushes = (
            'Clay Strips',
            'Blob', 'Inflate/Deflate',
            'Draw Sharp', 'Crease', 'Pinch/Magnify',

            'Grab',
            'Elastic Deform',
            'Snake Hook',

            'Scrape/Peaks',
            #'Pose', 'Cloth',
            #'Mask', 'Draw Face Sets'
        )
        brush_set: SCULPTPLUS_PG_slot_set = self.new_set()
        brush_set.name = "DEFAULT"
        for br_name in def_brushes:
            brush_set.new_slot(bpy.data.brushes.get(br_name, None))
