from bpy.types import UIList


class SCULPTPLUS_UL_brush_slot(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        slot = item
        br = slot.brush
        layout.prop(slot, 'brush', text="")
