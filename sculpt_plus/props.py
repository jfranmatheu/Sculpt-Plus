from typing import Union

from bpy.types import Context

#from sculpt_plus.core.data.scn import SCULPTPLUS_PG_scn
#from sculpt_plus.core.data.wm import SCULPTPLUS_PG_wm
#from sculpt_plus.brush_manager.data_brush_manager import SCULPTPLUS_PG_brush_manager
#from sculpt_plus.brush_manager.data_brush_category import SCULPTPLUS_PG_brush_category
#from sculpt_plus.brush_manager.data_brush_slot import SCULPTPLUS_PG_brush_slot


''' Helper to get properties paths (with typing). '''
class Props:
    @staticmethod
    def Scene(context: Context):# -> SCULPTPLUS_PG_scn:
        return context.scene.sculpt_plus

    @staticmethod
    def Temporal(context: Context):# -> SCULPTPLUS_PG_wm:
        return context.window_manager.sculpt_plus
        
    @classmethod
    def UI(cls, context: Context):# -> SCULPTPLUS_PG_wm:
        return cls.Temporal(context).ui

    @classmethod
    def BrushManager(cls, context: Context):# -> SCULPTPLUS_PG_brush_manager:
        return cls.Temporal(context).brush_manager

    @classmethod
    def GetBrushCat(cls, context: Context, cat_idname: Union[str, int]):# -> SCULPTPLUS_PG_brush_category:
        return cls.BrushManager(context).get_cat(cat_idname)

    @classmethod
    def ActiveBrushCat(cls, context: Context):# -> SCULPTPLUS_PG_brush_category:
        return cls.BrushManager(context).active

    #@classmethod

