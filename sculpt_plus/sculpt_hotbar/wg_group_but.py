from math import ceil
from telnetlib import SE
from time import time
from typing import Any, Dict, List, Set, Tuple
from uuid import uuid4
from bpy import ops as OP
from mathutils import Vector
from sculpt_plus.sculpt_hotbar.canvas import Canvas
from sculpt_plus.sculpt_hotbar.di import DiCage, DiIma, DiImaco, DiRct, DiText
from sculpt_plus.lib.icons import BrushIcon, Icon
from sculpt_plus.prefs import SCULPTPLUS_AddonPreferences
from sculpt_plus.sculpt_hotbar.wg_base import WidgetBase


SLOT_SIZE = 22

class ButtonGroup(WidgetBase):
    fill_by: str = 'ROWS'
    #modal_trigger: Set[str] = {'LEFTMOUSE'}
    relative_to_bar_pos = (0, 1)
    rows: int = 2
    items: Tuple[str, Dict[str, Any]]
    align_dir: str = 'LEFT'

    def init(self) -> None:
        self.opacity = 1.0
        self.hovered_item = None
        self.padding = 4
        self.items_pos = []
        self.item_size = Vector((SLOT_SIZE, SLOT_SIZE))
        self.item_toggle = None


    def get_hovered_item_data(self) -> Dict[str, Any]:
        if self.hovered_item is not None:
            return self.items[self.hovered_item]
        return None


    def update(self, cv: Canvas, prefs: SCULPTPLUS_AddonPreferences) -> None:
        item_count: int = len(self.items)
        self.cols = ceil(item_count / self.rows)

        # Size.
        pad = self.padding * cv.scale
        isize = SLOT_SIZE * cv.scale
        self.size = s = Vector((
            isize*self.cols + int((pad-1)*self.cols), # (isize+pad)*self.cols,
            isize*self.rows + int((pad-1)*self.rows), # (isize+pad)*self.rows
        ))

        # Position.
        '''
        bar_pos = cv.hotbar.pos
        bar_height = cv.hotbar.size.y
        self.pos = p = Vector((
            bar_pos.x,
            bar_pos.y + bar_height + pad*2
        ))
        '''
        origin = cv.hotbar.get_pos_by_relative_point(Vector(self.relative_to_bar_pos))
        if self.relative_to_bar_pos[0] != 0:
            origin.x -= s.x * self.relative_to_bar_pos[0]
            if self.align_dir == 'RIGHT':
                origin.x += (s.x + pad + isize)
        #if self.relative_to_bar_pos[1] != 0:
        #    origin.y += s.y * self.relative_to_bar_pos[1]
        is_zero: bool = not all(self.relative_to_bar_pos)
        self.pos = p = Vector((
            origin.x - pad*2 if is_zero else origin.x,
            origin.y if is_zero else origin.y + pad*2
        ))

        # print(self.relative_to_bar_pos, origin, self.pos, self.size)

        # Slot Size.
        self.item_size = Vector((isize, isize))

        # Slot Position.
        col_idx = 0
        row_idx = 0
        items: List[Vector] = []
        for i in range(item_count):
            pos = p.copy()
            if col_idx != 0:
                pos.x += (isize+pad) * col_idx #+ pad * (col_idx-1)
            if row_idx != 0:
                pos.y += (isize+pad) * row_idx #+ pad * (row_idx-1)

            items.append(pos)

            if self.fill_by == 'ROWS':
                col_idx += 1
                if col_idx >= self.cols:
                    row_idx += 1
                    col_idx = 0
            elif self.fill_by == 'COLS':
                row_idx += 1
                if row_idx >= self.rows:
                    col_idx += 1
                    row_idx = 0

        self.items_pos = items

    def update_items(self):
        cv = self.cv
        item_count: int = len(self.items)
        pad = self.padding * cv.scale
        isize = SLOT_SIZE * cv.scale

        # Slot Position.
        col_idx = 0
        row_idx = 0 if self.fill_by == 'ROWS' else (self.rows-1)
        items: List[Vector] = []
        for i in range(item_count):
            pos = self.pos.copy()
            if col_idx != 0:
                pos.x += (isize+pad) * col_idx #+ pad * (col_idx-1)
            if row_idx != 0:
                pos.y += (isize+pad) * row_idx #+ pad * (row_idx-1)

            items.append(pos)

            if self.fill_by == 'ROWS':
                col_idx += 1
                if col_idx >= self.cols:
                    row_idx += 1
                    col_idx = 0
            elif self.fill_by == 'COLS':
                row_idx -= 1
                if row_idx < 0:
                    col_idx += 1
                    row_idx = (self.rows-1)

        self.items_pos = items

    def on_hover_item(self, m, p, s):
        return m.x>p.x and m.x<p.x+s.x and m.y>p.y and m.y<p.y+s.y

    def on_hover_stay(self, m: Vector) -> None:
        for idx, ipos in enumerate(self.items_pos):
            if self.on_hover_item(m, ipos, self.item_size):
                self.hovered_item = idx
                return
        self.hovered_item = None

    def on_hover_enter(self) -> None:
        self.on_hover_stay(self.cv.mouse)

    def on_hover_exit(self) -> None:
        self.hovered_item = None

    def on_left_click(self, ctx, cv: Canvas, m: Vector) -> None:
        if self.hovered_item is None:
            return
        item = self.items[self.hovered_item]
        print("hovered item to trigger:", item)
        if 'pre_func_ctx' in item:
            item['pre_func_ctx'](ctx)
        item['func'](*item['args'], **item['kwargs'])
        if 'post_func_ctx' in item:
            item['post_func_ctx'](ctx)
        if 'toggle' in item:
            self.item_toggle = item

    def poll(self, context, cv: Canvas) -> bool:
        return cv.shelf.anim_running() and not cv.shelf.expand and not cv.shelf_drag.dragging

    def draw(self, context, cv: Canvas, mouse: Vector, scale: float, prefs: SCULPTPLUS_AddonPreferences):
        if self.item_toggle:
            if not self.item_toggle['toggle'](context):
                self.item_toggle = None
        p, s = self.pos, self.size
        hover_item = self.hovered_item
        DiText(p, ".", 1, scale, prefs.theme_text)

        DiRct(p, s, (0.12, 0.12, 0.12, .75))

        isize = self.item_size
        for idx, (ipos, item) in enumerate(zip(self.items_pos, self.items)):
            if idx==hover_item or item==self.item_toggle:
                color = list(prefs.theme_hotbar_slot if (idx!=hover_item and item!=self.item_toggle) else prefs.theme_active_slot_color)
                color[-1] *= self.opacity * .75
                DiRct(ipos, isize, color)
            color = list(Vector(prefs.theme_hotbar_slot)*.9)
            color[-1] *= self.opacity * .5
            DiCage(ipos, isize, 1.3, color)
            # TODO: support icons.
            #DiIma(Vector((0,0)), Vector((1,1)), bpy.data)
            icon = item['icon']
            if isinstance(icon, (Icon, BrushIcon)):
                icon_col = item.get('icon_color', None)
                icon_scale = item.get('icon_scale', 1.0)
                if icon_scale != 1:
                    d = isize[0] * (1.0 - icon_scale)
                    pad = Vector((d, d))
                else:
                    pad = Vector((2, 2))
                if idx == hover_item or icon_col:
                    color = list(icon_col or prefs.theme_text)
                    color[-1] *= self.opacity
                    DiImaco(
                        ipos+pad,
                        isize-pad*2,
                        icon(),
                        color
                    )
                else:
                    DiIma(
                        ipos+pad,
                        isize-pad*2,
                        icon()
                    )
                if icon_scale != 1:
                    isize = self.item_size
            elif isinstance(icon, str):
                color = list(prefs.theme_text)
                color[-1] *= self.opacity
                DiText(ipos+isize/2, icon, 12, scale, prefs.theme_text, (.5, .5))

        color = list(Vector(prefs.theme_hotbar_slot)*1.1)
        color[-1] *= self.opacity
        DiCage(p, s, 1.3, color)

