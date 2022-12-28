import bpy
from gpu.types import Buffer, GPUTexture
from bpy.types import Brush, Image, Camera, Context
from pathlib import Path
from time import sleep, time
from os import path
from mathutils import Vector, Matrix
from threading import Thread
from typing import Union, Dict, Tuple
from .get_image_size import get_image_size
import imbuf
import gpu
from imbuf.types import ImBuf
from sculpt_plus.path import data_brush_dir, SculptPlusPaths
from sculpt_plus.lib import BrushIcon, Icon
import numpy as np
from gpu_extras.presets import draw_texture_2d


cache_tex: Dict[str, GPUTexture] = {}

def load_image_and_scale(filepath: str, size: Tuple[int, int] = (128, 128)) -> Image:
    if not path.exists(filepath):
        return None
    image: Image = bpy.data.images.load(filepath, check_existing=True)
    image.scale(*size)
    return image

def get_nparray_from_image(image: Image) -> np.ndarray:
    px_count: int = len(image.pixels)
    pixels = np.empty(shape=px_count, dtype=np.float32)
    image.pixels.foreach_get(pixels)
    return pixels

def resize_and_save_brush_icon(brush: Brush, size: Tuple[int, int] = (128, 128), output: Union[str, None] = None) -> str:
    """ Resize and save the brush icon.
        Args:
            brush (Brush): The brush to resize and save.
    """
    if not path.exists(brush.icon_filepath):
        return
    image_buffer: ImBuf = imbuf.load(brush.icon_filepath)
    image_buffer.resize(size, method='BILINEAR')
    save_path = str(data_brush_dir / 'br_icon' / (brush['id'] + '.png'))
    imbuf.save(image_buffer, filepath=save_path)
    image_buffer.free()
    brush.icon_filepath = save_path
    return save_path

def get_ui_image_tex(icon: Union[Icon, str]) -> Union[GPUTexture, None]:
    if isinstance(icon, str):
        icon = getattr(Icon, icon, None)
    if icon is None:
        return None
    return gputex_from_image_file(
        SculptPlusPaths.SRC_LIB_IMAGES('icons', icon.value + '.png'),
        idname='Icon.' + icon.name)

def get_brush_type_tex(brush: Union[Brush, str]) -> GPUTexture:
    sculpt_tool: str = brush if isinstance(brush, str) else brush.sculpt_tool.upper()
    brush_icon = getattr(BrushIcon, sculpt_tool, BrushIcon.DEFAULT)
    return gputex_from_image_file(
        SculptPlusPaths.SRC_LIB_IMAGES('brushes', brush_icon.value + '.png'),
        idname='BrushIcon.' + brush_icon.name)

def get_brush_tex(brush: Union[Brush, str]) -> GPUTexture:
    if isinstance(brush, str):
        return get_brush_type_tex(brush)
    if not brush.use_custom_icon:
        return get_brush_type_tex(brush)
    icon_path: str = brush.icon_filepath
    if not icon_path:
        return get_brush_type_tex(brush)
    if not path.exists(icon_path):
        return get_brush_type_tex(brush)
    width, height = get_image_size(icon_path)
    if width > 128 or height > 128:
        resize_and_save_brush_icon(brush)
    return gputex_from_image_file(icon_path, idname=brush['sculpt_plus_id'])

def gputex_from_image_file(filepath: str, size: Tuple[int, int] = (128, 128), idname: Union[str, None] = None, get_pixels: bool = False) -> GPUTexture:
    """
    Loads an image as  GPUTexture type from a file.

    Args:
        filepath (str): Path to the image file.
    """
    if idname is None:
        idname: str = filepath

    gputex: GPUTexture = cache_tex.get(idname, None)
    if gputex is not None:
        if get_pixels:
            return gputex, None
        return gputex

    img: Image = load_image_and_scale(filepath, size)
    if img is None:
        if get_pixels:
            return None, None
        return None
    px: np.ndarray = get_nparray_from_image(img)

    buff: Buffer = Buffer(
        'FLOAT',
        len(img.pixels),
        px
    )

    gputex: GPUTexture = GPUTexture(
        size,
        layers=0,
        is_cubemap=False,
        format='RGBA16F',
        data=buff
    )

    bpy.data.images.remove(img)
    del img

    cache_tex[idname] = gputex
    if get_pixels:
        return gputex, px

    return gputex


