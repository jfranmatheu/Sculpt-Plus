from math import floor
from time import time
from typing import Set

import bpy
from bpy.types import Brush
from mathutils import Vector
from sculpt_hotbar.canvas import Canvas
from sculpt_hotbar.prefs import SculptHotbarPreferences
from sculpt_hotbar.utils.cursor import Cursor, CursorIcon

from sculpt_hotbar.utils.math import clamp, point_inside_circle
from sculpt_hotbar.di import DiIma, DiImaco, DiLine, DiText, DiRct, DiCage, DiBr, get_rect_from_text, get_text_dim
from sculpt_hotbar.wg_view import ViewWidget
from .wg_base import WidgetBase
from sculpt_hotbar.icons import Icon


SLOT_SIZE = 56
HEADER_HEIGHT = 32

class Shelf(WidgetBase):

    interactable: bool = False

    def init(self) -> None:
        self.max_height = 600
        self._expand: bool = False
        self.margin: int = 6

    @property
    def expand(self):
        return self._expand

    @expand.setter
    def expand(self, state: bool):
        self.cv.shelf_drag.interactable = False

        def _update():
            self.cv.refresh()
            self.cv.shelf_drag.update(self.cv, None)
            self.cv.shelf_search.update(self.cv, None)

        if state == False:
            self.cv.shelf_grid.selected_item = None

            def _disable():
                self._expand = False
                self.cv.shelf_drag.interactable = True

            self.resize(y=0, animate=True, anim_change_callback=_update, anim_finish_callback=_disable)

        else:
            self._expand = True

            def _enable():
                self._expand = True
                self.cv.shelf_drag.interactable = True

            r: float = self.size.y * .2
            slot_size = SLOT_SIZE * self.cv.scale
            height = slot_size * 5.25 # int(self.cv.size.y * .65) # self.cv.size.y - self.cv.shelf.pos.y - self.cv.hotbar.size.y - r
            self.resize(y=height, animate=True, anim_change_callback=_update, anim_finish_callback=_enable)

    def update(self, cv: Canvas, prefs: SculptHotbarPreferences):
        self.margin = 6 * cv.scale

        # Calc final shelf transform.
        self.size.x = cv.hotbar.size.x
        self.pos.x = cv.hotbar.pos.x
        # limit height: self.cv.size.y - self.cv.shelf.pos.y - self.cv.hotbar.size.y - r
        self.max_height = int(self.cv.size.y * .65)

        r: float = cv.hotbar.size.y * .2
        p = cv.hotbar.get_pos_by_relative_point(Vector((0.0, 1.0)))
        self.pos = p
        self.pos.y += r
        self.size = Vector((cv.hotbar.size.x, 0))
        #height = context.region.height - p.y - wg.size.y
        #wg.shelf_size.y = height
        if self.expand:
            self._expand = False
            self.expand = True

    def on_leftmouse_press(self, ctx, cv: Canvas, m: Vector) -> None:
        pass

    def on_hover_stay(self, m: Vector) -> None:
        if self.cv.shelf_grid.on_hover(m):
            self.cv.shelf_grid.on_hover_stay(m)

    def on_hover_exit(self) -> None:
        self.cv.shelf_grid.on_hover_exit()

    def draw(self, context, cv: Canvas, mouse: Vector, scale: float, prefs: SculptHotbarPreferences):
        if self.expand:
            DiRct(self.pos, self.size, prefs.theme_shelf)
            DiCage(self.pos, self.size, 3.2*scale, Vector(prefs.theme_shelf)*.9)


