from math import floor, radians, ceil
from time import time
from typing import Set

import bpy
from bpy.types import Brush, Texture
from mathutils import Vector
from sculpt_plus.sculpt_hotbar.canvas import Canvas
from sculpt_plus.prefs import SCULPTPLUS_AddonPreferences
from sculpt_plus.utils.cursor import Cursor, CursorIcon

from sculpt_plus.utils.math import clamp, point_inside_circle
from sculpt_plus.sculpt_hotbar.di import DiIma, DiImaco, DiLine, DiText, DiRct, DiCage, DiBr, get_rect_from_text, get_text_dim
from .wg_base import WidgetBase
from .wg_view import VerticalViewWidget
from sculpt_plus.lib.icons import Icon
from sculpt_plus.props import Props


SLOT_SIZE = 80
HEADER_HEIGHT = 32

class ShelfSidebar(VerticalViewWidget):
    interactable: bool = True
    use_scissor: bool = True
    scissor_padding: Vector = Vector((3, 3))

    def init(self) -> None:
        super().init()
        self.margin: int = 10
        self._is_on_hover_view: bool = False
        # self.scroll: int = 0

    def update(self, cv: Canvas, prefs: SCULPTPLUS_AddonPreferences) -> None:
        #super().update(cv, prefs)
        width = cv.hotbar.slot_size.x * 3 # item_size.x * 3 # * cv.scale
        # higher point - lower point
        height = cv.shelf.get_pos_by_relative_point(Vector((0, 1))).y - cv.hotbar.pos.y
        self.margin = 10 * cv.scale

        self.size = Vector((width, height))
        self.pos = cv.hotbar.get_pos_by_relative_point(Vector((0, 0))) - Vector((self.margin + width, 0))
        
        self.slot_width: int = width # int(self.size.x / self.num_cols)
        self.slot_height: int = int(self.slot_width * self.item_aspect_ratio)
        self.item_size = Vector((self.slot_width, self.slot_height)) #* cv.scale

    @property
    def expand(self):
        return self.cv.shelf.expand

    def on_hover(self, m: Vector, _p: Vector = None, _s: Vector = None) -> bool:
        if not self.expand:
            return False
        # Restar altura de 1 item, ahi se dibujará la cat activa.
        top_margin = Vector((0, self.item_size.y))
        # TODO. restar altura de header inferior con opciones...
        self._is_on_hover_view = super().on_hover(m, self.pos, self.size - top_margin)
        # BUG. Add the margin between sidebar and shelf to avoid cursor flickering.
        return super().on_hover(m, self.pos, Vector((self.size.x+self.margin+1, self.size.y)))

    def on_leftmouse_release(self, ctx, cv: Canvas, m: Vector) -> None:
        if not self._is_on_hover_view:
            return
        if not self.hovered_item:
            return False
        Props.BrushManager(ctx).set_active(self.hovered_item)
        ctx.area.tag_redraw()

    def on_left_click_drag(self, ctx, cv: Canvas, m: Vector) -> bool:
        if not self._is_on_hover_view:
            return False
        return super().on_left_click_drag(ctx, cv, m)

    def get_slot_at_pos(self, m: Vector) -> int:
        # Our mouse position at Y axis in the editor's region space.
        m_y = m.y

        # Get the top-left corner, and take into account the offset from the top header (item height).
        margin = self.get_view_margins_vertical()
        # pad = 6 * self.cv.scale
        p_top_y: int = self.get_pos_by_relative_point(Vector((0.0, 1.0))).y - margin[1] # self.item_size.y - pad

        # Mouse Y coordinate inside the top header.
        if m_y > p_top_y:
            return None

        cat_count: int = len(Props.BrushManager(bpy.context).collection) - 1 # Remove the active item.
        act_cat_idx: int = Props.BrushManager(bpy.context).active_index

        # Get the bottom-left corner height.
        p_bot_y: int = self.get_pos_by_relative_point(Vector((0.0, 0.0))).y

        # Get relative mouse Y coordinate inside the region (scrollable) area.
        # Taking into consideration the origin point as the top-left corner.
        m_y = clamp(m_y, p_bot_y, p_top_y) # Clamp between bottom and top.
        rel_m_y = m_y - p_top_y

        # Add the offset to the relative mouse Y coordinate to get the view position (projected position).
        # Value should be multiplied by -1 as Y axis between region and view are inverted.
        view_m_y = rel_m_y - self.scroll
        view_m_y *= -1

        # We calculate the index based on the mouse view position in Y axis and the item height.
        target_cat_idx: int = floor(view_m_y / self.item_size.y)

        # Workaround to prevent picking up the item at act_cat_idx.
        if target_cat_idx >= act_cat_idx:
            target_cat_idx += 1
        if target_cat_idx >= cat_count:
            return None
        
        # Return the item at target_cat_idx.
        return Props.GetBrushCat(bpy.context, target_cat_idx)

    def get_data(self, cv: Canvas) -> list:
        act_cat = Props.ActiveBrushCat(bpy.context)
        return [cat for cat in Props.BrushManager(bpy.context).collection if cat != act_cat]

    def draw_poll(self, context, cv: Canvas) -> bool:
        return self.expand and self.size.y > self.item_size.y

    def draw_item(self, slot_p, slot_s, item, thumb_size: Vector, color: Vector, scale: float, prefs: SCULPTPLUS_AddonPreferences):
        DiCage(slot_p, slot_s, 2, color)
        pad = 3 * scale
        if item.icon:
            DiIma(slot_p+Vector((pad, pad)), thumb_size, item.icon) #, (.92, .92, .92, .92))
        else:
            DiRct(slot_p+Vector((pad, pad)), thumb_size, Vector(prefs.theme_shelf_slot)*.8)
        DiText(slot_p+Vector((pad*2 + thumb_size.x, slot_s.y/2+pad)), item.name, 12, scale, pivot=(0, 0))
        DiText(slot_p+Vector((pad*2 + thumb_size.x, pad*3)), "v." + str(item.version), 11, scale, (.5, .5, .5, .5), pivot=(0, 0))

        if self.hovered_item == item:
            DiRct(slot_p, slot_s, (.6,.6,.6,.25))

    def get_draw_item_args(self, context, cv: Canvas, scale: float, prefs: SCULPTPLUS_AddonPreferences) -> tuple:
        pad = 3 * scale
        isize = self.item_size
        isize_thumb = Vector((isize.y - pad*2, isize.y - pad*2))
        bg_color = Vector(prefs.theme_shelf)
        bg_color.w *= 0.5
        return (
            isize_thumb,
            bg_color
        )

    def get_view_margins_vertical(self) -> tuple:
        ''' 0 -> Bottom margin;
            1 -> Top margin; '''
        return (0, self.item_size.y + 4)

    def draw_post(self, context, cv: Canvas, mouse: Vector, scale: float, prefs: SCULPTPLUS_AddonPreferences):
        p = self.get_pos_by_relative_point(Vector((0.0, 1.0)))
        DiText(p, '.', 1, 1) # RESET.
        p -= Vector((0, self.item_size.y))
        DiRct(p, self.item_size, (.05,0,.1,.5))
        self.draw_item(p, self.item_size,
                       Props.ActiveBrushCat(context),
                       self.get_draw_item_args(context, cv, scale, prefs)[0],
                       Vector(prefs.theme_active_slot_color),
                       scale, prefs)

        p.y -= 2 * scale
        DiLine(p, p+Vector((self.item_size.x, 0)), 2.4, (.05, .05, .05, .8))

        if self.hovered_item:
            pass

        if cv.active_ctx_widget:
            DiRct(self.pos, self.size, (.24, .24, .24, .64))

    '''
    def draw(self, context, cv: Canvas, mouse: Vector, scale: float, prefs: SCULPTPLUS_AddonPreferences):
        bg_color = Vector(prefs.theme_shelf)
        bg_color.w *= 0.5
        isize = Vector((self.size.x, self.size.x / 3))
        pad = 3 * scale
        isize_thumb = Vector((isize.y - pad*2, isize.y - pad*2))
        ioff = Vector((0, self.size.x / 3))
        p = self.get_pos_by_relative_point(Vector((0.0, 1.0))) - ioff

        # apply scroll
        brushes = context.scene.sculpt_hotbar.get_brushes()
        br_count: int = len(brushes)
        max_cats_in_view: int = floor(self.size.y / isize.y)
        max_scroll: int = br_count * isize.y - max_cats_in_view * isize.y
        if self.scroll > max_scroll:
            self.scroll = max_scroll
        p += Vector((0, self.scroll))
        for idx, br in enumerate(brushes):
            if p.y > self.size.y:
                p -= ioff
                continue

            #DiRct(p, isize, bg_color)
            DiCage(p, isize, 2, bg_color)
            DiBr(p+Vector((pad, pad)), isize_thumb, br)
            DiText(p+Vector((pad + isize_thumb.x, isize.y/2+pad)), "Brush Category %i" % idx, 12, scale, pivot=(0, 0))
            DiText(p+Vector((pad + isize_thumb.x, pad*3)), br.name, 11, scale, (.5, .5, .5, .5), pivot=(0, 0))
            p -= ioff

            if p.y < (-isize.y+5):
                break
    '''

    def draw_pre(self, context, cv: Canvas, mouse: Vector, scale: float, prefs: SCULPTPLUS_AddonPreferences):
        p, s = self.pos, self.size
        DiText(p, '.', 1, 1) # RESET.
        color = Vector(prefs.theme_shelf)
        color.w *= 0.5
        DiRct(self.pos, self.size, color)
        DiCage(self.pos, self.size, 3.2*scale, color*.9)

    def draw_over(self, context, cv: Canvas, mouse: Vector, scale: float, prefs: SCULPTPLUS_AddonPreferences):
        pass
