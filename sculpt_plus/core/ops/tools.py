from bpy.types import Operator
from bpy.props import StringProperty
from bpy import ops as OPS


class SCULPTPLUS_OT_select_tool__face_set_edit(Operator):
    bl_idname = 'sculpt_plus.select_tool__face_set_edit'
    bl_label = "Select 'Face Set Edit' tool"

    mode : StringProperty()

    @classmethod
    def poll(cls, context):
        return context.mode == 'SCULPT'

    def execute(self, context):
        OPS.wm.tool_set_by_id(name='builtin.face_set_edit')
        tool = context.workspace.tools.from_space_view3d_mode("SCULPT", create=False)
        if tool:
            tool.operator_properties("sculpt.face_set_edit").mode = self.mode
        return {'FINISHED'}
