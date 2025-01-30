import bpy
from bpy.types import Operator, MultiresModifier
from bpy.props import IntProperty, BoolProperty

from ...utils.modifiers import get_modifier_by_type
from ...ackit import ACK


class MultiresChangeLevel(ACK.Type.OPS.ACTION):
    label = "Change Multires Level"
    tooltip = "Change Multires Level"

    level: IntProperty(default=0, name="Multires Level")

    @classmethod
    def poll(cls, context):
        return context.mode == "SCULPT" and context.sculpt_object is not None

    def action(self, context):
        mod: MultiresModifier = get_modifier_by_type(context.sculpt_object, 'MULTIRES')
        if not mod:
            return -1
        if self.level > mod.total_levels:
            return -1
        mod.sculpt_levels = self.level


class MultiresApply(ACK.Type.OPS.ACTION):
    label = "Apply Multires Modifier"
    tooltip = "Apply Multires Modifier"

    as_shape_key: BoolProperty(name="Apply as Shape Key", default=False)

    @classmethod
    def poll(cls, context):
        return context.mode == "SCULPT" and context.sculpt_object is not None

    def action(self, context):
        mod: MultiresModifier = get_modifier_by_type(context.sculpt_object, 'MULTIRES')
        if not mod:
            return -1
        bpy.ops.object.mode_set(False, mode='OBJECT', toggle=False)
        mod.levels = mod.sculpt_levels
        if self.as_shape_key:
            bpy.ops.object.modifier_apply_as_shapekey(False, keep_modifier=False, modifier=mod.name, report=True)
        else:
            bpy.ops.object.modifier_apply(modifier=mod.name, report=True)
        bpy.ops.object.mode_set(False, mode='SCULPT', toggle=False)


class MultiresRemove(Operator):
    label = "Remove Multires Modifier"
    tooltip = "Remove Multires Modifier"

    @classmethod
    def poll(cls, context):
        return context.mode == "SCULPT" and context.sculpt_object is not None

    def action(self, context):
        mod: MultiresModifier = get_modifier_by_type(context.sculpt_object, 'MULTIRES')
        if not mod:
            return -1
        bpy.ops.object.mode_set(False, mode='OBJECT', toggle=False)
        context.active_object.modifiers.remove(mod)
        bpy.ops.object.mode_set(False, mode='SCULPT', toggle=False)
