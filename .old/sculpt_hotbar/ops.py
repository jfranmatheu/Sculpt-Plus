from bpy.types import Operator
from bpy.props import IntProperty

from sculpt_plus.globals import G



class SCULPTHOTBAR_OT_set_brush(Operator):
    bl_idname = 'sculpt_hotbar.set_brush'
    bl_label = "Set Active Brush"
    bl_description = "Sets the current active brush into this hotbar slot"

    index : IntProperty(default=-1)

    @classmethod
    def poll(cls, context):
        return context.mode == 'SCULPT' and context.tool_settings.sculpt.brush

    def execute(self, context):
        if self.index == -1:
            return {'CANCELLED'}
        G.hm_data.select_brush(context, self.index)
        return {'FINISHED'}
