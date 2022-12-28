from math import floor
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
from sculpt_plus.sculpt_hotbar.di import DiIcoCol, DiLine, DiText, DiRct, DiCage, DiBr, get_rect_from_text, get_text_dim, DiTriCorner, DiStar, DiIcoOpGamHl
from sculpt_plus.sculpt_hotbar.wg_view import ViewWidget
from .wg_base import WidgetBase
from sculpt_plus.lib.icons import Icon
from sculpt_plus.props import Props, Brush, Texture


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
            self.cv.shelf_sidebar_actions.update(self.cv, None)
            self.cv.shelf_sidebar.update(self.cv, None)
            self.cv.shelf_ctx_switcher.update(self.cv, None)
            self.cv.shelf_grid_item_info.update(self.cv, None)

        if state == False:
            self.cv.shelf_grid.selected_item = None

            self.cv.shelf_grid_item_info.enabled = False

            def _disable():
                self._expand = False
                self.cv.shelf_drag.interactable = True

            self.resize(y=0, animate=True, anim_change_callback=_update, anim_finish_callback=_disable)

        else:
            self._expand = True
            self.cv.shelf_grid_item_info.enabled = True
            self.cv.shelf_grid_item_info.update(self.cv, None)
            if self.cv.shelf_grid.type == 'TEXTURE':
                self.cv.shelf_grid_item_info.expand = True

            def _enable():
                self._expand = True
                self.cv.shelf_drag.interactable = True

            r: float = self.size.y * .2
            slot_size = SLOT_SIZE * self.cv.scale
            height = slot_size * 5.25 # int(self.cv.size.y * .65) # self.cv.size.y - self.cv.shelf.pos.y - self.cv.hotbar.size.y - r
            self.resize(y=height, animate=True, anim_change_callback=_update, anim_finish_callback=_enable)

    def update(self, cv: Canvas, prefs: SCULPTPLUS_AddonPreferences):
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

    def draw_poll(self, context, cv: Canvas) -> bool:
        return self.expand

    def draw(self, context, cv: Canvas, mouse: Vector, scale: float, prefs: SCULPTPLUS_AddonPreferences):
        DiRct(self.pos, self.size, prefs.theme_shelf)
        DiCage(self.pos, self.size, 3.2*scale, Vector(prefs.theme_shelf)*.9)


