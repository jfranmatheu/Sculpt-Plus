from bpy.types import Scene as scn, PropertyGroup
from bpy.props import PointerProperty, BoolProperty


class SculptHotbarPG(PropertyGroup):
    show_gizmo_sculpt_hotbar : BoolProperty(default=True, description='Enable Sculpt Hotbar')


def register():
    scn.sculpt_hotbar = PointerProperty(type=SculptHotbarPG)