class OffscreenBuffer(object):
    _instance = None

    @classmethod
    def get(cls) -> 'OffscreenBuffer':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._context = None
        self._offscreen = None
        self.width, self.height = 0, 0
        self._needs_redraw = False
        self._is_redrawing = False
        self._thread = None

    @property
    def needs_redraw(self):
        return self._needs_redraw

    @needs_redraw.setter
    def needs_redraw(self, value):
        value, ctx = value
        self._needs_redraw = value
        if not self._is_redrawing and self._thread is None and value == True:
            #self._thread = Thread(name="OffscreenBuffer", target=self.redraw, daemon=True, args=(ctx,))
            #self._thread.start()
            self.redraw(ctx)

    def redraw(self, ctx):
        while 1:
            #window = bpy.context.window_manager.windows[0]
            #with ctx.temp_override(window=ctx.window, area=ctx.area, region=ctx.region):
            print("Start redraw")
            self._needs_redraw = False
            self._is_redrawing = True

            reg_width = ctx.region.width
            reg_height = ctx.region.height

            cv = bpy.sculpt_hotbar._cv_instance

            #if master := getattr(bpy, 'sculpt_hotbar', None):
            #    print(master)
            #    if hasattr(master, 'cv'):
            #        print(master.cv)
            if cv is None:
                sleep(0.1)
                continue

            #gpu.state.viewport_set(0, 0, reg_width, reg_height)

            # get currently bound framebuffer
            #framebuffer = gpu.state.active_framebuffer_get()
            #framebuffer.bind()
            #framebuffer.clear(color=(0.0, 0.0, 0.0, 0.0))

            # get information on current viewport
            viewport_info = gpu.state.viewport_get()
            width = viewport_info[2]
            height = viewport_info[3]
            #print(width, height)


            #with gpu.matrix.push_pop():
            #    gpu.matrix.load_matrix(Matrix.Identity(4))
            offscreen = gpu.types.GPUOffScreen(width, height)
            with offscreen.bind():
                cv.draw(ctx)
            self._offscreen = offscreen

            self.width = width
            self.height = height

            ctx.region.tag_redraw()

            self._is_redrawing = False
            print("End redraw")
            if not self.needs_redraw:
                break

    @classmethod
    def tag_redraw(cls, ctx):
        return
        cls.get().needs_redraw = True, ctx

    @classmethod
    def draw(cls, ctx):
        cv = bpy.sculpt_hotbar._cv_instance
        if cv: cv.draw(ctx)
        return

        off_buffer = OffscreenBuffer.get()

        if getattr(bpy, 'sculpt_hotbar', None) is None:
            return

        from sculpt_plus.sculpt_hotbar.di import DiIma

        reg_width = ctx.region.width
        reg_height = ctx.region.height

        print("off size:", off_buffer.width, off_buffer.height)

        if off_buffer._offscreen is not None:
            viewport_info = gpu.state.viewport_get()
            width = viewport_info[2]
            height = viewport_info[3]
            DiIma(Vector((0, 0)), Vector((width, height)), off_buffer._offscreen.texture_color)

        if off_buffer._is_redrawing or off_buffer.needs_redraw:
            #if off_buffer._offscreen is not None:
            #    DiIma(Vector((0, 0)), Vector((reg_width, reg_height)), off_buffer._offscreen.texture_color)
            #    print("ok")
            print("redrawing...")
            return

        if off_buffer._offscreen is None or reg_width != off_buffer.width or reg_height != off_buffer.height:
            off_buffer.needs_redraw = True, ctx

        print("Hello, world!")


# TODO: Run this in a separate thread, pass the redraw signals through some queue object or something to that thread.


# LIVE VIEW

def get_cam_matrices(ctx: Context, camera: Camera, w: int = 256, h: int = 256) -> Tuple[Matrix, Matrix]:
    return camera.matrix_world.inverted(), camera.calc_matrix_camera(ctx.evaluated_depsgraph_get(), x=w, y=h, scale_x=1, scale_y=1)

