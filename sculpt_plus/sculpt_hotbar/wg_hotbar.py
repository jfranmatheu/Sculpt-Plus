from copy import copy, deepcopy
from math import dist
from time import time
from typing import Set, Tuple
from bpy import ops as OP
from mathutils import Vector
from sculpt_hotbar.canvas import Canvas
from sculpt_hotbar.di import DiArrowSolid, DiBr, DiCage, DiRct, DiText
from sculpt_hotbar.prefs import SculptHotbarPreferences
from sculpt_hotbar.utils.math import clamp, ease_quad_in_out, ease_quadratic_out, lerp_smooth
from sculpt_hotbar.wg_base import WidgetBase


SLOT_SIZE = 48

class Hotbar(WidgetBase):
    #modal_trigger: Set[str] = {'LEFTMOUSE'}

    def init(self) -> None:
        self.slot_pos = [Vector((0, 0))]*10
        self.slot_on_hover = None
        self.slot_size = Vector((0, 0))
        self._press_time = 0
        self._press_slot = Vector((0, 0))
        self.moving_slot = False
        self.item_size = Vector((SLOT_SIZE, SLOT_SIZE))
        self.tooltip_data_pool = []
        self.curr_tooltip_data = None
        self.curr_tooltip_opacity = 0.0
        self.prev_tooltip_opacity = 0.8
        self.prev_tooltip_data = None
        self.use_secondary = False
        self.brush_rolling = False
        self.brush_scrolling_m = Vector((0, 0))

    def update(self, cv: Canvas, prefs: SculptHotbarPreferences) -> None:
        # Size.
        isize = SLOT_SIZE*cv.scale
        self.size = s = Vector((
            isize*10,
            isize#+self.padding*2
        ))

        # Position.
        cv_width = cv.size.x
        self.pos = p = Vector((
            cv_width/2 - s.x/2,
            prefs.margin_bottom*cv.scale
        ))
        # Slot Size.
        self.slot_size = slot_size = Vector((s.x/10, s.x/10))
        # Slot Position.
        off = Vector((slot_size.x, 0))
        pad = Vector((prefs.padding*cv.scale, prefs.padding*cv.scale))
        # Vector((s.x/10, s.x/10)) - pad*2
        #isize /= 10
        isize -= (pad.x*2)
        self.item_size = Vector((isize, isize))
        for idx in range(10):
            self.slot_pos[idx] = p + off*idx + pad
        #print(self.item_size)

    def on_hover_enter(self) -> None:
        self.on_hover_stay(self.cv.mouse)

    def on_hover_stay(self, m: Vector) -> None or int:
        if self.moving_slot:
            return
        if self.brush_rolling:
            if dist(self.brush_scrolling_m, m) < 5*self.cv.scale:
                return
            self.brush_rolling = False
            self.brush_scrolling_m = Vector((0, 0))
        slot_index = self.get_slot_at_pos(m)
        if slot_index is not None and slot_index != self.slot_on_hover:
            self.slot_on_hover = slot_index
            return 1

    def on_hover_exit(self) -> None:
        self.brush_rolling = False
        if self.moving_slot:
            return
        self.slot_on_hover = None

    def on_hover_slot(self, m, p, s):
        return m.x>p.x and m.x<p.x+s.x and m.y>p.y and m.y<p.y+s.y

    def get_slot_at_pos(self, m) -> int or None:
        for idx, pos in enumerate(self.slot_pos):
            if self.on_hover_slot(m, pos, self.slot_size):
                return idx
        return None
    
    def update_active_brush(self, ctx) -> None:
        br = ctx.scene.sculpt_hotbar.get_brush(self.slot_on_hover)
        if not br:
            return
        OP.wm.tool_set_by_id(name="builtin_brush.Draw")
        ctx.tool_settings.sculpt.brush = br

    def on_leftmouse_press(self, ctx, cv: Canvas, m: Vector) -> bool:
        if self.slot_on_hover is None:
            self.moving_slot = False
            self._press_time = None
            return
        if cv.shelf.expand:
            if cv.shelf_grid.selected_item:
                ctx.scene.sculpt_hotbar.set_brush(self.slot_on_hover, cv.shelf_grid.selected_item)
                cv.shelf_grid.selected_item = None
            return
        
        self.update_active_brush(ctx)

        def _check_time(reg):
            if not self._press_time:
                return None
            if (time() - self._press_time) >= .3:
                self.moving_slot = True
                self._press_slot = self.slot_pos[self.slot_on_hover].copy()
                reg.tag_redraw()
                return None
            return 0.05
        self._press_time = time()
        self.time_fun(_check_time, 0.15, ctx.region)

    def on_left_click_drag(self, ctx, cv: Canvas, m: Vector) -> None:
        if self.slot_on_hover is None:
            return
        if not self._press_time:
            return
        if (time() - self._press_time) >= .32:
            self.moving_slot = True
            self._press_time = None
            self._press_slot = self.slot_pos[self.slot_on_hover].copy()
            self._press_off_x = m.x - self._press_slot.x
            self._press_clamp_x = (self.slot_pos[0].x, self.slot_pos[9].x)
            return True
        self._press_time = None

    def on_scroll_up(self, ctx, cv: Canvas):
        if self.slot_on_hover is None:
            return
        if not self.brush_rolling:
            self.brush_scrolling_m = cv.mouse.copy()
            self.brush_rolling = True
        self.slot_on_hover += 1
        if self.slot_on_hover >= len(self.slot_pos):
            self.slot_on_hover = 0
        self.update_active_brush(ctx)

    def on_scroll_down(self, ctx, cv: Canvas):
        if self.slot_on_hover is None:
            return
        if not self.brush_rolling:
            self.brush_scrolling_m = cv.mouse.copy()
            self.brush_rolling = True
        self.slot_on_hover -= 1
        if self.slot_on_hover < 0:
            self.slot_on_hover = len(self.slot_pos) - 1
        self.update_active_brush(ctx)

    def modal(self, ctx, evt, cv: Canvas, m: Vector) -> bool:
        if self.brush_rolling:
            self.brush_rolling = False
            return False
        if evt.type in {'ESC', 'RIGHTMOUSE'}:
            self.slot_pos[self.slot_on_hover].x = self._press_slot.x
            self.moving_slot = False
            return False
        if evt.type == 'LEFTMOUSE' and evt.value == 'RELEASE':
            active_slot_pos = self.slot_pos[self.slot_on_hover].copy()
            self.slot_pos[self.slot_on_hover] = Vector((-100, -100))
            hover_slot_pos = self.slot_pos[self.get_slot_at_pos(m)]
            self.slot_pos[self.slot_on_hover] = active_slot_pos
            active_slot_pos.x = self._press_slot.x
            self.moving_slot = False
            return False
        if evt.type == 'MOUSEMOVE':
            prev_slot = self.slot_on_hover # self.slot_pos[self.slot_on_hover].copy()
            curr_slot = self.get_slot_at_pos(m)
            if prev_slot == curr_slot or curr_slot == None:
                return True
            brushes = ctx.scene.sculpt_hotbar.active_brushes
            #print(brushes[prev_slot], brushes[curr_slot])
            brushes[prev_slot].slot, brushes[curr_slot].slot = brushes[curr_slot].slot, brushes[prev_slot].slot
            self._press_slot.x = self.slot_pos[curr_slot].x
            self.slot_on_hover = curr_slot
        #cv.refresh()
        return True

    def on_leftmouse_release(self, ctx, cv: Canvas, m: Vector) -> None:
        self.moving_slot = False
        self._press_time = None

    def modal_exit(self, ctx, cv: Canvas, m: Vector, cancel: bool = False) -> None:
        self.moving_slot = False
        self._press_time = None

    def draw(self, context, cv: Canvas, mouse: Vector, scale: float, prefs: SculptHotbarPreferences):
        p = self.pos.copy()
        s = self.size.copy()

        replace_brush = cv.shelf.expand and self.slot_on_hover is not None and cv.shelf_grid.selected_item

        sep = prefs.padding
        pad = Vector((sep,sep))
        isize = self.item_size

        hotbar = context.scene.sculpt_hotbar
        max_idx = 10 # len(hotbar.brushes)

        DiRct(p,s,prefs.theme_hotbar)
        DiCage(p, s, 3.2*scale, Vector(prefs.theme_hotbar)*.9)
        DiCage(p, s, 2.0*scale, Vector(prefs.theme_hotbar_slot)*.9)

        act_br = context.tool_settings.sculpt.brush

        if self.moving_slot:
            slots = self.slot_pos.copy()
            slots[self.slot_on_hover] = None
        else:
            slots = self.slot_pos

        for idx, slot_pos in enumerate(slots):
            if slot_pos is None:
                continue
            if idx == self.slot_on_hover:
                DiRct(slot_pos, isize,(.4,.4,.4,.25)) # (.8,.4,.1,.4)
            else:
                DiRct(slot_pos,isize,prefs.theme_hotbar_slot)
                #DiCage(slot_pos, isize, 2.0*scale, Vector(prefs.theme_hotbar_slot)*.9)
            if idx < max_idx:
                b=hotbar.get_brush(idx)
                if b:
                    if (not cv.shelf.expand and act_br == b) or (replace_brush and idx == self.slot_on_hover):
                        DiRct(slot_pos+Vector((0,isize.y)),Vector((isize.x,int(5*scale))),prefs.theme_active_slot_color)
                    DiBr(slot_pos+pad,isize-pad*2,b)

            text = str(idx+1)
            DiText(slot_pos+pad, '0' if idx==9 else text, 10, scale, prefs.theme_text)

        if self.moving_slot:
            idx = self.slot_on_hover
            b=hotbar.get_brush(idx)
            slot_pos = self._press_slot
            DiRct(slot_pos, isize,(.4,.4,.4,.25))
            DiBr(slot_pos+pad,isize-pad*2,b)
            DiCage(slot_pos, isize, 2.2*scale, (.2, .6, 1.0, 1.0))
            text = str(idx+1)
            DiText(slot_pos+pad, '0' if idx==9 else text, 10, scale, prefs.theme_text)

    def draw_over(self, ctx, cv: Canvas, mouse: Vector, scale: float, prefs: SculptHotbarPreferences):
        if self.moving_slot:
            idx = self.slot_on_hover
            t = time()
            t = abs((round(t % 1, 2) - 0.5) * 2)
            co = Vector(prefs.theme_active_slot_color)
            co.w = t
            slot_pos = self.slot_pos[idx]
            size = Vector((self.slot_size.x-1,self.slot_size.y/2))
            if idx < 9:
                DiArrowSolid(slot_pos+size, size*.2, co,False)
            if idx > 0:
                _size = Vector((0,self.slot_size.y/2))
                DiArrowSolid(slot_pos+_size, size*.2, co,True)
            return

        self.update_tooltip(ctx, cv)
        if self.prev_tooltip_data and self.prev_tooltip_opacity > 0:
            DiText(
                *self.prev_tooltip_data,
                12,
                scale,
                (.9,.9,.9,self.prev_tooltip_opacity),
                pivot=(0.5, -1),
                #shadow_props={'color':(0,0,0,1.0), 'blur': 3, 'offset': (1, 1)},
                draw_rect_props={'color':(.1,.1,.1,self.prev_tooltip_opacity), 'margin': 4}
            )
        if self.curr_tooltip_data and self.curr_tooltip_opacity > 0:
            DiText(
                *self.curr_tooltip_data,
                12,
                scale,
                (.9,.9,.9,self.curr_tooltip_opacity),
                pivot=(0.5, -1),
                #shadow_props={'color':(0,0,0,1.0), 'blur': 3, 'offset': (1, 1)},
                draw_rect_props={'color':(.1,.1,.1,self.curr_tooltip_opacity), 'margin': 4}
            )


    def update_tooltip(self, ctx, cv: Canvas) -> Tuple[str, Vector]:
        text = None
        pos = None
        alignment = (0.5, 1)
        # pivot     = (0.5, -1)

        replace_brush = cv.shelf.expand and self.slot_on_hover is not None and cv.shelf_grid.selected_item
        if replace_brush:
            hotbar = ctx.scene.sculpt_hotbar
            idx = self.slot_on_hover
            b_bar = hotbar.get_brush(idx)
            b_shelf = cv.shelf_grid.selected_item
            if not b_bar:
                slot_numkey = 0 if idx==9 else idx+1
                text = "Sets [ %s ] in Slot %i" % (b_shelf.name, slot_numkey)
            else:
                text = "Replace [ %s ] with [ %s ]" % (b_bar.name, b_shelf.name)

            pos = self.get_pos_by_relative_point(Vector(alignment))

        elif self.slot_on_hover is not None:
            hotbar = ctx.scene.sculpt_hotbar
            idx = self.slot_on_hover
            slot_pos = self.slot_pos[idx]
            b_bar = hotbar.get_brush(idx)
            if b_bar:
                text = b_bar.name
            else:
                text = "[ Empty Slot ]"
            pos = slot_pos + Vector((self.slot_size.x/2.0, self.slot_size.y))

        elif cv.group_t.get_hovered_item_data():
            text = cv.group_t.get_hovered_item_data()['label']
            pos = cv.group_t.get_pos_by_relative_point(Vector(alignment))

        elif cv.group_mask.get_hovered_item_data():
            text = cv.group_mask.get_hovered_item_data()['label']
            pos = cv.group_mask.hovered_group.get_pos_by_relative_point(Vector(alignment))

        if not text:
            if self.curr_tooltip_data:
                self.prev_tooltip_opacity = 0.8
                self.prev_tooltip_data = deepcopy(self.curr_tooltip_data)
                self.anim('tooltip__prev',
                        self, 'prev_tooltip_opacity', target_value=0.0,
                        duration=0.2, smooth=True, delay=0.0,
                        finish_callback=self.disable_tooltip)
                self.curr_tooltip_data = None
            return None

        if self.curr_tooltip_data:
            if self.curr_tooltip_data[1] == text:
                return

            self.prev_tooltip_opacity = 0.8
            self.prev_tooltip_data = deepcopy(self.curr_tooltip_data)
            self.anim('tooltip__prev',
                      self, 'prev_tooltip_opacity', target_value=0.0,
                      duration=0.15, smooth=True, delay=0.0,
                      finish_callback=self.disable_tooltip)

        self.curr_tooltip_opacity = 0.0
        self.curr_tooltip_data = pos, text
        self.anim('tooltip__curr',
                  self, 'curr_tooltip_opacity', target_value=0.8,
                  duration=0.2, smooth=True, delay=0.0)

    def disable_tooltip(self):
        #self.curr_tooltip_data = None
        self.prev_tooltip_data = None
