from bpy.types import Operator
from bpy.props import FloatProperty, BoolProperty

from ...ackit import ACK


class IncreaseRemeshVoxelSize(ACK.Type.OPS.ACTION):
    label = "De/Increase Voxel Size"
    tooltip = "Decrease/Increase Remesh Voxel Size by a given value"

    value: FloatProperty(default=0, name="Value")

    @classmethod
    def poll(cls, context):
        return context.mode == "SCULPT" and context.sculpt_object is not None

    def action(self, context):
        context.sculpt_object.data.remesh_voxel_size += self.value

class IncreaseRemeshVoxelDensity(ACK.Type.OPS.ACTION):
    label = "De/Increase Voxel Size by density"
    tooltip = "Decrease/Increase Remesh Voxel Size by density porcentage change"

    value: FloatProperty(default=0, name="Percentage Value")

    @classmethod
    def poll(cls, context):
        return context.mode == "SCULPT" and context.sculpt_object is not None

    def action(self, context):
        context.sculpt_object.data.remesh_voxel_size -= (context.sculpt_object.data.remesh_voxel_size * self.value / 100)
