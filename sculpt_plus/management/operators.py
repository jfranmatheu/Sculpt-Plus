from bpy.types import Operator
from bpy.props import BoolProperty
from sculpt_plus.globals import G
from sculpt_plus.path import SculptPlusPaths

from shutil import rmtree


class SCULPTPLUS_OT_toggle_hotbar_alt(Operator):
    bl_idname: str = 'sculpt_plus.toggle_hotbar_plus'
    bl_label: str = "Toggle Hotbar Alt Brush-Set"

    def execute(self, context):
        G.hm_data.use_alt = not G.hm_data.use_alt
        return {'FINISHED'}


class SCULPTPLUS_OT_set_hotbar_alt(Operator):
    bl_idname: str = 'sculpt_plus.set_hotbar_plus'
    bl_label: str = "Enable/Disable Hotbar Alt Brush-Set"

    enabled: BoolProperty()

    def execute(self, context):
        G.hm_data.use_alt = self.enabled
        return {'FINISHED'}



class SCULPTPLUS_OT_set_clear_data(Operator):
    bl_idname: str = 'sculpt_plust.clear_data'
    bl_label: str = "Clear Sculpt+ Data"

    def execute(self, context):
        data_path = SculptPlusPaths.APP__DATA()
        if data_path.exists() and data_path.is_dir():
            rmtree(data_path)
        
        from ..management.hotbar_manager import HotbarManager
        HotbarManager.clear_instance()
        return {'FINISHED'}
