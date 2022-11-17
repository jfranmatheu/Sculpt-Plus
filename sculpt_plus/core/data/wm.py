from bpy.types import PropertyGroup, Context, WindowManager as WM
from bpy.props import PointerProperty

from sculpt_plus.brush_manager.data_brush_manager import SCULPTPLUS_PG_brush_manager as PG_BrushManager
'''
try:
    from sculpt_plus.brush_manager.data_brush_manager import SCULPTPLUS_PG_brush_manager as PG_BrushManager
except:
    PG_BrushManager = type("DummyPG", (PropertyGroup,), {})
'''

class SCULPTPLUS_PG_wm(PropertyGroup):
    @staticmethod
    def get_data(ctx: Context) -> 'SCULPTPLUS_PG_wm':
        return ctx.window_manager.sculpt_plus

    brush_manager: PointerProperty(type=PG_BrushManager)
    #hotbar: PointerProperty(type=PG_SculptHotbar)


# -------------------------------------------------------------------


def register():
    WM.sculpt_plus = PointerProperty(type=SCULPTPLUS_PG_wm)
