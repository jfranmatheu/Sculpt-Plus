from math import floor, radians
from time import time
from typing import Set

import bpy
from bpy.types import Brush, Texture
from mathutils import Vector
from sculpt_hotbar.canvas import Canvas
from sculpt_hotbar.prefs import SculptHotbarPreferences
from sculpt_hotbar.utils.cursor import Cursor, CursorIcon

from sculpt_hotbar.utils.math import clamp, point_inside_circle
from sculpt_hotbar.di import DiIma, DiImaco, DiLine, DiText, DiRct, DiCage, DiBr, get_rect_from_text, get_text_dim
from sculpt_hotbar.wg_view import ViewWidget
from .wg_base import WidgetBase
from sculpt_hotbar.icons import Icon


SLOT_SIZE = 80
HEADER_HEIGHT = 32

class Sidebar(WidgetBase):
    interactable: bool = False

    def init(self) -> None:
        self._expand = False
        self.handler_size = Vector((30, 100))
        self.handler_pos = Vector((10, 500))

    def update(self, cv: Canvas, prefs: SculptHotbarPreferences) -> None:
        bar_height = (cv.hotbar.size.y) * 2.0
        height = cv.size.y - bar_height * 2

        if self.expand:
            self.pos = Vector((prefs.margin_left, bar_height))
            slot_size = SLOT_SIZE * self.cv.scale
            width = slot_size * 5.5
            self.size = Vector((width, height))
        else:
            self.size = Vector((0, height)) # Vector((SLOT_SIZE*cv.scale*.5, SLOT_SIZE*cv.scale*2))
            self.pos = Vector((0, bar_height)) # prefs.margin_left, cv.size.y*.5-SLOT_SIZE*cv.scale))

        self.handler_size = Vector((50*cv.scale*.5, 54*cv.scale*2))
        self.handler_pos = Vector((prefs.margin_left, cv.size.y*.5-50*cv.scale))


    @property
    def expand(self):
        return self._expand

    @expand.setter
    def expand(self, state: bool):

        def _update():
            #self.update(self.cv, None)
            self.cv.sidebar_grid.update(self.cv, None)

        if state == False:
            def _disable():
                self._expand = False

            self.resize(x=0, animate=True, anim_change_callback=_update, anim_finish_callback=_disable)

        else:
            self._expand = True

            def _enable():
                self._expand = True

            slot_size = SLOT_SIZE * self.cv.scale
            width = slot_size * 5.5
            self.resize(x=width, animate=True, anim_change_callback=_update, anim_finish_callback=_enable)

    def on_hover(self, m: Vector, _p: Vector = None, _s: Vector = None) -> bool:
        if not self.expand:
            #if m.x < (20 * self.cv.scale):
            if super().on_hover(m, self.handler_pos, self.handler_size):
                self.expand = True
                return True
        elif 'size_x' not in self.anim_pool:
            if m.x < self.size.x:
                return True
            self.expand = False
        return False

    def on_leftmouse_press(self, ctx, cv: Canvas, m: Vector) -> None:
        pass

    def on_hover_stay(self, m: Vector) -> None:
        if self.cv.sidebar_grid.on_hover(m):
            self.cv.sidebar_grid.on_hover_stay(m)

    def on_hover_exit(self) -> None:
        self.cv.sidebar_grid.on_hover_exit()
        
    def draw_poll(self, context, cv: Canvas) -> bool:
        return True

    def draw(self, context, cv: Canvas, mouse: Vector, scale: float, prefs: SculptHotbarPreferences):
        if self.expand:
            out_col = Vector(prefs.theme_sidebar)*.9
            out_col.w = 1.0
            from bgl import glDisable, GL_POLYGON_SMOOTH, glEnable
            glDisable(GL_POLYGON_SMOOTH)
            DiRct(self.pos, self.size, prefs.theme_sidebar)
            glEnable(GL_POLYGON_SMOOTH)
            DiCage(self.pos, self.size, 3.2*scale, out_col)
     
    def draw_over(self, context, cv: Canvas, mouse: Vector, scale: float, prefs: SculptHotbarPreferences):
        if not self.expand:
            DiRct(self.handler_pos, self.handler_size, (.16, .16, .16, .5))
            #DiText(self.handler_pos+self.handler_size/2, ": : :", 14, scale, pivot=(-.24,1), rotation=radians(90))
            s = self.handler_size.x - 12*scale
            im_size = Vector((s, s))
            im_pos = self.handler_pos+self.handler_size*.5-im_size*.5
            DiText(Vector((0,0)),' ',1,scale)
            DiImaco(im_pos, im_size, Icon.ARROW_RIGHT(), (.9, .9, .9, .5))
            DiCage(self.handler_pos, self.handler_size, 2.4*scale, (.1, .1, .1, .8))

class SidebarGrid(ViewWidget):
    use_scissor: bool = True
    grid_slot_size: int = 80

    def get_max_width(self, cv: Canvas, scale) -> float:
        padding = 6 * scale
        return self.slot_size * 5.5 - padding * 2

    def update(self, cv: Canvas, prefs: SculptHotbarPreferences):
        scale = cv.scale

        p = self.cv.sidebar.pos.copy()
        s = self.cv.sidebar.size.copy()

        padding = 6 * scale
        margin = 6 * scale

        # add margin from search.
        shelf_search_height = HEADER_HEIGHT * scale
        s.y -= (shelf_search_height + margin * 2)

        p += Vector((padding, padding))
        s -= (Vector((padding, padding)) * 2.0)

        self.pos = p.copy()
        self.size = s

    def get_data(self, cv: Canvas) -> list:
        #filt = cv.shelf_search.search
        #if filt:
        #    filt = filt.lower()
        #    br_startswith = {br for br in bpy.data.brushes if br.use_paint_sculpt and br.name.lower().startswith(filt)}
        #    br_contains = [br for br in bpy.data.brushes if br not in br_startswith and br.use_paint_sculpt and filt in br.name.lower()]
        #    brushes = list(br_startswith) + br_contains
        #else:
        #    images = [br for br in bpy.data.brushes if br.use_paint_sculpt]
        images = [i for i in bpy.data.images if i.name[0] != '.' and i.file_format in {'JPEG', 'PNG'} and i.source == 'FILE' and i.size[0] > 128 and i.size[1] > 128]# and i.size[0] == i.size[1]]
        #print(images, "images...")
        return images

    def draw_poll(self, context, cv: Canvas) -> bool:
        return cv.sidebar.expand and cv.sidebar.size.x > self.slot_size

    def get_draw_item_args(self, context, cv: Canvas, scale: float, prefs: SculptHotbarPreferences) -> tuple:
        slot_color = Vector(prefs.theme_sidebar_slot)
        return (slot_color,)

    def draw_item(self, slot_p, slot_s, tex, slot_color, scale: float, prefs: SculptHotbarPreferences):
        #print(tex.name, slot_p, slot_s)
        DiRct(slot_p, slot_s, slot_color)
        DiIma(slot_p, slot_s, tex)
        if tex == self.selected_item:
            DiCage(slot_p, slot_s, 2.4*scale, prefs.theme_active_slot_color) #(.2, .6, 1.0, 1.0))
        else:
            DiCage(slot_p, slot_s, 2.4*scale, slot_color*1.3)
        if self.hovered_item == tex:
            DiRct(slot_p, slot_s, (.6,.6,.6,.25))
