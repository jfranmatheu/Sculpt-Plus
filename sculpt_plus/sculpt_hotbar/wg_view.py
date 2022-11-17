from math import floor
from bpy.types import Brush, Texture
from mathutils import Vector

from sculpt_plus.sculpt_hotbar.canvas import Canvas
from sculpt_plus.sculpt_hotbar.di import DiLine, DiText
from sculpt_plus.prefs import SCULPTPLUS_AddonPreferences
from sculpt_plus.utils.cursor import Cursor, CursorIcon
from sculpt_plus.utils.math import clamp
from .wg_base import WidgetBase


HEADER_HEIGHT = 32

class ViewWidget(WidgetBase):
    grid_slot_size: int = 64

    def init(self) -> None:
        self.hovered_item = None
        self.selected_item = None

        self._press_time = None
        self._press_mouse = None

        self.scroll_axis: str = 'Y'
        self.scroll: float = 0.0

        self.view_size = Vector((0, 0))
        self.view_pos = Vector((0, 0))
        self.slot_size = 0
        self.tot_scroll = 0
        self.scroll_visible_range = (0, 0)

        self.use_smooth_scroll = False

    def update(self, cv: Canvas, prefs: SCULPTPLUS_AddonPreferences):
        if prefs:
            self.use_smooth_scroll = prefs.use_smooth_scroll

    def get_data(self, cv: Canvas) -> list:
        return None

    def get_max_width(self, cv: Canvas, scale) -> float:
        return self.grid_slot_size * scale

    def iter_slots(self, scale: float, mouse: Vector = None, loop_callback: callable = None) -> Brush or Texture or None:
        self.update(self.cv, None)

        p = self.pos.copy()
        s = self.size.copy()

        margin = 6 * scale

        # GET DATA TO FILL THE SLOTS BELOW.
        data = self.get_data(self.cv)
        if not data:
            return
        #print(data)

        # CALC SLOT SIZE, NUM ROWS/COLS.
        slot_size = self.grid_slot_size * scale # floor(s.x / cols) # 64

        if self.scroll_axis == 'Y':
            s.x = self.get_max_width(self.cv, scale)

        rows = floor(s.y / slot_size)
        cols = floor(s.x / slot_size)

        tot_margin_width = ((cols - 1) * margin)
        if (slot_size * cols) + tot_margin_width > s.x:
            slot_size = int( (s.x - tot_margin_width) / cols )

        self.slot_size = slot_size + margin

        slot_s = Vector((slot_size, slot_size))
        n_row = 0
        n_col = 0
        hovered_item = None

        visible_rows = rows
        item_count = len(data)
        view_rows = floor(item_count / cols) + 1
        view_height = view_rows * self.slot_size
        #print("rows", rows, "cols", cols)
        self.view_size = Vector((s.x, view_height))
        self.view_pos = p.copy()
        self.tot_scroll = (view_rows - visible_rows) * (self.slot_size)

        # Determine the visible range.
        ## row_limit_min = -1
        ## if self.scroll != 0:
        if view_rows > visible_rows:
            rows = view_rows

            # How many rows the scroll can contain?
            row_limit_min = floor(self.scroll / self.slot_size)
            row_limit_max = row_limit_min + visible_rows + (0 if self.scroll % self.slot_size == 0 else 1)
            #print(row_limit_min, row_limit_max)
            _min = row_limit_min*cols
            _max = row_limit_max*cols
            data = data[_min:_max]

            n_row += row_limit_min

            # Apply Scroll offset (if exist).
            if self.scroll != 0:
                p.y += self.scroll

        #print("ROWS, COLS, COUNT", rows, cols, len(data))
        for item in data:
            if n_col >= cols:
                n_row += 1
                n_col = 0
            if n_row >= rows:
                break
            slot_p = Vector((
                int(p.x + (slot_size + margin) * n_col),
                # p.y + (slot_size + margin) * n_row # BOTTOM -> TOP
                int(p.y + s.y - slot_size * (n_row+1) - margin * n_row) # TOP -> BOTTOM
            ))
            #if not self.on_hover(slot_p) or not self.on_hover(slot_p+slot_s):
            #    continue

            if loop_callback:
                loop_callback(slot_p, slot_s, item)

            if mouse and hovered_item is None and WidgetBase.check_hover(None, mouse, slot_p, slot_s):
                hovered_item = item
            n_col += 1

        return hovered_item

    def get_slot_at_pos(self, m) -> Brush or Texture or None:
        return self.iter_slots(self.cv.scale, m)

    def on_hover_exit(self) -> None:
        self.hovered_item = None

    def on_hover_stay(self, m: Vector) -> None:
        self.hovered_item = self.get_slot_at_pos(m)

    def on_leftmouse_release(self, ctx, cv: Canvas, m: Vector) -> None:
        if not self.hovered_item:
            self.selected_item = None
        else:
            self.selected_item = self.hovered_item
        return False

    def on_left_click_drag(self, ctx, cv: Canvas, m: Vector) -> bool:
        return True

    def modal_enter(self, ctx, cv: Canvas, m: Vector) -> None:
        self._prev_mouse = m.copy()
        self._modal_scroll = False
        self.hovered_item = None

    def modal_exit(self, ctx, cv: Canvas, m: Vector, cancel: bool = False) -> None:
        del self._prev_mouse
        del self._modal_scroll
        Cursor.set_icon(ctx, CursorIcon.DEFAULT)

    def modal(self, ctx, evt, cv: Canvas, m: Vector) -> bool:
        if self._modal_scroll:
            if evt.type == 'LEFTMOUSE' and evt.value == 'RELEASE':
                return False
            if evt.type == 'MOUSEMOVE':
                delta_mouse_y = m.y - self._prev_mouse.y
                self.do_scroll(cv, delta_mouse_y)
                self._prev_mouse = m
            return True

        if evt.type == 'LEFTMOUSE' and evt.value == 'RELEASE':
            self.on_leftmouse_release(ctx, cv, m)
            return False

        if abs(self._prev_mouse.y - m.y) > 4 * cv.scale:
            self._modal_scroll = True
            Cursor.set_icon(ctx, CursorIcon.SCROLL_Y)

        return True

    def do_scroll(self, cv, off_y: float, anim: bool = False):
        if anim:
            target_scroll = clamp(self.scroll+off_y, 0, self.tot_scroll)

            if self.scroll == target_scroll:
                if target_scroll == self.tot_scroll or target_scroll == 0:
                    return
            #print("Target Scroll:", target_scroll)
            def _change():
                self.update(cv, None)
                #self.cv.refresh()
                #print(self.scroll)
            def _finish():
                #print("FINISH!")
                self.update(cv, None)
            self.anim(
                'scroll',
                self, 'scroll',
                target_scroll,
                0.2,
                smooth=True,
                delay=0,
                change_callback=_change,
                finish_callback=_finish
            )
        else:
            self.scroll = clamp(self.scroll+off_y, 0, self.tot_scroll) # self.view_size.y - self.slot_size)
            self.update(cv, None)

    def on_scroll_up(self, ctx, cv: Canvas):
        self.do_scroll(cv, -self.grid_slot_size*cv.scale if self.use_smooth_scroll else -10*cv.scale, anim=self.use_smooth_scroll)

    def on_scroll_down(self, ctx, cv: Canvas):
        self.do_scroll(cv, self.grid_slot_size*cv.scale if self.use_smooth_scroll else 10*cv.scale, anim=self.use_smooth_scroll)

    def draw_item(self, slot_p, slot_s, item, scale: float, prefs: SCULPTPLUS_AddonPreferences):
        pass

    def draw_poll(self, context, cv: Canvas) -> bool:
        return True

    def get_draw_item_args(self, context, cv: Canvas, scale: float, prefs: SCULPTPLUS_AddonPreferences) -> tuple:
        return ()

    def draw(self, context, cv: Canvas, _mouse: Vector, scale: float, prefs: SCULPTPLUS_AddonPreferences):
        item_args = self.get_draw_item_args(context, cv, scale, prefs)
        if not item_args:
            return
        def _draw(*args):
            self.draw_item(*args, *item_args, scale, prefs)
        self.iter_slots(scale, None, loop_callback=_draw)

        if self.scroll != 0:
            DiLine(
                self.get_pos_by_relative_point(Vector((0,1))),
                self.get_pos_by_relative_point(Vector((1,1))),
                3.0*scale,
                prefs.theme_shelf)

    def draw_post(self, _context, cv: Canvas, mouse: Vector, scale: float, _prefs: SCULPTPLUS_AddonPreferences):
        if not self.hovered_item:# self._is_on_hover
            return
        # BLENDER BUG: Needs 2 passes.
        name: str = self.hovered_item.name
        if '.' in name:
            name = name.rsplit( ".", 1 )[ 0 ]
        if '_' in name:
            name = name.replace('_', ' ')
        DiText(
            mouse,
            name,
            14,
            scale,
            (0,0,0,1.0),
            pivot=(0.2, -2.0),
            #shadow_props={'color':(0,0,0,1.0), 'blur': 0, 'offset': (1, -2)},
            draw_rect_props={'color':(.92,.92,.92,.8), 'margin': 6}
        )
        DiText(
            mouse,
            name,
            14,
            scale,
            (0.1,0.1,0.1,1.0),
            pivot=(0.2, -2.0)
        )


