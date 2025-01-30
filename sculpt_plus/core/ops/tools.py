from bpy.types import Operator
from bpy.props import StringProperty
from bpy import ops as OPS

from ...ackit import ACK


class SelectTool_FaceSetEdit(ACK.Type.OPS.ACTION):
    label = "Select 'Face Set Edit' tool"

    mode : StringProperty()

    @classmethod
    def poll(cls, context):
        return context.mode == 'SCULPT'

    def action(self, context):
        OPS.wm.tool_set_by_id(name='builtin.face_set_edit')
        if tool := context.workspace.tools.from_space_view3d_mode("SCULPT", create=False):
            tool.operator_properties("sculpt.face_set_edit").mode = self.mode
