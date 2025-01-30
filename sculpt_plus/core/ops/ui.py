from bpy.types import Operator, Region
from bpy.props import BoolProperty

from time import time

from ...utils.math import map_value
from ...core.data.cy_structs import CyBlStruct
from ...ackit import ACK


class ExpandToolbar(ACK.Type.OPS.ACTION):
    label = "[Sculpt+] Expand Toolbar"

    use_smooth: BoolProperty(default=True)

    def execute(self, context):
        if context.area is None:
            print("Bad context to expand toolbar!")
            return {'CANCELLED'}
        region: Region = None
        for reg in context.area.regions:
            if reg.type == 'TOOLS':
                region = reg
                break
        if region is None:
            return {'CANCELLED'}
        self.region = region
        self.space_data = context.space_data
        self.cy_region = CyBlStruct.UI_REGION(region)
        prefs = context.preferences
        # ui_scale = prefs.system.ui_scale
        if not self.use_smooth:
            self.set_width(320) # *ui_scale # already applied by Blender itself
            del self.cy_region
            return {'FINISHED'}
        self.width = self.cy_region.winx
        #self.velocity = 2
        self.target_width = 320 # *ui_scale # already applied by Blender itself
        # self.inc_width = 1 / ((320-self.width) * 0.01) # 10 steps to reach 320
        self.anim_time = .32
        self.start_time = time()
        #self.inc_width = 100 / (320-self.width) * self.velocity
        context.window_manager.modal_handler_add(self)
        self._timer = context.window_manager.event_timer_add(time_step=0.01, window=context.window)
        return {'RUNNING_MODAL'}

    def finish(self, context):
        if hasattr(self, '_timer') and self._timer:
            context.window_manager.event_timer_remove(self._timer)

    def modal(self, context, event):
        if event.type == 'TIMER':
            if finished := self.increment_width():
                self.finish(context)
                return {'FINISHED'}
            return {'RUNNING_MODAL'}
        return {'PASS_THROUGH'}

    def increment_width(self) -> bool:
        width = map_value(time()-self.start_time, (0, self.anim_time), (0, 1)) * self.target_width
        if width >= self.target_width:
            width = self.target_width
        self.width = width
        self.set_width(int(width))
        if width == self.target_width:
            return True
        return False

    def set_width(self, width: int):
        self.cy_region.sizex = width
        self.region.tag_redraw()
        val = self.space_data.show_region_header
        self.space_data.show_region_header = True
        self.space_data.show_region_header = False
        self.space_data.show_region_header = val
