from math import floor, ceil
import bpy
from bpy.types import Brush, Texture, ImageTexture, Image
from mathutils import Vector
from gpu.types import GPUTexture
from typing import Union
from os.path import exists, isfile
import numpy as np
import PIL
from pathlib import Path

from uuid import uuid4

from sculpt_plus.sculpt_hotbar.canvas import Canvas
from sculpt_plus.sculpt_hotbar.di import DiLine, DiText
from sculpt_plus.prefs import SCULPTPLUS_AddonPreferences
from sculpt_plus.utils.cursor import Cursor, CursorIcon
from sculpt_plus.utils.math import clamp
from sculpt_plus.utils.gpu import gputex_from_image_file, get_brush_type_tex, gputex_from_pixels
from .wg_base import WidgetBase
from sculpt_plus.management.types.brush_props import sculpt_tool_items


sculpt_tool_items_set = set(sculpt_tool_items)


HEADER_HEIGHT = 32


COMPATIBLE_IMAGE_EXTENSIONS = {'PNG', 'JPG', 'JPEG', 'TGA', 'TIFF', 'TIF', 'PSD'}
def _verify_image_path(filepath: str) -> Path or None:
    image_path = Path(filepath)
    if not image_path.exists() or not image_path.is_file():
        return None
    format = image_path.suffix[1:].upper()
    if format not in COMPATIBLE_IMAGE_EXTENSIONS:
        return None
    return format


class FakeViewItemThumbnail:
    # TODO: ADD CLASSMETHOD TO CREATE NEW FROM FILEPATH, WHICH WILL GENERATE THE THUMBNAIL TO TEMP FAKE ITEMS FOLDER.

    # gputex: GPUTexture
    pixels: np.ndarray
    size: tuple[int, int]
    filepath: str

    def __init__(self, idname: str, filepath: str, size: tuple[int, int] = (100, 100), pixels = None):
        self.id = idname
        self.pixels = pixels
        self.size = size
        self.filepath = filepath

    def load_gputex(self) -> GPUTexture:
        if self.pixels:
            return gputex_from_pixels(self.size, self.id, self.pixels)
        elif self.filepath:
            gputex, pixels = gputex_from_image_file(self.filepath, self.size, self.id)
            if pixels:
                self.pixels = pixels
            return gputex
        return None # DEFAULT Icon

    def draw(self, p, s) -> None:
        if gputex := self.load_gputex():
            pass


class FakeViewItem:
    id: str
    name: str
    icon: FakeViewItemThumbnail

    def __init__(self, name: str = '', icon_filepath: str = '', icon_size: tuple = (100, 100), icon_pixels = None, id: str = None) -> None:
        self.id = id if id else uuid4().hex
        self.name = name
        if icon_filepath or icon_pixels:
            self.icon = FakeViewItemThumbnail(self.id, icon_filepath, icon_size, icon_pixels)
        else:
            self.icon = None

    def draw(self, p, s):
        if self.icon:
            self.icon.draw(p, s)
        else:
            self.draw_default(p, s)

    def draw_default(self, p, s):
        ''' To be overrided in subclasses. '''
        pass

    def set_icon(self, filepath: str, size: tuple[int, int] = (100, 100), pixels = None) -> Union['FakeViewItem_Brush', 'FakeViewItem_Texture']:
        self.icon = FakeViewItemThumbnail(self.id, filepath, size, pixels)
        return self

    def come_true(self) -> None:
        ''' Turn fake item into a real item! Save thumbnail and image, brush info...
            whatever info in corresponding folder and database. '''
        pass


class FakeViewItem_Texture(FakeViewItem):
    @classmethod
    def from_bl_image(cls, image: Image, generate_thumbnail: bool = True):
        image['id'] = uuid4().hex
        fake_texture = cls(
            name=image.name,
            id=image['id'],
            # icon_filepath=image.filepath_from_user(),
            # icon_size=image.size,
        )
        if generate_thumbnail:
            from sculpt_plus.path import SculptPlusPaths
            from sculpt_plus.props import Props
            filepath: str = SculptPlusPaths.TEMP_FAKE_ITEMS(image['id'] + '.jpg')
            base_thumb_image = Props.get_temp_thumbnail_image()
            thumb_image: Image = base_thumb_image.copy()
            thumb_image.scale(100, 100)
            thumb_image.filepath_raw = filepath
            thumb_image.save()
            thumb_pixels = np.empty(40000, dtype=np.float32)
            thumb_image.pixels.foreach_get(thumb_pixels)
            # image.save_render(filepath, quality=75)
            fake_texture.set_icon(filepath, size=(100, 100), pixels=thumb_pixels)
            bpy.data.images.remove(thumb_image)
        #else:
        #    fake_texture.set_icon(filepath, size=image.size)
        return fake_texture

