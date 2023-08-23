from time import time
from typing import Set, List, Union

import bpy
# from bpy.types import Brush
from mathutils import Vector
from sculpt_plus.sculpt_hotbar.canvas import Canvas
from sculpt_plus.prefs import SCULPTPLUS_AddonPreferences
from sculpt_plus.utils.cursor import Cursor, CursorIcon
from sculpt_plus.utils.math import ease_quad_in_out

from sculpt_plus.utils.math import clamp, point_inside_circle
from sculpt_plus.sculpt_hotbar.di import DiIcoCol, DiLine, DiText, DiRct, DiCage, DiBr, get_rect_from_text, get_text_dim, DiTriCorner, DiStar, DiIcoOpGamHl, DiBMType
from .wg_base import WidgetBase
from sculpt_plus.lib.icons import Icon
from sculpt_plus.props import hm_data, bm_data
from sculpt_plus.management.hotbar_layer import HotbarLayer

from brush_manager.api import bm_types
from brush_manager.globals import GLOBALS



class ShelfLayers(WidgetBase):
    hovered_item: HotbarLayer
    selected_item: HotbarLayer
    
    def init(self) -> None:
        super().init()
        self.enabled = False
    
    



class ShelfLayerSets(WidgetBase):
    def init(self) -> None:
        super().init()
        self.enabled = False

    def update(self, cv: Canvas, prefs: SCULPTPLUS_AddonPreferences):
        scale = cv.scale

        hotbar = cv.hotbar
        isize = hotbar.item_size
        width = hotbar.size.x
        x = hotbar.pos.x
        y = hotbar.get_pos_by_relative_point(Vector((0, 1))).y

        self.label_height = 24 * scale
        self.pad = 5 * scale
        self.margin = 6 * scale

        self.pos = Vector((x, y + self.margin))
        self.size = Vector((width, isize.y * 2 + self.label_height * 2 + self.pad * 2))

    def poll(self, _context, cv: Canvas) -> bool:
        return cv.shelf.expand

    def draw_poll(self, context, cv: Canvas) -> bool:
        return cv.shelf.expand and cv.shelf.size.y > self.slot_size

    def draw_pre(self, context, cv: Canvas, mouse: Vector, scale: float, prefs: SCULPTPLUS_AddonPreferences):
        return super().draw_pre(context, cv, mouse, scale, prefs)

    def draw_post(self, _context, cv: Canvas, mouse: Vector, scale: float, _prefs: SCULPTPLUS_AddonPreferences):
        pass
