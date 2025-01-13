from enum import Enum
from math import pi

from bpy.props import *

from .property_enum import EnumPropertyHelper, DynamicEnumPropertyHelper
from .property_pointer import PointerPropertyTypes

from mathutils import Matrix

IdentityMatrix_2 = Matrix.Identity(2)
IdentityMatrix_3 = Matrix.Identity(3)
IdentityMatrix_4 = Matrix.Identity(4)


class PropertyTypes:
    FLOAT = FloatProperty
    INT = IntProperty
    BOOL = BoolProperty
    FLOAT_VECTOR = FloatVectorProperty
    INT_VECTOR = IntVectorProperty
    BOOL_VECTOR = BoolVectorProperty
    ENUM = EnumProperty
    STRING = StringProperty
    POINTER_CUSTOM = PointerProperty

    ANGLE_DEGREE = lambda name, default = 0, min = -pi, max = pi, **kwargs: FloatProperty(name=name, default=default, min=min, max=max, subtype='ANGLE', unit='ROTATION', **kwargs)
    FACTOR = lambda name, default = 0, **kwargs: FloatProperty(name=name, default=default, min=0, max=1, **kwargs)

    IVECTOR_2 = lambda default = (0, 0), **kwargs: IntVectorProperty(default=default, size=2, **kwargs)
    IVECTOR_3 = lambda default = (0, 0, 0), **kwargs: IntVectorProperty(default=default, size=3, **kwargs)
    IVECTOR_XY = lambda default = (0, 0), **kwargs: IntVectorProperty(default=default, size=2, subtype='XYZ', **kwargs)
    IVECTOR_XYZ = lambda default = (0, 0, 0), **kwargs: IntVectorProperty(default=default, size=3, subtype='XYZ', **kwargs)
    IVECTOR_N = lambda default, **kwargs: IntVectorProperty(default=default, size=len(default), **kwargs)
    VECTOR_2 = lambda default = (0, 0), **kwargs: FloatVectorProperty(default=default, size=2, **kwargs)
    VECTOR_3 = lambda default = (0, 0, 0), **kwargs: FloatVectorProperty(default=default, size=3, **kwargs)
    VECTOR_XY = lambda default = (0, 0), **kwargs: FloatVectorProperty(default=default, size=2, subtype='XYZ', **kwargs)
    VECTOR_XYZ = lambda default = (0, 0, 0), **kwargs: FloatVectorProperty(default=default, size=3, subtype='XYZ', **kwargs)
    VECTOR_AXISANGLE = lambda default = (0, 0, 0), **kwargs: FloatVectorProperty(default=default, size=3, subtype='AXISANGLE', **kwargs)
    VECTOR_N = lambda default, **kwargs: FloatVectorProperty(default=default, size=len(default), **kwargs)

    COLOR_RGB = lambda name, default_color, **kwargs: FloatVectorProperty(name=name, default=default_color, min=0.0, max=1.0, size=3, subtype='COLOR', **kwargs)
    COLOR_RGBA = lambda name, default_color, **kwargs: FloatVectorProperty(name=name, default=default_color, min=0.0, max=1.0, size=4, subtype='COLOR', **kwargs)

    MATRIX_2 = lambda name, **kwargs: FloatVectorProperty(name=name, default=IdentityMatrix_2, size=(2, 2), **kwargs)
    MATRIX_3 = lambda name, **kwargs: FloatVectorProperty(name=name, default=IdentityMatrix_3, size=(3, 3), **kwargs)
    MATRIX_4 = lambda name, **kwargs: FloatVectorProperty(name=name, default=IdentityMatrix_4, size=(4, 4), **kwargs)
    MATRIX_N = lambda name, default, **kwargs: FloatVectorProperty(name=name, default=default, size=(len(default), len(default[0])), **kwargs)

    DIRPATH = lambda **kwargs: StringProperty(subtype='DIR_PATH', **kwargs)
    FILEPATH = lambda **kwargs: StringProperty(subtype='FILE_PATH', **kwargs)

    POINTER = PointerPropertyTypes
    COLLECTION = lambda type, **kwargs: CollectionProperty(type=type, **kwargs)

    ENUM_HELPER = EnumPropertyHelper
    ENUM_DYNAMIC = DynamicEnumPropertyHelper


class PropertyEnum(Enum):
    FLOAT = FloatProperty
    INT = IntProperty
    BOOL = BoolProperty
    FLOAT_VECTOR = FloatVectorProperty
    INT_VECTOR = IntVectorProperty
    BOOL_VECTOR = BoolVectorProperty
    ENUM = EnumProperty
    STRING = StringProperty
    POINTER_CUSTOM = PointerProperty
    COLLECTION = CollectionProperty

    def __init__(self, name: str):
        self.prop = self.value
        self.kwargs = {}

    def set_limit(self, min: float, max: float) -> 'PropertyEnum':
        self.kwargs['min'] = min
        self.kwargs['max'] = max

    def set_soft_limit(self, soft_min: float, soft_max: float) -> 'PropertyEnum':
        self.kwargs['soft_min'] = soft_min
        self.kwargs['soft_max'] = soft_max

    def set_dimensions(self, ndim: int | tuple[int]) -> 'PropertyEnum':
        self.kwargs['size'] = ndim
        if 'default' not in self.kwargs:
            if isinstance(ndim, tuple):
                self.kwargs['default'] = [[0] * ndim[0]] * ndim[1]
            else:
                self.kwargs['default'] = [0] * ndim