class ShelfGrid(ViewWidget):
    use_scissor: bool = True
    grid_slot_size: int = 56
    hovered_item: Union[Brush, Texture]
    selected_item: Union[Brush, Texture]
    type: str

    def init(self) -> None:
        super().init()
        self.type: str = 'BRUSH' # 'TEXTURE'
        self.show_all_brushes: bool = True

    def get_max_width(self, cv: Canvas, scale) -> float:
        return self.size.x
        padding = 6 * scale
        return SLOT_SIZE * scale * 5.25 - padding * 2

    def update(self, cv: Canvas, prefs: SCULPTPLUS_AddonPreferences):
        info_expanded = cv.shelf_grid_item_info.expand

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

        if info_expanded:
            info_panel_width = cv.shelf_grid_item_info.size.x
            p.x += info_panel_width
            s.x -= info_panel_width

        self.pos = p.copy()
        self.size = s

    def on_left_click(self, ctx, cv: Canvas, m: Vector) -> None:
        return super().on_left_click(ctx, cv, m)

    def on_leftmouse_release(self, ctx, cv: Canvas, m: Vector) -> None:
        super().on_leftmouse_release(ctx, cv, m)
        if self.type == 'TEXTURE' and self.selected_item:
            texture: Texture = self.selected_item
            texture.to_brush(ctx)
        return False

    def on_double_click(self, ctx, cv: Canvas, m: Vector) -> None:
        if self.hovered_item is None:
            return
        if self.type == 'BRUSH':
            if self.hovered_item.id in Props.GetHotbarBrushIds():
                Props.SetHotbarSelected(ctx, self.hovered_item)
            else:
                Props.SelectBrush(ctx, self.hovered_item)
        elif self.type == 'TEXTURE':
            pass

        # Close shelf.
        cv.shelf.expand = False

    # def on_right_click(self, ctx, cv: Canvas, m: Vector) -> None:
    def on_rightmouse_press(self, ctx, cv: Canvas, m: Vector) -> int:
        if self.hovered_item is None:
            return 0
        if Props.GetActiveCat(self.type) is None:
            return 0
        cv.ctx_shelf_item.show(cv, m, self.hovered_item)
        self.hovered_item = None
        return 1

    def on_numkey(self, ctx, number: int, cv: Canvas, m: Vector) -> None:
        if not self.selected_item:
            return
        #if not cv.shelf.expand:
        #    return
        list_index = 9 if number==0 else number-1
        # ctx.scene.sculpt_hotbar.set_brush(list_index, self.selected_item)
        Props.SetHotbarBrush(list_index, self.selected_item)
        self.selected_item = None

    def get_data(self, cv: Canvas) -> list:
        # Get brushes from source.
        #if self.show_all_brushes:
        #    brushes = bpy.data.brushes
        #else:
        items: List[Union[Brush, Texture]] = Props.GetActiveCatItems(self.type)
        if items is None:
            return []

        # Apply filter (if exist).
        filt = cv.shelf_search.search
        if filt:
            filt = filt.lower()
            startswith = {item for item in items if item.name.lower().startswith(filt)}
            contains = [item for item in items if item not in startswith and filt in item.name.lower()]
            items = list(startswith) + contains
        #else:
        #    if self.show_all_brushes:
        #        brushes = [br for br in brushes if br.use_paint_sculpt]
        items.sort(key=lambda item: item.fav, reverse=True) # Favs first.
        return items

    def draw_poll(self, context, cv: Canvas) -> bool:
        return cv.shelf.expand and cv.shelf.size.y > self.slot_size

    def get_draw_item_args(self, context, cv: Canvas, scale: float, prefs: SCULPTPLUS_AddonPreferences) -> tuple:
        # brushes = context.scene.sculpt_hotbar.get_brushes()
        act_cat_id = Props.GetActiveCat(self.type)
        if act_cat_id is None:
            return None
        slot_color = Vector(prefs.theme_shelf_slot)
        # if not brushes:
        #     return slot_color, None
        #brush_idx_rel: dict = {brush: idx for idx, brush in enumerate(brushes)}
        #return brush_idx_rel, slot_color, act_cat_id
        act_item = Props.GetActiveBrush() if self.type == 'BRUSH' else Props.GetActiveTexture()
        return slot_color, act_cat_id.id, act_item.id if act_item else None, Props.GetHotbarBrushIds()

    def draw_item(self,
                  slot_p: Vector, slot_s: Vector,
                  item: Union[Brush, Texture], #brush_idx_rel: dict,
                  is_hovered: bool,
                  slot_color: Vector,
                  act_cat_id: str,
                  act_item: str,
                  hotbar_ids: List[str],
                  scale: float,
                  prefs: SCULPTPLUS_AddonPreferences):
        
        is_active = item.id == act_item
        is_selected = item == self.selected_item

        #if brush is None or brush_idx_rel is None:
        #    return
        DiRct(slot_p, slot_s, slot_color)
        if is_hovered:
            DiRct(slot_p, slot_s, Vector(prefs.theme_hotbar_slot)+Vector((.2, .2, .2, 0))) # (.6,.6,.6,.25))

        def draw_preview_fallback(p, s, act):
            if self.type == 'BRUSH':
                DiBr(p, s, item.sculpt_tool, act)
            else:
                DiRct(p, s, Vector(prefs.theme_shelf_slot)*.8)

        item.draw_preview(
            slot_p,
            slot_s,
            is_hovered,
            fallback=draw_preview_fallback
        )

        #if brush_idx_rel is not None and brush in brush_idx_rel:
        #    idx: int = brush_idx_rel[brush]
        #    idx = idx+1 if idx!=9 else 0
        #    DiText(slot_p+Vector((1,3)), str(idx), 12, scale)
        if self.type == 'BRUSH':
            if item.id in hotbar_ids:
                DiText(slot_p+Vector((1,3)), str(hotbar_ids.index(item.id)), 12, scale)

        cat_id = item.cat_id
        if cat_id == act_cat_id:
            DiTriCorner(slot_p+Vector((.5, slot_s.y-.5)), slot_s.x/5, 'TOP_LEFT', (1, 0.212, 0.48, .9))

        if item.fav:
            size = 16 * scale
            margin = size/2
            DiStar(slot_p+slot_s-Vector((margin, margin)), size)

        if is_active:
            DiCage(slot_p, slot_s, 2.4*scale, prefs.theme_active_slot_color)
        if is_selected:
            DiCage(slot_p, slot_s, 2.4*scale, prefs.theme_selected_slot_color) #(.2, .6, 1.0, 1.0))
        if not is_active and not is_selected:
            DiCage(slot_p, slot_s, 2.4*scale, slot_color*1.3)

    def draw_post(self, _context, cv: Canvas, mouse: Vector, scale: float, _prefs: SCULPTPLUS_AddonPreferences):
        if cv.active_ctx_widget:
            DiText(self.pos, '.', 1, scale)
            DiRct(self.pos, self.size, (.24, .24, .24, .64))
        else:
            super().draw_post(_context, cv, mouse, scale, _prefs)

    #def draw(self, context, cv: Canvas, mouse: Vector, scale: float, prefs: SCULPTPLUS_AddonPreferences):
    #    DiRct(self.pos, self.size, (.2, .6, .9, .8))
    #    super().draw(context, cv, mouse, scale, prefs)


