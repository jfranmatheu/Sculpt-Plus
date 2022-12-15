from bpy.types import UIList

'''
class SCULPTHOTBAR_UL_brush_set_slots(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        row.prop(item, "icon", text="", emboss=False)
        row.prop(item, "name", text="", emboss=False)
        if data.active_set_index == index:
            return
        _row = row.row(align=True)
        _row.alignment = 'RIGHT'
        if data.alt_set_index==index:
            _row.alert = True
            _row.label(text="[ Alt ]")
        else:
            _row.emboss = 'PULLDOWN_MENU'
            _row.operator('sculpt_hotbar.set_secondary_set', text="", icon='EVENT_ALT', depress=data.alt_set_index==index).index = index
            
        #_row.prop(item, "_remove", text="", icon='X')
        #_row.operator('sculpt_hotbar.remove_set', text="", icon='X')
'''