def get_view_cam_matrices(ctx: Context, w: int = 256, h: int = 256):
    return ctx.space_data.region_3d.view_matrix, ctx.scene.camera.calc_matrix_camera(ctx.evaluated_depsgraph_get(), x=w, y=h, scale_x=1.0, scale_y=1.0)

shading_props = {
    'light' : 'FLAT',
    'background_type' : 'VIEWPORT',
    'background_color' : (0.0, 0.0, 0.0),
    'color_type' : 'SINGLE',
    'single_color' : (1.0, 1.0, 1.0),
    'show_xray' : False,
    'show_shadows' : False,
    'show_cavity' : False,
    'show_specular_highlight' : False,
    'use_dof' : False,
}

class LiveView(object):
    _instance = None

    @classmethod
    def get(cls) -> 'LiveView':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.scale = 1.0
        WIDTH = 256
        HEIGHT = 160
        self.width = int(WIDTH * self.scale)
        self.height = int(HEIGHT * self.scale)
        self.offscreen: gpu.types.GPUOffScreen = gpu.types.GPUOffScreen(WIDTH, HEIGHT)
        self.buffer: gpu.types.Buffer #= self.offscreen.texture_color.read()
        self.icon_id = None
        self.timer = time()
        self._draw_handler = None
        self.region_id = None

    def start_handler(self, context):
        if self._draw_handler:
            return
        self.region_id = context.region.as_pointer()
        self._draw_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw_px, (context,), 'WINDOW', 'POST_PIXEL')

    def stop_handler(self):
        if self._draw_handler:
            bpy.types.SpaceView3D.draw_handler_remove(self._draw_handler, 'WINDOW')
            self._draw_handler = None

    def draw_px(self, context: bpy.types.Context):
        if not context.region or self.region_id != context.region.as_pointer():
            return

        def _draw():
            gpu.state.depth_mask_set(False)
            draw_texture_2d(self.offscreen.texture_color, (10, 10), self.width, self.height)

        if (time() - self.timer) < 1.2:
            _draw()
            return

        self.timer = time()

        #scene = context.scene
        #view_matrix = scene.camera.matrix_world.inverted()
        #projection_matrix = scene.camera.calc_matrix_camera(context.evaluated_depsgraph_get(), x=self.width, y=self.height)
        # Backup. # We want to hide overlays and gizmos for any configuration we have.
        space = context.space_data
        shading = space.shading

        show_overlays   = space.overlay.show_overlays
        show_gizmo      = space.show_gizmo
        space.overlay.show_overlays = False
        space.show_gizmo            = False

        # Shading settings...
        backup_props = {}
        for key, value in shading_props.items():
            backup_props[key] = getattr(shading, key)
            setattr(shading, key, value)

        # mat = get_view_cam_matrices(context, self.width, self.height)
        self.offscreen.draw_view3d(
            context.scene,
            context.view_layer,
            space,
            context.region,
            space.region_3d.view_matrix,
            context.scene.camera.calc_matrix_camera(context.evaluated_depsgraph_get(), x=self.width, y=self.height, scale_x=1.0, scale_y=1.0))
        
        _draw()

        # Return to original settings.
        space.overlay.show_overlays     = show_overlays
        space.show_gizmo                = show_gizmo

        for key, value in backup_props.items():
            setattr(shading, key, value)

        # self.buffer = self.offscreen.texture_color.read()

    def refresh(self, context=None):
        if self.buffer is None:
            return None
        if self.offscreen is None:
            return None
        context = context if context else bpy.context
        pixels = np.array(self.buffer.to_list()).reshape(self.width * self.height, 4)
        preview = context.sculpt_object.preview
        if preview is None:
            preview = context.sculpt_object.preview_ensure()
        preview.icon_size = self.width, self.height
        preview.icon_pixels_float.foreach_set(pixels)
        self.icon_id = preview.icon_id

        return 5

    def draw_template(self, context: Context, layout: bpy.types.UILayout, scale: float = 1.0):
        if not self.offscreen:
            return
        if self.icon_id is not None:
            layout.box().template_icon(self.icon_id, scale=scale)
        with self.offscreen.bind():
            layout.box().template_icon(self.offscreen.color_texture, scale=scale)
