from bpy.types import Operator, MultiresModifier
from bpy.props import IntProperty

from sculpt_plus.utils.modifiers import get_modifier_by_type


class SCULPTPLUS_OT_multires_change_level(Operator):
    bl_idname = "sculpt_plus.multires_change_level"
    bl_label = "Change Multires Level"
    bl_description = "Change Multires Level"

    level: IntProperty(default=0, name="Multires Level")

    @classmethod
    def poll(cls, context):
        return context.mode == "SCULPT" and context.sculpt_object is not None

    def execute(self, context):
        mod: MultiresModifier = get_modifier_by_type(context.sculpt_object, 'MULTIRES')
        if not mod:
            return {'CANCELLED'}
        if self.level > mod.total_levels:
            return {'CANCELLED'}
        mod.sculpt_levels = self.level
        return {'FINISHED'}
