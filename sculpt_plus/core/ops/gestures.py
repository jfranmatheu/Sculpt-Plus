from gpu_extras.presets import draw_circle_2d
from bpy.types import Operator
from mathutils import Vector
from math import dist
from gpu import state

from ...gpu.di import DiText
from ...utils.math import clamp, map_value
from ...ackit import ACK


class GestureSizeStrength(ACK.Type.OPS.ACTION):
    label: str = "Gesture Size Strength"

    @classmethod
    def poll(cls, context):
        return context.object and context.mode == 'SCULPT' and context.tool_settings.sculpt.brush is not None

    def invoke(self, context, event):
        self.scale = scale = context.preferences.system.ui_scale
        self.start_mouse = Vector((event.mouse_region_x, event.mouse_region_y))
        self.current_mouse = self.start_mouse.copy()
        self.prev_mouse = self.start_mouse.copy()
        context.window_manager.modal_handler_add(self)
        self._draw_handler = context.space_data.draw_handler_add(self.draw_px, (context, self.start_mouse, self.current_mouse, scale), 'WINDOW', 'POST_PIXEL')
        self.started = False
        self.start_event = event.type
        self.safe_radius = 10*scale
        self.direction = 'NONE'
        self.old_value = 0
        self.mouse_delta_resto_for_next_iter = 0
        self.max_radius = 250*scale
        self.data = None
        self.data_prop = ''
        self.data_range = (0, 1)
        context.tool_settings.sculpt.show_brush = False
        context.region.tag_redraw()
        return {'RUNNING_MODAL'}

    def modal_exit(self, context):
        context.region.tag_redraw()
        context.space_data.draw_handler_remove(self._draw_handler, 'WINDOW')
        context.tool_settings.sculpt.show_brush = True

    def modal(self, context, event):
        if event.type in {'ESC'}:
            if self.started:
                setattr(self.data, self.data_prop, self.old_value)
            self.modal_exit(context)
            return {'CANCELLED'}
        if event.type == self.start_event and event.value == 'RELEASE':
            if self.started:
                pass
            self.modal_exit(context)
            return {'FINISHED'}
        self.current_mouse.x = event.mouse_region_x
        self.current_mouse.y = event.mouse_region_y

        if self.started:
            context.region.tag_redraw()
            #d = dist(self.start_mouse, self.current_mouse)
            #if d > self.max_radius or d == 0:
            #    return {'RUNNING_MODAL'}
            mouse_delta = self.current_mouse - self.prev_mouse
            if self.direction == 'HORIZONTAL':
                off = mouse_delta.x * 0.002 # 200px to increase strength to its soft max (1.0).
                value = clamp(getattr(self.data, self.data_prop) + off, *self.data_range)
            else:
                _off = mouse_delta.y + self.mouse_delta_resto_for_next_iter
                off = int(_off) # * 0.1 # 500px to increase size to its soft max (500).
                self.mouse_delta_resto_for_next_iter = _off-off
                value = clamp(getattr(self.data, self.data_prop) + off, *self.data_range)
            setattr(self.data, self.data_prop, value)
        else:
            if dist(self.start_mouse, self.current_mouse) > self.safe_radius:
                context.region.tag_redraw()
                brush = context.tool_settings.sculpt.brush
                ups = context.tool_settings.unified_paint_settings
                self.started = True
                # check direction...
                rel_pos = self.current_mouse - self.start_mouse
                x, y = abs(rel_pos.x), abs(rel_pos.y)
                if x > y:
                    self.direction = 'HORIZONTAL'
                    if ups.use_unified_strength:
                        self.old_value = ups.strength
                        self.data = ups
                    else:
                        self.old_value = brush.strength
                        self.data = brush
                    self.data_prop = 'strength'
                    self.data_range = (0.0, 2.0)
                    self.max_radius = 300
                else:
                    self.direction = 'VERTICAL'
                    if ups.use_unified_size:
                        self.old_value = ups.size
                        self.data = ups
                    else:
                        self.old_value = brush.size
                        self.data = brush
                    self.data_range: tuple[int, int] = (1, 500)
                    self.data_prop = 'size'
                    self.max_radius = 500
                    
                self.start_mouse = self.current_mouse.copy()

        self.prev_mouse = self.current_mouse.copy()
        return {'RUNNING_MODAL'}


    def draw_px(self, context, origin: Vector, current_mouse: Vector, scale: float):
        origin = self.start_mouse
        # current_mouse = self.current_mouse
        state.blend_set('ALPHA')
        state.line_width_set(1.8*scale)
        if self.started:
            value = getattr(self.data, self.data_prop)
            value_rad = map_value(value, self.data_range, (0, self.max_radius))
            
            # mouse_rad = dist(origin, current_mouse)
            if self.direction == 'HORIZONTAL':
                label = 'Strength'
                color = (1.0, 1.0, 0.0, 1.0)
                value = round(value, 2)
            else:
                label = 'Size'
                color = (0.0, 1.0, 1.0, 1.0)
            # draw_circle_2d(origin, (0.1, 0.1, 0.1, 0.4), mouse_rad, segments=int(64*scale))
            # draw_circle_2d(origin, (.8, .8, .8, 1.0), self.max_radius, segments=int(64*scale))
            # draw_circle_2d(origin, (.6, .6, .6, 1.0), self.max_radius*0.5, segments=int(32*scale))

            draw_circle_2d(origin, color, value_rad, segments=int(64*scale))
            # +Vector((0, -self.safe_radius*2))
            DiText(origin+Vector((0, self.safe_radius*2)), label, 16, scale, pivot=(0.5, 0), draw_rect_props={}, shadow_props={})
            DiText(origin, str(value), 14, scale, pivot=(0.5, .5), draw_rect_props={}, shadow_props={})
        else:
            DiText(origin+Vector((0, self.safe_radius*2)), 'Size +', 14, scale, pivot=(0.5, 0), draw_rect_props={}, shadow_props={})
            DiText(origin+Vector((self.safe_radius*2, 0)), 'Strength +', 14, scale, pivot=(0, 0.5), draw_rect_props={}, shadow_props={})
            DiText(origin+Vector((0, -self.safe_radius*2)), 'Size -', 14, scale, pivot=(0.5, 1), draw_rect_props={}, shadow_props={})
            DiText(origin+Vector((-self.safe_radius*2, 0)), 'Strength -', 14, scale, pivot=(1, 0.5), draw_rect_props={}, shadow_props={})
            draw_circle_2d(origin, (1.0, 0.0, 0.0, 1.0), self.safe_radius, segments=int(24*scale))
        state.blend_set('NONE')
