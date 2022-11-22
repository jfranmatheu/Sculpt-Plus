from typing import List, Set, Dict, Any

import bpy
from bpy.types import PropertyGroup, Brush, Context
from bpy.props import PointerProperty, IntProperty, StringProperty, BoolProperty, CollectionProperty, EnumProperty

from sculpt_plus.core.data.common import PG_id
from sculpt_plus.props import Props


class SCULPTPLUS_PG_brush_slot(PropertyGroup, PG_id):
    ''' Brush properties. '''
    tag_to_remove: BoolProperty(default=False)

    def clear(self) -> None:
        self.brush = None        

    def on_update_brush(self, context: Context) -> None:
        if self.brush is None and not self.tag_to_remove:
            Props.ActiveBrushCat(context).remove_brush(self)

    brush: PointerProperty(type=Brush, update=on_update_brush)
