from bpy.types import PropertyGroup, Context, WindowManager as WM
from bpy.props import PointerProperty, BoolProperty

from .ui import SCULPTPLUS_PG_ui_toggles

class SCULPTPLUS_PG_wm(PropertyGroup):
    @staticmethod
    def get_data(ctx: Context) -> 'SCULPTPLUS_PG_wm':
        return ctx.window_manager.sculpt_plus

    ui: PointerProperty(type=SCULPTPLUS_PG_ui_toggles)
    
    test_context: BoolProperty()


# -------------------------------------------------------------------


def register():
    WM.sculpt_plus = PointerProperty(type=SCULPTPLUS_PG_wm)

def unregister():
    del WM.sculpt_plus
