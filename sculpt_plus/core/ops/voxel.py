from bpy.types import Operator
from bpy.props import FloatProperty, BoolProperty


class SCULPTPLUS_OT_remesh_voxel_increase_size(Operator):
    bl_idname = "sculpt_plus.remesh_voxel_increase_size"
    bl_label = "De/Increase Voxel Size"
    bl_description = "Decrease/Increase Remesh Voxel Size by a given value"

    value: FloatProperty(default=0, name="Value")

    @classmethod
    def poll(cls, context):
        return context.mode == "SCULPT" and context.sculpt_object is not None

    def execute(self, context):
        context.sculpt_object.data.remesh_voxel_size += self.value
        return {'FINISHED'}

class SCULPTPLUS_OT_remesh_voxel_increase_density(Operator):
    bl_idname = "sculpt_plus.remesh_voxel_increase_density"
    bl_label = "De/Increase Voxel Size by density"
    bl_description = "Decrease/Increase Remesh Voxel Size by density porcentage change"

    value: FloatProperty(default=0, name="Percentage Value")

    @classmethod
    def poll(cls, context):
        return context.mode == "SCULPT" and context.sculpt_object is not None

    def execute(self, context):
        context.sculpt_object.data.remesh_voxel_size -= (context.sculpt_object.data.remesh_voxel_size * self.value / 100)
        return {'FINISHED'}
