from bpy.types import UILayout, PropertyGroup
from bpy.props import PointerProperty

from .data import AddonData
from .ops.op_toggle_prefs_ui import BRUSHMANAGER_OT_toggle_prefs_ui as OPS_TogglePrefsUI


class BrushManagerPreferences(AddonData, PropertyGroup): # (AddonPreferences):
    # bl_idname = __package__

    data : PointerProperty(type=AddonData)

    def draw(self, layout: UILayout, context):
        row = layout.row()
        row.scale_y = 2.0
        OPS_TogglePrefsUI.draw_in_layout(row, text="Open Brush Manager")
