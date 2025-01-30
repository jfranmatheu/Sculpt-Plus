import bpy
from bpy.types import Operator, MultiresModifier
from bpy.props import IntProperty, BoolProperty

from ...utils.modifiers import get_modifier_by_type


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


class SCULPTPLUS_OT_multires_apply(Operator):
    bl_idname = "sculpt_plus.multires_apply"
    bl_label = "Apply Multires Modifier"
    bl_description = "Apply Multires Modifier"

    as_shape_key: BoolProperty(name="Apply as Shape Key", default=False)

    @classmethod
    def poll(cls, context):
        return context.mode == "SCULPT" and context.sculpt_object is not None

    def execute(self, context):
        mod: MultiresModifier = get_modifier_by_type(context.sculpt_object, 'MULTIRES')
        if not mod:
            return {'CANCELLED'}
        bpy.ops.object.mode_set(False, mode='OBJECT', toggle=False)
        mod.levels = mod.sculpt_levels
        if self.as_shape_key:
            bpy.ops.object.modifier_apply_as_shapekey(False, keep_modifier=False, modifier=mod.name, report=True)
        else:
            bpy.ops.object.modifier_apply(modifier=mod.name, report=True)
        bpy.ops.object.mode_set(False, mode='SCULPT', toggle=False)
        return {'FINISHED'}


class SCULPTPLUS_OT_multires_remove(Operator):
    bl_idname = "sculpt_plus.multires_remove"
    bl_label = "Remove Multires Modifier"
    bl_description = "Remove Multires Modifier"

    @classmethod
    def poll(cls, context):
        return context.mode == "SCULPT" and context.sculpt_object is not None

    def execute(self, context):
        mod: MultiresModifier = get_modifier_by_type(context.sculpt_object, 'MULTIRES')
        if not mod:
            return {'CANCELLED'}
        bpy.ops.object.mode_set(False, mode='OBJECT', toggle=False)
        context.active_object.modifiers.remove(mod)
        bpy.ops.object.mode_set(False, mode='SCULPT', toggle=False)
        return {'FINISHED'}
