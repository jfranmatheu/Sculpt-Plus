import bpy
from bpy.types import Brush as BlBrush, Property, PropertyGroup, Image as BlImage
from bpy.props import (
    IntProperty, IntVectorProperty,
    FloatProperty, FloatVectorProperty,
    BoolProperty, BoolVectorProperty,
    StringProperty,
    PointerProperty, CollectionProperty)
from gpu.types import Buffer, GPUTexture

from uuid import uuid4
from typing import Dict, Tuple, List, Set, Union
import numpy as np

from .image import Image



sub_property_groups = ('brush_capabilities', 'mask_texture_slot', 'sculpt_capabilities', '')

exclude_pattern_starts = ('gpencil', )
exclude_pattern_contain = {}
exclude_set = {'users', 'tag'}

brush_properties: Dict[str, Property] = lambda : bpy.types.Brush.bl_rna.properties


class Brush(BlBrush):
    id: str

    def __init__(self, brush: BlBrush):
        self.id: str = uuid4().hex
        brush['id'] = self.id

        self._attributes: List[str] = []
        for prop_name, prop in brush_properties.items():
            if prop_name in exclude_set:
                continue
            if prop_name.startswith(exclude_pattern_starts):
                continue
            if isinstance(prop, CollectionProperty):
                continue
            value = getattr(brush, prop_name)
            if isinstance(value, BlImage):
                value = Image(value)
            self.add_property(prop_name, value)

    def add_property(self, attr, value):
        setattr(self, attr, value)
        self._attributes.append(attr)