class ShelfDragHandle(WidgetBase):
    modal_trigger: Set[str] = {'LEFTMOUSE'}
    msg_on_enter: str = "Click, or Press & Drag up/down to expand or hide"

    def init(self) -> None:
        self.start_mouse = Vector((0, 0))
        self.end_mouse   = Vector((0, 0))
        self.tx_pos = Vector((0, 0))
        self.dragging = False

    def update(self, cv: Canvas, prefs: SCULPTPLUS_AddonPreferences) -> None:
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

        cv.shelf_drag.update(cv, None)
        cv.shelf_search.update(cv, None)
        cv.shelf_sidebar_actions.update(cv, None)
        cv.shelf_sidebar.update(cv, None)
        cv.shelf_ctx_switcher.update(cv, None)
        cv.shelf_grid_item_info.update(cv, None)

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

    def draw(self, context, cv: Canvas, mouse: Vector, scale: float, prefs: SCULPTPLUS_AddonPreferences):
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
        self._expand = False

    @property
    def expand(self):
        return self._expand

    @expand.setter
    def expand(self, state: bool):
        def _update():
            self.cv.refresh()

        if state == False:
            self._expand = False
            self.resize(x=self.size.y, animate=True, anim_change_callback=_update)
        else:
            def _enable():
                self._expand = True
            self.resize(x=self.cv.shelf_grid.size.x, animate=True, anim_change_callback=_update, anim_finish_callback=_enable)

    def on_hover(self, m: Vector, p: Vector = None, s: Vector = None) -> bool:
        return super().on_hover(m, p, s) and self.cv.shelf.expand

    def update(self, cv: Canvas, prefs: SCULPTPLUS_AddonPreferences) -> None:
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

    def draw(self, context, cv: Canvas, mouse: Vector, scale: float, prefs: SCULPTPLUS_AddonPreferences):
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
                DiIcoCol(p, s, Icon.SEARCH, (.9, .9, .9, .9))
            else:
                DiIcoCol(p, s, Icon.SEARCH, (.9, .9, .9, .6))

    def on_left_click(self, ctx, cv: Canvas, m: Vector) -> bool:
        return True

    def modal_enter(self, ctx, cv: Canvas, m: Vector) -> None:
        self.expand = True

    def modal_exit(self, ctx, cv: Canvas, m: Vector, cancel: bool = False) -> None:
        self.expand = False

        if self.modal_cancel or cancel:
            self.modal_cancel = False
            self.search = ''

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