class FakeViewItem_Brush(FakeViewItem):
    use_custom_icon: bool
    sculpt_tool: str

    @classmethod
    def from_bl_brush(cls, brush: Brush, generate_thumbnail: bool = True, generate_tex_thumbnail: bool = True):
        brush['id'] = uuid4().hex
        fake_brush = cls(
            name=brush.name,
            sculpt_tool=brush.sculpt_tool,
            id=brush['id']
        )
        if brush.use_custom_icon:
            if generate_thumbnail:
                from sculpt_plus.path import SculptPlusPaths
                filepath: str = SculptPlusPaths.TEMP_FAKE_ITEMS(brush['id'] + '.jpg')
                fake_brush.generate_from_filepath(
                    brush.icon_filepath,
                    filepath,
                    'JPEG'
                 )
            else:
                fake_brush.set_icon(
                    filepath=brush.icon_filepath,
                )
        if texture := brush.texture:
            if isinstance(texture, ImageTexture) and (image := texture.image):
                if image.type == 'IMAGE' and image.source in {'FILE', 'SEQUENCE'} and len(image.pixels) > 0:
                    fake_brush.set_texture(
                        FakeViewItem_Texture.from_bl_image(image, generate_thumbnail=generate_tex_thumbnail)
                    )
        return fake_brush

    def generate_from_filepath(self, filepath, output, format: str = 'JPEG'):
        image = PIL.Image.open(filepath)
        image.thumbnail((100, 100), resample=PIL.Image.Resampling.NEAREST)
        image = image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        thumb_pixels = np.array(image, dtype=np.float32).reshape(40000) / 255
        if format == 'JPEG':
            image.save(output, format=format, optimize=True, quality=80)
        else:
            image.save(output, format=format)
        self.set_icon(output, size=(100, 100), pixels=thumb_pixels)
        image.close()
        del image

    def __init__(self, name: str = '', sculpt_tool: str = 'DRAW', id: str = None): # icon_filepath: str = '', icon_size: tuple = (100, 100), icon_pixels = None, texture_data: dict = None) -> None:
        self.use_custom_icon = False # icon_filepath not in sculpt_tool_items_set
        self.sculpt_tool = sculpt_tool
        self.texture = None
        super().__init__(name, id=id)
        # print("pixels:", icon_pixels)
        '''
        super().__init__(name, icon_filepath, icon_size, icon_pixels)
        if texture_data:
            self.texture = FakeViewItem_Texture(**texture_data)
        else:
            self.texture = None
        '''

    def set_icon(self, filepath: str, size: tuple[int, int] = (100, 100), pixels=None) -> Union['FakeViewItem_Brush', 'FakeViewItem_Texture']:
        if exists(filepath) and isfile(filepath):
            self.use_custom_icon = True
        super().set_icon(filepath, size, pixels)

    def load_icon(self):
        if self.use_custom_icon:
            super().load_icon()
        else:
            self.icon = get_brush_type_tex(self.icon_filepath)

    def set_texture(self, fake_texture: FakeViewItem_Texture) -> 'FakeViewItem_Brush':
        self.texture = fake_texture
        return self

    def new_texture(self, name: str = '', icon_filepath: str = '', icon_size: tuple = (100, 100), icon_pixels = None, id: str = None):
        fake_texture = FakeViewItem_Texture(
            name=name,
            icon_filepath=icon_filepath,
            icon_size=icon_size,
            icon_pixels=icon_pixels,
            id=id
        )
        self.set_texture(fake_texture)
        return fake_texture


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
        # NOTE: this update is broken LOL.
        if prefs:
            self.use_smooth_scroll = prefs.use_smooth_scroll

        # GET DATA TO FILL THE SLOTS BELOW.
        data = self.get_data(self.cv)
        if not data:
            return

        item_height: float = self.grid_slot_size
        item_width: float = self.size.x
        self.item_size: Vector = Vector((item_width, item_height))

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

        #if self.scroll_axis == 'Y':
        #    s.x = self.get_max_width(self.cv, scale)

        rows = max(floor(s.y / slot_size), 1)
        cols = max(floor(s.x / slot_size), 1)

        #print("Size:", s.x, s.y)
        #print("Rows/Cols:", rows, cols)

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

            if mouse and hovered_item is None and WidgetBase.check_hover(None, mouse, slot_p, slot_s):
                hovered_item = item

            if loop_callback:
                loop_callback(slot_p, slot_s, item, item==hovered_item)

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

    def draw_item(self, slot_p, slot_s, item, is_hovered: bool, scale: float, prefs: SCULPTPLUS_AddonPreferences):
        pass

    def draw_poll(self, context, cv: Canvas) -> bool:
        return True

    def get_draw_item_args(self, context, cv: Canvas, scale: float, prefs: SCULPTPLUS_AddonPreferences) -> tuple:
        return ()

    def draw(self, context, cv: Canvas, mouse: Vector, scale: float, prefs: SCULPTPLUS_AddonPreferences):
        item_args = self.get_draw_item_args(context, cv, scale, prefs)
        if not item_args:
            return
        def _draw(*args):
            self.draw_item(*args, *item_args, scale, prefs)
        self.iter_slots(scale, mouse, loop_callback=_draw)

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
        self.item_pos: list[Vector] = []
        self.visible_range: tuple[int, int] = None
        self.view_height = 0
        self.data_count: int = 0

    def get_view_margins_vertical(self) -> tuple:
        ''' 0 -> Bottom margin;
            1 -> Top margin; '''
        return (0, 0)

    def update(self, cv: Canvas, prefs: SCULPTPLUS_AddonPreferences):
        # super().update(cv, prefs)

        width, height = self.size.x, self.size.y

        item_width: int = width
        item_height: int = int(item_width * self.item_aspect_ratio)
        self.item_size = Vector((item_width, item_height)) # * cv.scale

        data = self.get_data(cv)
        # print(data)
        item_count: int = len(data)
        self.data_count = item_count
        if item_count == 0:
            self.tot_scroll = 0 # Max Scroll.
            self.item_pos = None
            self.visible_range = None
            self.view_height = 0
            return

        tot_rows: int = item_count
        visible_rows: float = height / item_height
        hidden_rows: float = tot_rows - visible_rows
        view_height: float = tot_rows * item_height
        self.view_height = view_height
        self.tot_scroll = view_height - height

        first_visible_row = floor(abs(self.scroll) / item_height)
        last_visible_row = ceil(first_visible_row + visible_rows)
        self.visible_range: tuple[int, int] = (
            max(first_visible_row, 0),
            min(last_visible_row, tot_rows) + 1
        )

        x: float = self.pos.x
        y: float = self.pos.y + self.size.y - item_height
        y += self.scroll # (self.scroll - hidden_rows)

        # visible_rows = ceil(visible_rows)
        # self.item_pos = [Vector((0, 0))] * visible_rows
        # for i in range(visible_rows):
        #    self.item_pos[i] = Vector((x, y))
        #    y -= item_height

        self.item_pos = [Vector((x, y - item_height * i)) for i in range(item_count)]

        #print("visible_rows:", visible_rows)
        #print("first_visible_row:", first_visible_row)
        #print("last_visible_row:", last_visible_row)
        #print("scroll:", self.scroll)
        #print("view_height:", view_height)

    def on_left_click_drag(self, ctx, cv: Canvas, m: Vector) -> bool:
        return self.view_height > self.size.y

    def do_scroll(self, cv, off_y: float, anim: bool = False):
        if self.view_height > self.size.y:
            super().do_scroll(cv, off_y, anim)
            # self.update(cv, None)

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
        m_y = mouse.y
        item_size = self.item_size
        hovered_item = None
        visible_items = self.get_visible_items(self.cv)
        #print("visible items:", visible_items)
        if not visible_items:
            return None
        visible_item_pos = self.item_pos[self.visible_range[0]: self.visible_range[1]]
        mouse_y_ok = (m_y >= self.pos.y) and (m_y <= (self.pos.y + self.size.y))
        for (item, item_pos) in zip(visible_items, visible_item_pos):
            #print(item, item_pos)
            if self._is_on_hover and mouse_y_ok and hovered_item is None and super().on_hover(mouse, item_pos, item_size):
                hovered_item = item
            if loop_callback is not None:
                loop_callback(item_pos, item_size, item, item==hovered_item)

        return hovered_item

    def get_visible_items(self, cv: Canvas) -> list:
        if self.visible_range is None:
            return []
        data = self.get_data(cv)
        item_count: int = len(data)
        if self.data_count != item_count:
            self.update(cv, None)
        if self.visible_range is None:
            return []
        return data[self.visible_range[0]: self.visible_range[1]]
