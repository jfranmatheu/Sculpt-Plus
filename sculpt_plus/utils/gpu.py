import bpy
from gpu.types import Buffer, GPUTexture
from bpy.types import Brush, Image, Camera, Context
from pathlib import Path
from math import sqrt
from time import sleep, time
from os import path
from mathutils import Vector, Matrix
from threading import Thread
from typing import Union, Dict, Tuple
from .get_image_size import get_image_size
import imbuf
import gpu
from imbuf.types import ImBuf
from ..path import data_brush_dir, SculptPlusPaths
from ..lib import BrushIcon, Icon
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
    save_path = str(data_brush_dir / 'br_icon' / (brush['uuid'] + '.png'))
    imbuf.save(image_buffer, filepath=save_path)
    image_buffer.free()
    brush.icon_filepath = save_path
    return save_path

def get_ui_image_tex(icon: Union[Icon, str]) -> Union[GPUTexture, None]:
    if isinstance(icon, GPUTexture):
        return icon
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
        print("[Sculpt+] Error! gputex_from_image_file() -> loaded image is null!")
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

def gputex_from_pixels(size: Tuple[int, int], idname: Union[str, None], pixels: np.ndarray) -> GPUTexture:
    """
    Loads an image as  GPUTexture type from a file.

    Args:
        filepath (str): Path to the image file.
    """
    gputex: GPUTexture = cache_tex.get(idname, None)
    if gputex is not None:
        return gputex

    #pixels_size: int = len(pixels)

    buff: Buffer = Buffer(
        'FLOAT',
        size[0]*size[1]*4,
        pixels
    )

    #_size =  sqrt(pixels_size / 4)
    #_size = int(_size)
    #if size[0] != _size or size[1] != _size:
    #    print(f"WTF! Size mismatch! ({size}) vs ({(_size, _size)}).")
    #    size = (_size, _size)

    gputex: GPUTexture = GPUTexture(
        size,
        layers=0,
        is_cubemap=False,
        format='RGBA16F',
        data=buff
    )

    cache_tex[idname] = gputex
    return gputex


def unregister():
    for gputex in cache_tex.values():
        del gputex
    cache_tex.clear()