class ShelfGrid(ViewWidget):
    use_scissor: bool = True
    grid_slot_size: int = 56

    def get_max_width(self, cv: Canvas, scale) -> float:
        return self.size.x
        padding = 6 * scale
        return SLOT_SIZE * scale * 5.25 - padding * 2

    def update(self, cv: Canvas, prefs: SculptHotbarPreferences):
        scale = cv.scale

        p = self.cv.shelf.pos.copy()
        s = self.cv.shelf.size.copy()

        padding = 6 * scale
        margin = 6 * scale

        # add margin from search.
        # self.cv.shelf_search.size.y
        shelf_search_height = HEADER_HEIGHT * scale
        s.y -= (shelf_search_height + margin * 2)

        p += Vector((padding, padding))
        s -= (Vector((padding, padding)) * 2.0)

        self.pos = p.copy()
        self.size = s

    def get_data(self, cv: Canvas) -> list:
        # Apply filter (if exist).
        filt = cv.shelf_search.search
        if filt:
            filt = filt.lower()
            br_startswith = {br for br in bpy.data.brushes if br.use_paint_sculpt and br.name.lower().startswith(filt)}
            br_contains = [br for br in bpy.data.brushes if br not in br_startswith and br.use_paint_sculpt and filt in br.name.lower()]
            brushes = list(br_startswith) + br_contains
        else:
            brushes = [br for br in bpy.data.brushes if br.use_paint_sculpt]
        return brushes

    def on_numkey(self, ctx, number: int, cv: Canvas, m: Vector) -> None:
        if not self.selected_item:
            return
        #if not cv.shelf.expand:
        #    return
        list_index = 9 if number==0 else number-1
        ctx.scene.sculpt_hotbar.set_brush(list_index, self.selected_item)
        self.selected_item = None

    def draw_poll(self, context, cv: Canvas) -> bool:
        return cv.shelf.expand and cv.shelf.size.y > self.slot_size

    def get_draw_item_args(self, context, cv: Canvas, scale: float, prefs: SculptHotbarPreferences) -> tuple:
        brushes = context.scene.sculpt_hotbar.get_brushes()
        slot_color = Vector(prefs.theme_shelf_slot)
        if not brushes:
            return None, slot_color
        brush_idx_rel: dict = {brush: idx for idx, brush in enumerate(brushes)}
        return brush_idx_rel, slot_color

    def draw_item(self, slot_p, slot_s, brush, brush_idx_rel, slot_color, scale: float, prefs: SculptHotbarPreferences):
        #if brush is None or brush_idx_rel is None:
        #    return
        DiRct(slot_p, slot_s, slot_color)
        DiBr(slot_p, slot_s, brush)
        if brush_idx_rel is not None and brush in brush_idx_rel:
            idx: int = brush_idx_rel[brush]
            idx = idx+1 if idx!=9 else 0
            DiText(slot_p+Vector((1,3)), str(idx), 12, scale)
        if brush == self.selected_item:
            DiCage(slot_p, slot_s, 2.4*scale, prefs.theme_active_slot_color) #(.2, .6, 1.0, 1.0))
        else:
            DiCage(slot_p, slot_s, 2.4*scale, slot_color*1.3)

        if self.hovered_item == brush:
            DiRct(slot_p, slot_s, (.6,.6,.6,.25))


