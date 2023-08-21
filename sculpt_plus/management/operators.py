from bpy.types import Operator
from bpy.props import BoolProperty
from sculpt_plus.props import hm_data


class SCULPTPLUS_OT_toggle_hotbar_alt(Operator):
    bl_idname: str = 'sculpt_plus.toggle_hotbar_plus'
    bl_label: str = "Toggle Hotbar Alt Brush-Set"

    def execute(self, context):
        hm_data.use_alt = not hm_data.use_alt
        return {'FINISHED'}


class SCULPTPLUS_OT_set_hotbar_alt(Operator):
    bl_idname: str = 'sculpt_plus.set_hotbar_plus'
    bl_label: str = "Enable/Disable Hotbar Alt Brush-Set"

    enabled: BoolProperty()

    def execute(self, context):
        hm_data.use_alt = self.enabled
        return {'FINISHED'}
