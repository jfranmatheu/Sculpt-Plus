from bpy.types import Panel, UILayout

'''
class VIEW3D_PT_sculpt_hotbar(Panel):
    #bl_parent_id = "VIEW3D_PT_tools_brush_select"
    bl_label = "Sculpt Hotbar"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Sculpt'
    #bl_options = {'DEFAULT_CLOSED', 'HEADER_LAYOUT_EXPAND'}
    bl_context = '.paint_common'

    @classmethod
    def poll(cls, context):
        return context.mode == 'SCULPT'

    def draw(self, context):
        layout = self.layout.column(align=True)

        hotbar = context.scene.sculpt_hotbar

        row = layout.row(align=True)
        row.box().label(text="", icon='ASSET_MANAGER')
        row.box().label(text="List of Brush Sets")

        row = layout.row(align=True)
        row.template_list('SCULPTHOTBAR_UL_brush_set_slots', "",
                          hotbar, "sets",
                          hotbar, "active_set_index",
                          maxrows=8, rows=3)
        col = row.column(align=True)
        col.scale_y = .95
        col.operator('sculpt_hotbar.new_set', text="", icon='ADD')
        col.operator('sculpt_hotbar.remove_set', text="", icon='REMOVE')
        col.separator()
        col.operator('sculpt_hotbar.move_set', text="", icon='TRIA_UP').direction = -1
        col.operator('sculpt_hotbar.move_set', text="", icon='TRIA_DOWN').direction = 1

        act_set = hotbar.active_set
        if not act_set:
            return

        row = layout.row(align=True)
        row.box().label(text="", icon='BRUSHES_ALL')
        row.box().label(text="[ %s ] brushes" % act_set.name)

        layout.scale_y = 1.2
        for idx, brush in enumerate(act_set.brushes):
            slot_idx = idx+1 if idx!=9 else 0
            row = layout.row(align=True)
            num = row.box()
            num.ui_units_x = 1
            num.ui_units_y = 1
            num.scale_y = 0.6
            num.label(text=str(slot_idx))
            if brush.slot:
                row.prop(brush, 'slot', text='', icon_value=UILayout.icon(brush.slot))
            else:
                row.prop(brush, 'slot', text='')
            op = row.row(align=True)
            op.ui_units_x = 1
            op.operator('sculpt_hotbar.set_brush', text='', icon='BACK').index=idx
'''