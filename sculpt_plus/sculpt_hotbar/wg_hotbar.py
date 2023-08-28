from copy import copy, deepcopy
from math import dist
from time import time
from typing import Set, Tuple
from bpy import ops as OP
from mathutils import Vector
from sculpt_plus.sculpt_hotbar.canvas import Canvas
from sculpt_plus.sculpt_hotbar.di import DiArrowSolid, DiBr, DiCage, DiRct, DiText, DiBMType
from sculpt_plus.prefs import SCULPTPLUS_AddonPreferences
from sculpt_plus.utils.math import clamp, ease_quad_in_out, ease_quadratic_out, lerp_smooth, map_value
from sculpt_plus.sculpt_hotbar.wg_base import WidgetBase
from sculpt_plus.props import bm_types, Props
from sculpt_plus.globals import G


SLOT_SIZE = 48

class Hotbar(WidgetBase):
    #modal_trigger: Set[str] = {'LEFTMOUSE'}

    def init(self) -> None:
        self.slot_pos = [Vector((0, 0))]*10
        self.slot_on_hover = None
        self.slot_size = Vector((0, 0))
        self._press_time = 0
        self._press_slot = Vector((0, 0))
        self._moving_slot = False
        self.item_size = Vector((SLOT_SIZE, SLOT_SIZE))
        self.tooltip_data_pool = []
        self.curr_tooltip_data = None
        self.curr_tooltip_opacity = 0.8
        self.prev_tooltip_opacity = 0.8
        self.prev_tooltip_data = None
        self.tooltip_timer = 0.0
        self.use_secondary = False
        self.brush_rolling = False
        self.brush_scrolling_m = Vector((0, 0))

    @property
    def moving_slot(self) -> bool:
        return self._moving_slot

    @moving_slot.setter
    def moving_slot(self, value: bool) -> None:
        self._moving_slot = value
        if value:
            def _update():
                if not self.moving_slot:
                    return None
                self.cv.refresh()
                return 0.1
            self.time_fun(_update)

    def update(self, cv: Canvas, prefs: SCULPTPLUS_AddonPreferences) -> None:
        # Size.
        cv_pos: Vector = cv.pos
        isize = SLOT_SIZE*cv.scale
        self.size = s = Vector((
            isize*10,
            isize#+self.padding*2
        ))

        # Position.
        cv_width = cv.size.x
        self.pos = p = Vector((
            cv_pos.x + cv_width/2 - s.x/2,
            cv_pos.y + prefs.margin_bottom*cv.scale
        ))
        # Slot Size.
        self.slot_size = slot_size = Vector((isize, isize))
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

    def get_brush_item_on_hover(self) -> bm_types.BrushItem | None:
        return self.get_brush_item_at_index(self.slot_on_hover)

    def get_brush_item_at_index(self, index: int) -> bm_types.BrushItem | None:
        if index < 0 or index > 9:
            return None
        if G.hm_data.layers.active is None:
            return None
        return G.hm_data.brushes[index]

    def update_active_brush(self, ctx) -> None:
        brush_item = self.get_brush_item_on_hover()
        if brush_item is None:
            return
        # NOTE: brush_item.type == bl_brush.sculpt_tool
        OP.wm.tool_set_by_id(name="builtin_brush." + brush_item.type.replace('_', ' ').title())
        brush_item.set_active(ctx)
        Props.SculptTool.update_stored(ctx)


    def on_leftmouse_press(self, ctx, cv: Canvas, m: Vector) -> bool:
        if cv.shelf.expand:
            ''' Assign brush from grid to hotbar. '''
            if cv.shelf_grid.selected_item is not None:
                if hm_layer := G.hm_data.layers.active:
                    hm_layer.link_brush(cv.shelf_grid.selected_item, self.slot_on_hover)
                cv.shelf_grid.selected_item = None
            return

        if self.slot_on_hover is None or self.get_brush_item_on_hover() is None:
            self.moving_slot = False
            self._press_time = None
            return

        self.update_active_brush(ctx)

        def _check_time(reg):
            if not self._press_time:
                return None
            if (time() - self._press_time) >= .3:
                self.moving_slot = True
                self._press_slot = self.slot_pos[self.slot_on_hover].copy()
                cv.refresh()
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
            #print(brushes[prev_slot], brushes[curr_slot])
            #brushes[prev_slot].slot, brushes[curr_slot].slot = brushes[curr_slot].slot, brushes[prev_slot].slot
            G.hm_data.layers.active.switch(prev_slot, curr_slot)
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

    def draw(self, context, cv: Canvas, mouse: Vector, scale: float, prefs: SCULPTPLUS_AddonPreferences):
        p = self.pos.copy()
        s = self.size.copy()

        replace_brush = cv.shelf.expand and self.slot_on_hover is not None and cv.shelf_grid.selected_item

        sep = prefs.padding
        pad = Vector((sep,sep))
        isize = self.item_size

        max_idx = 10 # len(hotbar.brushes)

        DiRct(p,s,prefs.theme_hotbar)
        DiCage(p, s, 3.2*scale, Vector(prefs.theme_hotbar)*.9)
        DiCage(p, s, 2.0*scale, Vector(prefs.theme_hotbar_slot)*.9)

        act_br = context.tool_settings.sculpt.brush
        act_br_id = act_br['uuid'] if act_br and 'uuid' in act_br else None

        if self.moving_slot:
            slots = self.slot_pos.copy()
            slots[self.slot_on_hover] = None
        else:
            slots = self.slot_pos

        for idx, slot_pos in enumerate(slots):
            if slot_pos is None:
                continue
            if idx == self.slot_on_hover:
                DiRct(slot_pos, isize,Vector(prefs.theme_hotbar_slot)+Vector((.1, .1, .1, 0))) #(.4,.4,.4,.25)) # (.8,.4,.1,.4)
            else:
                DiRct(slot_pos,isize,prefs.theme_hotbar_slot)
                #DiCage(slot_pos, isize, 2.0*scale, Vector(prefs.theme_hotbar_slot)*.9)
            if idx < max_idx:
                # b=hotbar.get_brush(idx)
                b = self.get_brush_item_at_index(idx)
                if b:
                    if (not cv.shelf.expand and act_br_id == b.uuid) or (replace_brush and idx == self.slot_on_hover):
                        DiRct(slot_pos+Vector((0,isize.y)),Vector((isize.x,int(5*scale))),prefs.theme_active_slot_color)
                    #DiBr(slot_pos+pad,isize-pad*2,b,idx==self.slot_on_hover)

                    DiBMType(
                        slot_pos+pad,
                        isize-pad*2,
                        b,
                        idx==self.slot_on_hover
                    )

            text = str(idx+1)
            DiText(slot_pos+pad, '0' if idx==9 else text, 10, scale, prefs.theme_text)

        if self.moving_slot:
            idx = self.slot_on_hover
            b = self.get_brush_item_at_index(idx)
            # b=hotbar.get_brush(idx)
            slot_pos = self._press_slot
            DiRct(slot_pos, isize,(.4,.4,.4,.25))
            # DiBr(slot_pos+pad,isize-pad*2,b)
            DiBMType(
                slot_pos+pad,
                isize-pad*2,
                b,
                True
            )
            DiCage(slot_pos, isize, 2.2*scale, (.2, .6, 1.0, 1.0))
            text = str(idx+1)
            DiText(slot_pos+pad, '0' if idx==9 else text, 10, scale, prefs.theme_text)

        if cv.active_ctx_widget:
            DiRct(self.pos, self.size, (.24, .24, .24, .64))

    def draw_over(self, ctx, cv: Canvas, mouse: Vector, scale: float, prefs: SCULPTPLUS_AddonPreferences):
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
            idx = self.slot_on_hover
            b_bar = self.get_brush_item_at_index(idx) # hotbar.get_brush(idx)
            b_shelf = cv.shelf_grid.selected_item
            if not b_bar:
                slot_numkey = 0 if idx==9 else idx+1
                text = "Sets [ %s ] in Slot %i" % (b_shelf.name, slot_numkey)
            else:
                text = "Replace [ %s ] with [ %s ]" % (b_bar.name, b_shelf.name)

            pos = self.get_pos_by_relative_point(Vector(alignment))

        elif self.slot_on_hover is not None:
            idx = self.slot_on_hover
            slot_pos = self.slot_pos[idx]
            b_bar = self.get_brush_item_at_index(idx) # hotbar.get_brush(idx)
            if b_bar:
                text = b_bar.name
            else:
                text = "[ Empty Slot ] - %i" % (0 if idx==9 else idx+1)
            pos = slot_pos + Vector((self.slot_size.x/2.0, self.slot_size.y))

        elif cv.group_t and cv.group_t.get_hovered_item_data():
            text = cv.group_t.get_hovered_item_data()['label']
            pos = cv.group_t.get_pos_by_relative_point(Vector(alignment))

        elif cv.group_mask and cv.group_mask.get_hovered_item_data():
            text = cv.group_mask.get_hovered_item_data()['label']
            pos = cv.group_mask.hovered_group.get_pos_by_relative_point(Vector(alignment))

        if not text:
            self.curr_tooltip_data = None
            self.prev_tooltip_data = None
            return None

        self.curr_tooltip_data = pos, text

        """ NEW FADE IN OUT
        if self.curr_tooltip_data is None:
            self.curr_tooltip_opacity = 0.8
            self.curr_tooltip_data = pos, text
            self.prev_tooltip_opacity = 0.0

        elif self.curr_tooltip_data[1] != text:
            ''' New tooltip. Reset states. '''
            self.prev_tooltip_data = deepcopy(self.curr_tooltip_data)
            self.prev_tooltip_opacity = 0.8

            self.curr_tooltip_opacity = 0.0
            self.curr_tooltip_data = pos, text

            self.tooltip_timer = time()

        elif self.prev_tooltip_opacity != 0:
            ''' Anim opacity. '''
            passed_time = time() - self.tooltip_timer
            if passed_time > 0.2:
                self.curr_tooltip_opacity = 0.8
                self.prev_tooltip_opacity = 0.0
                self.prev_tooltip_data = None
                return

            self.curr_tooltip_opacity = map_value(passed_time, (0.0, 0.2), (0.0, 0.8))
            self.prev_tooltip_opacity = map_value(passed_time, (0.0, 0.2), (0.8, 0.0))
        """

        ''' OLD FADE-IN-OUT
        if not text and not self.brush_rolling:
            if self.curr_tooltip_data:
                self.prev_tooltip_opacity = 0.8
                self.prev_tooltip_data = deepcopy(self.curr_tooltip_data)
                self.anim('tooltip__prev',
                        self, 'prev_tooltip_opacity', target_value=0.0,
                        duration=0.2, smooth=True, delay=0.0,
                        finish_callback=self.disable_tooltip)
                self.curr_tooltip_data = None
            return None

        if self.curr_tooltip_data and not self.brush_rolling:
            if self.curr_tooltip_data[1] == text:
                return

            self.prev_tooltip_opacity = 0.8
            self.prev_tooltip_data = deepcopy(self.curr_tooltip_data)
            self.anim('tooltip__prev',
                      self, 'prev_tooltip_opacity', target_value=0.0,
                      duration=0.15, smooth=True, delay=0.0,
                      finish_callback=self.disable_tooltip)
        '''


        ''' OLD FADE-IN-OUT
        self.curr_tooltip_data = pos, text

        if self.brush_rolling:
            self.prev_tooltip_data = None
            self.prev_tooltip_opacity = 0.0
            self.curr_tooltip_opacity = 0.8
        else:
            self.curr_tooltip_opacity = 0.0
            self.anim('tooltip__curr',
                    self, 'curr_tooltip_opacity', target_value=0.8,
                    duration=0.2, smooth=True, delay=0.0)
        '''


    def disable_tooltip(self):
        #self.curr_tooltip_data = None
        self.prev_tooltip_data = None
