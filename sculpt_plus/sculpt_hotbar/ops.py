from bpy.types import Operator
from bpy.props import IntProperty



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
        # Props.SetHotbarSelected(context, self.index)
        print(">>>", self.index, context.tool_settings.sculpt.brush)
        return {'FINISHED'}
