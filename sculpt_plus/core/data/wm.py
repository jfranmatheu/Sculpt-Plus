from bpy.types import Context
from bpy.props import PointerProperty, BoolProperty

from .ui import SCULPTPLUS_PG_ui_toggles
from ...ackit import ACK


@ACK.Deco.PROP_GROUP.ROOT.WINDOW_MANAGER('sculpt_plus')
class SCULPTPLUS_PG_wm:
    @staticmethod
    def get_data(ctx: Context) -> 'SCULPTPLUS_PG_wm':
        return ctx.window_manager.sculpt_plus

    ui: PointerProperty(type=SCULPTPLUS_PG_ui_toggles)
    
    test_context: BoolProperty()