class ShelfDragHandle(WidgetBase):
    modal_trigger: Set[str] = {'LEFTMOUSE'}
    msg_on_enter: str = "Click, or Press & Drag up/down to expand or hide"

    def init(self) -> None:
        self.start_mouse = Vector((0, 0))
        self.end_mouse   = Vector((0, 0))
        self.tx_pos = Vector((0, 0))
        self.dragging = False

    def update(self, cv: Canvas, prefs: SculptHotbarPreferences) -> None:
        r: float = cv.hotbar.size.y * .2
        c: Vector = cv.shelf.get_pos_by_relative_point(Vector((0.5, 1.0)))
        c.y += (r*1.5)
        self.pos = c
        self.size = Vector((r*1.5, r*1.5))
        #self.pos, self.size = get_rect_from_text(self.tx_pos, ": : :", 16, cv.scale, (.5, 0), 8)

    def on_hover(self, m: Vector) -> bool:
        return point_inside_circle(m, self.pos, self.size.x)

    def start_drag(self, cv: Canvas, m: Vector):
        self.dragging = True
        self.start_mouse = m.copy()
        # Reset Size and end mouse to avoid weird artifact first frame of event.
        self.end_mouse = m.copy()
        if not cv.shelf.expand:
            cv.shelf.size = Vector((cv.hotbar.size.x, 0))

    def on_drag(self, cv: Canvas, m: Vector):
        self.end_mouse = m.copy()

        # Update shelf transform.
        r: float = cv.hotbar.size.y * .2
        p = cv.hotbar.get_pos_by_relative_point(Vector((0.0, 1.0)))
        p.y += r # * 2.0)
        if cv.shelf.expand:
            if self.end_mouse.y > self.start_mouse.y or self.end_mouse.y < p.y:
                return
            height = max(0, self.end_mouse.y - p.y - r)
        else:
            if self.end_mouse.y < self.start_mouse.y or self.end_mouse.y < p.y:
                return
            height = min(max(self.end_mouse.y - self.start_mouse.y, 0), 25*cv.scale)
        cv.shelf.pos = p.copy()
        cv.shelf.size = Vector((cv.hotbar.size.x, height))
        self.update(cv, None)
        cv.shelf_search.update(cv, None)

    def end_drag(self, cv: Canvas):
        self.dragging = False
        self._is_on_hover = False

        scale = cv.scale
        off_y = abs(self.end_mouse.y - self.start_mouse.y)
        threshold = (20 * scale)
        if (off_y > threshold or off_y == 0) and not cv.shelf.expand:
            cv.shelf.expand = True
        elif (off_y > threshold or off_y == 0) and cv.shelf.expand:
            cv.shelf.expand = False

    def modal_enter(self, ctx, cv: Canvas, m: Vector) -> None:
        self.start_drag(cv, m)

    def on_mousemove(self, ctx, cv: Canvas, m: Vector) -> None:
        self.on_drag(cv, m)
        if cv.shelf.expand:
            ctx.area.header_text_set("Drag it down, then release to hide")
        else:
            ctx.area.header_text_set("Drag it up, then release to expand")

    def modal_exit(self, ctx, cv: Canvas, m: Vector, cancel: bool = False) -> None:
        self.end_drag(cv)

    def draw(self, context, cv: Canvas, mouse: Vector, scale: float, prefs: SculptHotbarPreferences):
        color = prefs.theme_text if self._is_on_hover else Vector(prefs.theme_text) * .75
        bg_color = (.1, .1, .1, .7) if self._is_on_hover else (.1, .1, .1, .35)

        off_y = abs(self.end_mouse.y - self.start_mouse.y)
        threshold = (20 * scale)
        drag_enough = self.dragging and off_y > threshold
        handle_text = ": : :" if not self.dragging else " ○ " if drag_enough else " v " if cv.shelf.expand else " ^ "
        DiText(self.pos, handle_text, SLOT_SIZE/4, scale, color, pivot=(.5, 0), draw_rect_props={'margin': 8, 'color': bg_color}, id=0)

        if not cv.shelf.expand and drag_enough:
            DiText(self.pos - Vector((0, threshold)),
                   "Release to show Brush-Shelf",
                   12,
                   scale,
                   (.92, .92, .92, 0.7),
                   pivot=(.5, 1),
                   draw_rect_props={'margin': 8, 'color': (.1, .1, .1, .3)})


