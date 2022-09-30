from bpy.types import Panel, Context

from .data import SCULPTPLUS_PG_brush_manager, SCULPTPLUS_PG_slot_set


class SCULPTPLUS_PT_brush_management(Panel):
    bl_category: str = "Sculpt"
    bl_idname: str = "SCULPTPLUS_PT_brush_management"
    bl_space_type: str = "VIEW_3D"
    bl_region_type: str = "UI"
    bl_label: str = "Brush Management"

    def draw(self, context: Context):
        layout = self.layout

        manager = SCULPTPLUS_PG_brush_manager.get_data(context)
        active_set: SCULPTPLUS_PG_slot_set = manager.active

        section = layout.column(align=True)

        header = section.row(align=True)
        header.box().label(text="", icon='OUTLINER_COLLECTION')
        selector = header.row(align=True)
        selector.scale_y = 1.49
        selector.prop(manager, "enum", text="")

        if not active_set:
            return

        content = section.column(align=True)
        content.template_list(
            "SCULPTPLUS_UL_brush_slot","",
            active_set, "slots",
            active_set, "active_index"
        )
