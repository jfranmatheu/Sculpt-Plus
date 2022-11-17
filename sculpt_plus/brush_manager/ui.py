from bpy.types import Panel, Context

from sculpt_plus.props import Props


class SCULPTPLUS_PT_brush_management(Panel):
    bl_category: str = "Sculpt"
    bl_idname: str = "SCULPTPLUS_PT_brush_management"
    bl_space_type: str = "VIEW_3D"
    bl_region_type: str = "UI"
    bl_label: str = "Brush Management"

    def draw(self, context: Context):
        layout = self.layout

        manager = Props.BrushManager(context)
        active_cat = Props.ActiveBrushCat(context)

        section = layout.column(align=True)

        header = section.row(align=True)
        header.box().label(text="", icon='OUTLINER_COLLECTION')
        selector = header.row(align=True)
        selector.scale_y = 1.49
        selector.prop(manager, "cats_enum", text=str(len(manager.cats_enum)))

        layout.prop(active_cat, 'icon')

        '''
        if not active_cat:
            return

        content = section.column(align=True)
        content.template_list(
            "SCULPTPLUS_UL_brush_slot","",
            active_cat, "cats_coll",
            active_cat, "active_index"
        )
        '''
