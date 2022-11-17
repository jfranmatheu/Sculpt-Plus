import bpy
from gpu.types import Buffer, GPUTexture
from bpy.types import Brush, Image
from pathlib import Path
from os import path
from typing import Union, Dict, Tuple
from .get_image_size import get_image_size
import imbuf
from imbuf.types import ImBuf
from sculpt_plus.path import brush_sets_dir, SculptPlusPaths
from sculpt_plus.lib import BrushIcon, Icon
import numpy as np

cache_text: Dict[str, GPUTexture] = {}

def load_image_and_scale(filepath: str, size: Tuple[int, int] = (128, 128)) -> Image:
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
    save_path = str(brush_sets_dir / 'br_icon' / (brush['id'] + '.png'))
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
        SculptPlusPaths.SRC_LIB_IMAGES('icons', icon + '.png'),
        idname='Icon.' + icon.name)

def get_brush_type_tex(brush: Brush) -> GPUTexture:
    brush_icon = getattr(BrushIcon, brush.sculpt_tool.upper(), BrushIcon.DEFAULT)
    return gputex_from_image_file(
        SculptPlusPaths.SRC_LIB_IMAGES('brushes', brush_icon.value + '.png'),
        idname='BrushIcon.' + brush_icon.name)

def get_brush_tex(brush: Brush) -> GPUTexture:
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
    return gputex_from_image_file(icon_path, idname=brush['id'])

def gputex_from_image_file(filepath: str, size: Tuple[int, int] = (128, 128), idname: Union[str, None] = None) -> GPUTexture:
    """
    Loads an image as  GPUTexture type from a file.

    Args:
        filepath (str): Path to the image file.
    """
    if idname is None:
        idname: str = filepath

    gputex: GPUTexture = cache_text.get(idname, None)
    if gputex is not None:
        return gputex

    img: Image = load_image_and_scale(filepath, size)
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

    cache_text[idname] = gputex
    return gputex