class MultiButtonGroup(WidgetBase):
    #interactable: bool = False
    fill_by: str = 'COLS'
    relative_to_bar_pos = (0, 1)
    rows: int = 2
    group_items: Tuple[Tuple[Dict[str, Any]]] = ()
    #interactable: bool = False

    def init(self) -> None:
        self.hovered_group = None
        self.groups: List[ButtonGroup] = []
        for group in self.group_items:
            button_group_type: ButtonGroup = type(
                "ButtonGroup_" + uuid4().hex,
                (ButtonGroup,),
                {
                    'fill_by': self.fill_by,
                    'relative_to_bar_pos': self.relative_to_bar_pos,
                    'rows': self.rows,
                    'items': group,
                }
            )
            self.groups.append(button_group_type(self.cv))
        '''
        for group in self.groups:
            group.opacity = .5
        '''
        #self.update(self.cv, None)

    def get_hovered_item_data(self) -> Dict[str, Any]:
        if self.hovered_group:
            return self.hovered_group.get_hovered_item_data()
        return None

    def update(self, cv: Canvas, prefs: SCULPTPLUS_AddonPreferences) -> None:
        prev_pos: Vector = None
        prev_size: Vector = None
        pos_off: Vector = Vector((0, 0))
        min_pos: Vector = Vector((10000000, 10000000))
        max_pos: Vector = Vector((0, 0))
        max_size: Vector = Vector((0, 0))
        is_zero: bool = not all(self.relative_to_bar_pos)
        for i, group in enumerate(self.groups):
            group.update(cv, prefs)
            if prev_pos:
                if self.relative_to_bar_pos[0] == 0:# and not is_zero:
                    group.pos.x += pos_off.x
                elif self.relative_to_bar_pos[0] == 1:# or is_zero:
                    group.pos.x -= pos_off.x
                group.size.x -= i*.36*group.padding
                group.update_items()
            # print(i, group.pos, group.size)
            prev_pos = group.pos.copy()
            prev_size = group.size.copy()
            pos_off.x += (prev_size.x + 10*cv.scale)
            if prev_pos.x < min_pos.x:
                min_pos.x = prev_pos.x
            if prev_pos.y < min_pos.y:
                min_pos.y = prev_pos.y
            if prev_pos.x > max_pos.x:
                max_pos.x = prev_pos.x
            if prev_pos.y > max_pos.y:
                max_pos.y = prev_pos.y

            if prev_size.y > max_size.y:
                max_size.y = prev_size.y
        self.pos: Vector = min_pos
        self.size: Vector = Vector((pos_off.x, max_size.y))
        #print("pos/size", self.pos, self.size)

        if is_zero:
            for group in self.groups:
                group.pos.x -= self.size.x
                group.update_items()

    def on_hover(self, m: Vector, p: Vector = None, s: Vector = None) -> bool:
        if self.hovered_group:
            if self.hovered_group._on_hover(self.cv.hover_ctx, m):
                return True
        for group in self.groups:
            if group._on_hover(self.cv.hover_ctx, m):
                self.hovered_group = group
                return True
        return False # super().on_hover(m)

    '''
    def on_hover_enter(self) -> None:
        for group in self.groups:
            group.opacity = 1.0

    def on_hover_exit(self) -> None:
        for group in self.groups:
            group.opacity = .5
        self.hovered_group = None
    '''

    def on_left_click(self, ctx, cv: Canvas, m: Vector) -> None:
        if self.hovered_group:
            self.hovered_group.on_left_click(ctx, cv, m)

    def poll(self, context, cv: Canvas) -> bool:
        return cv.shelf.anim_running() and not cv.shelf.expand and not cv.shelf_drag.dragging

    def draw(self, *args):
        for group in self.groups:
            group.draw(*args)
