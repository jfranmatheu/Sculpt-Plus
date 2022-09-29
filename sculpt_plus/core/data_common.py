from datetime import datetime
from typing import List, Union
from uuid import uuid4

from bpy.types import Context
from bpy.props import PointerProperty, IntProperty, StringProperty, BoolProperty, CollectionProperty


class SCULPTPLUS_PG_id:
    uid: StringProperty(default="")
    created_at: StringProperty()
    updated_at: StringProperty()

class SCULPTPLUS_PG_collection:
    class DummyClass:
        pass

    collection_type = DummyClass
    collection_name = ''

    def update_active(self, _context: Context):
        collection = getattr(self, self.collection_name)
        if self.active_index < 0 or self.active_index >= len(collection):
            return
        #self.active = collection[self.active_index]

    #active: PointerProperty(type=collection_type)
    active_index: IntProperty(default=-1, update=update_active)
    
    @property
    def active(self) -> collection_type:
        return getattr(self, self.collection_name)[self.active_index]

    def new_item(self) -> collection_type:
        collection = getattr(self, self.collection_name)
        item = collection.add()
        if hasattr(item, 'uid'):
            item.uid = uuid4().hex
            item.created_at = datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S")
            item.updated_at = item.created_at
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
