from bpy.types import PropertyGroup
from bpy.props import PointerProperty


try:
    from sculpt_plus.brush_manager.data import SCULPTPLUS_PG_brush_manager as PG_BrushManager
except:
    PG_BrushManager = type("DummyPG", (PropertyGroup,))


class SCULPTPLUS_PG_wm(PropertyGroup):
    manager: PointerProperty(type=PG_BrushManager)
