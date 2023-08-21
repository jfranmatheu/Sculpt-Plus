from math import floor, radians, ceil
from time import time
from typing import Set, Union, List

import bpy
from bpy.types import Brush, Texture
from mathutils import Vector
from sculpt_plus.sculpt_hotbar.canvas import Canvas
from sculpt_plus.prefs import SCULPTPLUS_AddonPreferences
from sculpt_plus.utils.cursor import Cursor, CursorIcon

from sculpt_plus.utils.math import clamp, point_inside_circle
from sculpt_plus.sculpt_hotbar.di import DiIma, DiImaco, DiLine, DiText, DiRct, DiCage, DiBr, get_rect_from_text, get_text_dim, DiIco, DiIcoCol, DiBMType
from .wg_base import WidgetBase
from .wg_view import VerticalViewWidget
from sculpt_plus.lib.icons import Icon
from sculpt_plus.props import bm_data
from .wg_but import ButtonGroup

from brush_manager.api import bm_types, BM_OPS, BM_UI
from brush_manager.globals import GLOBALS


SLOT_SIZE = 80
HEADER_HEIGHT = 32

class ShelfSidebar(VerticalViewWidget):
    interactable: bool = True
    use_scissor: bool = True
    scissor_padding: Vector = Vector((3, 3))
    hovered_item: Union[bm_types.BrushCat, bm_types.TextureCat]

    item_aspect_ratio: float = 1 / 3.5

    def init(self) -> None:
        super().init()
        self.margin: int = 10
        self._is_on_hover_view: bool = False
        # self.scroll: int = 0
        self.type: str = 'BRUSH' # 'TEXtURE'
        self.item_size = None
        self.footer_height = 0
        self.header_height = 0

    def update(self, cv: Canvas, prefs: SCULPTPLUS_AddonPreferences) -> None:
        #super().update(cv, prefs)
        width = cv.hotbar.slot_size.x * 3 * cv.scale # item_size.x * 3 # * cv.scale
        # higher point - lower point
        footer_height = 24 * cv.scale
        slot_height: int = 0 # IF fixed header cat: # int(width * self.item_aspect_ratio)
        height = cv.shelf.get_pos_by_relative_point(Vector((0, 1))).y - cv.hotbar.pos.y - footer_height - slot_height
        self.margin = 10 * cv.scale

        self.size = Vector((width, height))
        self.pos = cv.hotbar.get_pos_by_relative_point(Vector((0, 0))) - Vector((self.margin + width, -footer_height))

        self.footer_height = footer_height
        self.header_height = slot_height

        #slot_width: int = width # int(self.size.x / self.num_cols)
        #slot_height: int = int(slot_width * self.item_aspect_ratio)
        #self.item_size = Vector((slot_width, slot_height)) #* cv.scale

        super().update(cv, prefs)

    @property
    def expand(self):
        return self.cv.shelf.expand

    def on_hover(self, m: Vector, _p: Vector = None, _s: Vector = None) -> bool:
        if not self.expand:
            return False
        # Restar altura de 1 item, ahi se dibujará la cat activa.
        # top_margin = Vector((0, self.item_size.y))
        # TODO. restar altura de header inferior con opciones...
        self._is_on_hover_view = super().on_hover(m, self.pos, self.size) # - top_margin)
        # BUG. Add the margin between sidebar and shelf to avoid cursor flickering.
        if super().on_hover(m, self.pos, Vector((self.size.x+self.margin+1, self.size.y + self.item_size.y))):
            if not self._is_on_hover_view and super().on_hover(m, self.get_pos_by_relative_point(Vector((0, 1))), self.item_size):
                self.hovered_item = bm_data.active_category
            else:
                self.hovered_item = None
            return True
        return False

    def on_leftmouse_release(self, ctx, cv: Canvas, _m: Vector) -> None:
        if not self._is_on_hover_view:
            return
        if not self.hovered_item:
            return False
        bm_data.active_category = self.hovered_item
        cv.refresh(ctx)

    def on_left_click_drag(self, ctx, cv: Canvas, m: Vector) -> bool:
        if not self._is_on_hover_view:
            return False
        return super().on_left_click_drag(ctx, cv, m)

    # def on_right_click(self, ctx, cv: Canvas, m: Vector) -> None:
    def on_rightmouse_press(self, ctx, cv: Canvas, m: Vector) -> int:
        if self.hovered_item is None and self._is_on_hover_view:
            return 0
        if self._is_on_hover_view:
            hovered_cat = self.hovered_item
        else:
            hovered_cat = bm_data.active_category
        if hovered_cat is None:
            return 0
        cv.ctx_shelf_sidebar_item.show(cv, m, hovered_cat)
        self.hovered_item = None
        return 1

    def get_data(self, _cv: Canvas) -> list:
        return list(bm_data.get_cats(skip_active=False))

    def poll(self, _context, cv: Canvas) -> bool:
        return cv.shelf.expand and self.size.y > self.item_size.y

    def draw_item(self,
                  slot_p,
                  slot_s,
                  item: Union[bm_types.BrushCat, bm_types.TextureCat],
                  is_hovered: bool,
                  act_item: Union[bm_types.BrushCat, bm_types.TextureCat],
                  thumb_size: Vector,
                  color: Vector,
                  scale: float,
                  prefs: SCULPTPLUS_AddonPreferences):

        DiLine(slot_p, slot_p+Vector((slot_s[0], 0)), 2, color)

        pad = 5 * scale

        def draw_fallback(p, s, cat, act: bool, op: float):
            # DiRct(p, s, Vector(prefs.theme_shelf_slot)*.8)
            DiIcoCol(p, s, Icon.PENCIL_CASE_1 if self.type == 'BRUSH' else Icon.TEXTURE_SMALL, (.9, .9, .9, 1.0 if act else .82))

        DiBMType(
            slot_p+Vector((pad, pad)),
            thumb_size,
            item,
            is_hovered,
            draw_fallback=draw_fallback
        )

        # DiRct(slot_p+Vector((pad, pad)), thumb_size, Vector(prefs.theme_shelf_slot)*.8)

        DiText(slot_p+Vector((pad*2 + thumb_size.x, slot_s.y/2+pad)), item.name, 13, scale, pivot=(0, 0))
        # DiText(slot_p+Vector((pad*2 + thumb_size.x, pad*2)), '( ' + str(item.items.count) + ' )', 11, scale, (.5, .5, .5, .5), pivot=(0, 0))

        if is_hovered:
            DiRct(slot_p, slot_s, (.6,.6,.6,.25))

        if item == act_item:
            DiCage(slot_p+Vector((pad, pad)), slot_s-Vector((pad, pad))*2, 3.2*scale, Vector(prefs.theme_active_slot_color))

    def get_draw_item_args(self, _context, _cv: Canvas, scale: float, prefs: SCULPTPLUS_AddonPreferences) -> tuple:
        pad = 5 * scale
        isize = self.item_size
        isize_thumb = Vector((isize.y - pad*2, isize.y - pad*2))
        bg_color = Vector(prefs.theme_shelf)
        bg_color.w *= 0.5
        return (
            bm_data.active_category,
            isize_thumb,
            bg_color
        )

    def draw_post(self, context, cv: Canvas, mouse: Vector, scale: float, prefs: SCULPTPLUS_AddonPreferences):
        return
        act_item = bm_data.active_category

        p = self.get_pos_by_relative_point(Vector((0.0, 1.0)))
        ## DiText(p, '.', 1, 1) # RESET.
        # p -= Vector((0, self.item_size.y))
        DiRct(p, self.item_size, (.08,0.05,.1,.8))

        if act_item is None:
            # print("None active brush cat", bm_data.brush_cats.count)
            DiText(p+Vector((10, 10))*scale, 'No Active Category', 14, scale, (.95, .4, .2, .9)) # RESET.
            DiCage(p, self.item_size, 2, Vector(prefs.theme_sidebar))
            DiLine(p, p+Vector((self.item_size.x, 0)), 3.0, (.08, .08, .08, .8))
            return

        self.draw_item(p, self.item_size,
                       act_item,
                       super().on_hover(mouse, p, self.item_size),
                       self.get_draw_item_args(context, cv, scale, prefs)[0],
                       Vector(prefs.theme_active_slot_color),
                       scale, prefs)

        p.y -= 2 * scale
        DiLine(p, p+Vector((self.item_size.x, 0)), 3.0, (.08, .08, .08, .8))

        if self.hovered_item:
            pass

        if cv.active_ctx_widget:
            DiRct(self.pos, self.size, (.24, .24, .24, .64))

    def draw_pre(self, context, cv: Canvas, mouse: Vector, scale: float, prefs: SCULPTPLUS_AddonPreferences):
        p, s = self.pos, self.size
        color = Vector(prefs.theme_shelf)
        color.w *= 0.5
        DiRct(p, s, color)
        DiCage(p, s, 3.2*scale, color*.9)

    def draw_over(self, context, cv: Canvas, mouse: Vector, scale: float, prefs: SCULPTPLUS_AddonPreferences):
        pass


class ShelfSidebarActions(ButtonGroup):
    def init(self) -> None:
        super().init()
        self.new_button(
            "New",
            Icon.ADD_ROW,
            lambda ctx, cv: BM_OPS.new_category(cat_name=None, ui_context_mode='SCULPT')
        )
        self.new_button(
            "Import",
            Icon.DOWNLOAD,
            lambda ctx, cv: BM_OPS.import_library(ui_context_mode='SCULPT'),
            draw_poll=lambda ctx, cv: BM_UI.get_data(ctx).ui_context_item == 'BRUSH'
        )


    def update(self, cv: Canvas, prefs: SCULPTPLUS_AddonPreferences) -> None:
        shelf_sidebar = cv.shelf_sidebar
        self.pos = shelf_sidebar.pos
        self.size.x = shelf_sidebar.size.x
        self.size.y = 24 * cv.scale
        self.pos.y -= self.size.y

        super().update(cv, prefs)

    def poll(self, _context, cv: Canvas) -> bool:
        return cv.shelf.expand