class ShelfSearch(WidgetBase):
    use_scissor: bool = True
    cursor: CursorIcon = CursorIcon.TEXT

    def init(self) -> None:
        self.search = u''
        self.type_index = 0
        self.modal_cancel = False
        
    def on_hover(self, m: Vector, p: Vector = None, s: Vector = None) -> bool:
        return super().on_hover(m, p, s) and self.cv.shelf.expand

    def update(self, cv: Canvas, prefs: SculptHotbarPreferences) -> None:
        height = HEADER_HEIGHT * cv.scale
        margin = 6 * cv.scale # cv.shelf.margin

        self.pos = cv.shelf.get_pos_by_relative_point(Vector((0, 1)))
        self.pos.x += margin
        self.pos.y -= height + margin
        self.size.y = height
        if self.in_modal:
            self.size.x = cv.shelf_grid.size.x # cv.shelf.size.x * .5 - margin * 2
        else:
            self.size.x = height

    def draw(self, context, cv: Canvas, mouse: Vector, scale: float, prefs: SculptHotbarPreferences):
        if not cv.shelf.expand or cv.shelf.size.y < 60:
            return
        p = self.pos.copy()
        s = self.size.copy()
        if self.in_modal or self.anim_pool:
            color = (.08, .08, .08, .9)
            DiRct(p, s, color)
            DiCage(p, s, 2.2*scale, (.2, .5, .9, .8)) # Vector(color)*.8
            tpos = p+Vector((10, s.y*.32))
            t = time()
            t = round(t % 1, 2)
            f2 = min(3, int(t / 0.25))
            f1 = t < .5
            text = 'Start Typing ' + ''.join(['.']*f2) + ('|' if f1 else '')
            DiText(tpos, self.search if self.search else text, 16, scale)
            if self.search:# and f1:
                tdim = get_text_dim(self.search[:self.type_index], 16, scale)
                tpos += Vector((tdim[0], -4*scale))
                DiLine(tpos, tpos+Vector((0, 20*scale)), 1.6*scale, (.1, .1, .1, .7))
                DiLine(tpos, tpos+Vector((0, 20*scale)), 1.3*scale, (.7, .7, .7, .7))
        else:
            if self._is_on_hover:
                color = (.2, .2, .2, .8)
                DiRct(p, s, color)
                DiCage(p, s, 2.2*scale, Vector(color)*.8)
                DiImaco(p, s, Icon.SEARCH(), (.9, .9, .9, .9))
            else:
                DiImaco(p, s, Icon.SEARCH(), (.9, .9, .9, .6))

    def on_left_click(self, ctx, cv: Canvas, m: Vector) -> bool:
        return True

    def modal_enter(self, ctx, cv: Canvas, m: Vector) -> None:
        def _finish_anim():
            self.update(cv, None)
        self.resize(x=cv.shelf_grid.size.x, animate=True, anim_finish_callback=_finish_anim)

    def modal_exit(self, ctx, cv: Canvas, m: Vector, cancel: bool = False) -> None:
        def _finish_anim():
            self.update(cv, None)
        self.resize(x=self.size.y, animate=True, anim_finish_callback=_finish_anim)

        if self.modal_cancel:
            self.modal_cancel = False
            self.search = ''
            return
        #cv.shelf_grid.filter = self.search

    def modal(self, ctx, evt, cv: Canvas, m: Vector) -> bool:
        if evt.type in {'ESC', 'RET', 'RIGHTMOUSE'}:
            self.modal_cancel = True
            if evt.type != 'RET':
                self.search = ''
            return False
        if evt.value != 'PRESS':
            return True
        if evt.type == 'LEFT_ARROW':
            self.type_index = clamp(self.type_index-1, 0, len(self.search))
            return True
        if evt.type == 'RIGHT_ARROW':
            self.type_index = clamp(self.type_index+1, 0, len(self.search))
            return True

        if evt.type == 'DEL':
            if len(self.search) == self.type_index:
                return True
            else:
                self.search = self.search[:self.type_index] + self.search[self.type_index+1:]
            #self.type_index -= 1
            return True
        if evt.type == 'BACK_SPACE':
            if self.type_index == 0:
                return True
            if len(self.search) == self.type_index:
                self.search = self.search[:-1]
            else:
                self.search = self.search[:self.type_index-1] + self.search[self.type_index:]
            self.type_index -= 1
            return True

        if not evt.unicode and not evt.ascii:
            return True
        if len(self.search) == self.type_index:
            self.search += evt.unicode
        else:
            self.search = self.search[:self.type_index] + evt.unicode + self.search[self.type_index:]
        self.type_index += 1
        return True