class VerticalViewWidget(ViewWidget):
    num_cols: int = 1
    item_aspect_ratio: float = 1 / 3 # 1 width equals 3 heights.
    interactable: bool = True

    def init(self) -> None:
        super().init()
        self.item_margin: int = 0
        self.scroll_axis = 'Y'

    def get_view_margins_vertical(self) -> tuple:
        ''' 0 -> Bottom margin;
            1 -> Top margin; '''
        return (0, 0)

    def update(self, cv: Canvas, prefs: SCULPTPLUS_AddonPreferences):
        super().update(cv, prefs)
        self.slot_width: int = int(self.size.x / self.num_cols)
        self.slot_height: int = int(self.slot_width * self.item_aspect_ratio)
        self.item_size = Vector((self.slot_width, self.slot_height)) * cv.scale

    def draw_poll(self, context, cv: Canvas) -> bool:
        return self.size.y > self.item_size.y # and self.size.x > self.item_size.x

    def draw_scissor_apply(self, _p: Vector, _s: Vector):
        p = _p.copy()
        s = _s.copy()
        vview_margins: tuple = self.get_view_margins_vertical()
        s.y -= (vview_margins[0] + vview_margins[1])
        p.y += vview_margins[0]
        super().draw_scissor_apply(p, s)

    def iter_slots(self, scale: float, mouse: Vector = None, loop_callback: callable = None):
        self.update(self.cv, None)

        p = self.pos.copy()
        s = self.size.copy()

        vview_margins: tuple = self.get_view_margins_vertical()
        s.y -= (vview_margins[0] + vview_margins[1])
        p.y += vview_margins[0]

        item_margin = self.item_margin * scale

        # GET DATA TO FILL THE SLOTS BELOW.
        data = self.get_data(self.cv)
        if not data:
            return
        #print(data)

        # CALC SLOT SIZE, NUM ROWS/COLS.
        slot_size = self.item_size

        #if self.scroll_axis == 'Y':
        #    s.x = self.get_max_width(self.cv, scale)

        rows = floor(s.y / slot_size.y)
        cols = max(floor(s.x / slot_size.x), 1)

        #tot_margin_width = ((cols - 1) * margin)
        #if (slot_size * cols) + tot_margin_width > s.x:
        #    slot_size = int( (s.x - tot_margin_width) / cols )

        #self.slot_size = slot_size # slot_size + margin

        #slot_s = Vector((slot_size, slot_size))
        n_row = 0
        n_col = 0
        hovered_item = None

        visible_rows = rows
        item_count = len(data)
        view_rows = floor(item_count / cols) - 1
        view_height = view_rows * slot_size.y
        #print("rows", rows, "cols", cols)
        self.view_size = Vector((s.x, view_height))
        self.view_pos = p.copy()
        self.tot_scroll = (view_rows - visible_rows) * (slot_size.y)

        # Determine the visible range.
        ## row_limit_min = -1
        ## if self.scroll != 0:
        if view_rows > visible_rows:
            rows = view_rows

            # How many rows the scroll can contain?
            row_limit_min = floor(self.scroll / slot_size.y)
            row_limit_max = row_limit_min + visible_rows + (0 if self.scroll % slot_size.y == 0 else 1)
            #print(row_limit_min, row_limit_max)
            _min = row_limit_min*cols
            _max = row_limit_max*cols
            data = data[max(0,_min):min(_max+1, item_count-1)]

            n_row += row_limit_min

            # Apply Scroll offset (if exist).
            if self.scroll != 0:
                p.y += self.scroll

        #print("ROWS, COLS, COUNT", rows, cols, len(data))
        for item in data:
            if n_col >= cols:
                n_row += 1
                n_col = 0
            if n_row >= rows:
                break
            slot_p = Vector((
                int(p.x), # int(p.x + (slot_size + item_margin) * n_col),
                # p.y + (slot_size + item_margin) * n_row # BOTTOM -> TOP
                int(p.y + s.y - slot_size.y * (n_row+1) - item_margin * n_row) # TOP -> BOTTOM
            ))
            #if not self.on_hover(slot_p) or not self.on_hover(slot_p+slot_s):
            #    continue

            if loop_callback:
                loop_callback(slot_p, slot_size, item)

            if mouse and hovered_item is None and self.on_hover(mouse, slot_p, slot_size):
                hovered_item = item
            n_col += 1

        return hovered_item