class ShelfGridItemInfo(WidgetBase):
    def init(self) -> None:
        self._expand = False
        self.max_width = 1
        self._anim_running = False

    @property
    def expand(self) -> bool:
        return self._expand

    @expand.setter
    def expand(self, value: bool) -> None:
        cv = self.cv
        def _update():
            self.cv.refresh()
            # self.update(cv, None)
            cv.shelf_grid.update(cv, None)

        if value:
            self._expand = True

            def _enable():
                self._anim_running = False
                self.update(cv, None)
                #self.enabled = True

            #self._anim_running = True
            self.resize(self.max_width, animate=True, anim_change_callback=_update, anim_finish_callback=_enable)
            #cv.shelf_grid.resize(cv.shelf_grid.size.x - 120, animate=True, anim_finish_callback=_enable, anim_change_callback=_update)
        else:
            def _disable():
                self._anim_running = False
                self._expand = False
                self.update(cv, None)
                #self.enabled = False

            self._anim_running = True
            self.resize(0, animate=True, anim_change_callback=_update, anim_finish_callback=_disable)
            #cv.shelf_grid.resize(cv.shelf_grid.size.x + 120, animate=True, anim_finish_callback=_disable, anim_change_callback=_update)

    def poll(self, _context, cv: Canvas) -> bool:
        return self.expand and cv.shelf.expand and self.size.y > 10

    def update(self, cv: Canvas, prefs: SCULPTPLUS_AddonPreferences) -> None:
        if not self.expand and not self.anim_running():
            self.pos = cv.shelf_grid.pos.copy()
            self.size = Vector((0, cv.shelf_grid.size.y))
            return
        scale = cv.scale

        p = self.cv.shelf.pos.copy()
        p.x += (6 * scale)
        p.y += (6 * scale)
        self.pos = p
        self.size = Vector((
            self.size.x,
            cv.shelf_grid.size.y
        ))

        self.max_width = self.cv.hotbar.size.x*.215

    def draw(self, context, cv: Canvas, mouse: Vector, scale: float, prefs: SCULPTPLUS_AddonPreferences):
        #return super().draw(context, cv, mouse, scale, prefs)
        DiText(self.pos, '.', 1, 1, (0.1, 0.1, 0.1, 1))

        opacity = min(max(self.size.x / self.max_width, 0), 1)
        opacity = ease_quad_in_out(-.25, 1, opacity)
        #print("opacity:", opacity)
        #print(self.size.x, self.max_width)
        mar = 6 * scale * 2
        pad = 5 * scale
        inner_pos = self.pos.copy()

        if self._anim_running:
            inner_size = Vector((self.max_width - mar, self.size.y)) # Vector((max(self.size.x - mar, (self.max_width - mar) * .32), self.size.y))
        else:
            inner_size = self.size.copy() - Vector((mar, 0))

        DiRct(self.pos, inner_size, (.04, .04, .04, .32 * opacity))

        DiLine(
            inner_pos + Vector((inner_size.x, 0)),
            inner_pos + inner_size,
            2.4,
            (.5, .5, .5, .64 * opacity)
        )
        DiLine(
            inner_pos + Vector((inner_size.x, 0)),
            inner_pos + inner_size,
            1.2,
            (.1, .1, .1, .64 * opacity)
        )

        act_brush = Props.GetActiveBrush()
        # if act_item is None:
        #     return

        inner_size -= Vector((mar + pad*2, pad*2))

        line_height = get_text_dim('O', 12, scale)[1] + mar
        item_height = (inner_size.y - line_height * 2 - mar * 2) / 2
        if item_height > inner_size.x:
            item_height = inner_size.x

        item_size = Vector((item_height, item_height))
        item_pos = self.get_pos_by_relative_point(Vector((0, 1))) - Vector((0, item_size.x))
        item_pos += Vector((pad, -pad))

        # DRAW BRUSH PREVIEW.
        def draw_preview_fallback(p, s, act):
            DiBr(p, s, act_brush.sculpt_tool, act, opacity)

        if act_brush:
            act_brush.draw_preview(
                item_pos,
                item_size,
                False,
                fallback=draw_preview_fallback,
                opacity=opacity
            )
            label = act_brush.name

        else:
            DiRct(item_pos, item_size, (.05, .05, .05, .4 * opacity))
            DiCage(item_pos, item_size, 1.5, (.05, .05, .65 * opacity))
            DiIcoCol(item_pos + Vector((pad, pad)), item_size - Vector((pad, pad)) * 2, Icon.PAINT_BRUSH, (.8, .8, .8, 1 * opacity))
            label = "No Active Brush"

        item_pos -= Vector((0, line_height))
        DiText(item_pos, label, 12, scale, (.92, .92, .92, opacity))

        # DRAW TEXTURE PREVIEW.
        item_pos -= Vector((0, item_height + mar * 2))

        def draw_preview_fallback(p, s, act):
            DiIcoOpGamHl(p, s, Icon.TEXTURE, opacity)

        # item_pos = inner_pos
        act_texture = Props.GetActiveTexture()
        if act_texture: # act_brush and act_brush.texture_id and (act_texture := Props.GetTexture(act_brush.texture_id)):
            label = act_texture.name
            act_texture.draw_preview(item_pos, item_size, False, fallback=draw_preview_fallback, opacity=opacity)
        else:
            label = "No Texture"
            draw_preview_fallback(item_pos, item_size, False)

        item_pos -= Vector((0, line_height))
        DiText(item_pos, label, 12, scale, (.92, .92, .92, opacity))
