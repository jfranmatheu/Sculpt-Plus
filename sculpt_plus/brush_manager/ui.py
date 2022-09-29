from bpy.types import Panel, Context


class SCULPTPLUS_PT_brush_management(Panel):
    #bl_category: str = "Sculpt"
    bl_idname: str = "SCULPTPLUS_PT_brush_management"
    bl_space_type: str = "VIEW_3D"
    bl_region_type: str = "WINDOW"
    bl_label: str = "Brush Management"

    def draw(self, context: Context):
        layout = self.layout
