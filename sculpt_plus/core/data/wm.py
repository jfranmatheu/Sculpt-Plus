from bpy.types import PropertyGroup, Context, WindowManager as WM
from bpy.props import PointerProperty, BoolProperty

from sculpt_plus.management.data_brush_manager import SCULPTPLUS_PG_brush_manager as PG_BrushManager


class SCULPTPLUS_PG_ui_toggles(PropertyGroup):
    show_brush_settings: BoolProperty(default=True)
    show_brush_settings_advanced: BoolProperty(default=False)
    show_brush_settings_stroke: BoolProperty(default=False)
    show_brush_settings_falloff: BoolProperty(default=False)
    show_brush_settings_texture: BoolProperty(default=False)

class SCULPTPLUS_PG_wm(PropertyGroup):
    @staticmethod
    def get_data(ctx: Context) -> 'SCULPTPLUS_PG_wm':
        return ctx.window_manager.sculpt_plus

    brush_manager: PointerProperty(type=PG_BrushManager)
    #hotbar: PointerProperty(type=PG_SculptHotbar)
    ui: PointerProperty(type=SCULPTPLUS_PG_ui_toggles)


# -------------------------------------------------------------------


def register():
    WM.sculpt_plus = PointerProperty(type=SCULPTPLUS_PG_wm)
