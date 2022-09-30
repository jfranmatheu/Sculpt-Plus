from datetime import datetime
from typing import List, Tuple, Union
from uuid import uuid4

from bpy.types import Context
from bpy.props import PointerProperty, IntProperty, StringProperty, BoolProperty, CollectionProperty, EnumProperty


class SCULPTPLUS_PG_id:
    name: StringProperty(default="")
    uid: StringProperty(default="")
    created_at: StringProperty()
    updated_at: StringProperty()
    

class SCULPTPLUS_PG_collection:
    class DummyClass:
        pass

    collection_type = DummyClass
    collection_name = ''

    enum_items = [('NONE', "None", ""),]

    def get_enum_items(self, context) -> Tuple:
        self.enum_items.clear()
        self.enum_items = [(item.uid, item.name, "") for item in getattr(self, self.collection_name)]
        return self.enum_items

    def update_enum(self, context):
        active_enum_item: str = self.enum
        for idx, item in enumerate(getattr(self, self.collection_name)):
            if item.uid == active_enum_item:
                self.active_index = idx
                context.area.tag_redraw()
                return

    enum: EnumProperty(
        name="List",
        items=get_enum_items,
        update=update_enum
    )

    def update_active(self, _context: Context):
        collection = getattr(self, self.collection_name)
        if self.active_index < 0 or self.active_index >= len(collection):
            return
        #self.active = collection[self.active_index]

    #active: PointerProperty(type=collection_type)
    active_index: IntProperty(default=-1, update=update_active)

    @property
    def active(self) -> collection_type:
        return getattr(self, self.collection_name)[self.active_index] if self.active_index != -1 else None

    def new_item(self) -> collection_type:
        collection = getattr(self, self.collection_name)
        item = collection.add()
        if hasattr(item, 'uid'):
            item.uid = uuid4().hex
            item.created_at = datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S")
            item.updated_at = item.created_at
        self.active_index = len(collection) - 1
        return item

    def remove_item(self, item: Union[int, collection_type]) -> None:
        collection = getattr(self, self.collection_name)
        if isinstance(item, int):
            if item < 0 or item >= len(collection):
                return
            collection.remove(item)
            return

        for idx, slot in enumerate(collection):
            if slot != item:
                continue
            return self.remove_item(idx)
