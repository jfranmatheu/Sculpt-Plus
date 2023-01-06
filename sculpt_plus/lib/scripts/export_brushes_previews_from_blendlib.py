from time import time
from pathlib import Path
import sys
from uuid import uuid4
import json
from datetime import datetime

from bpy.types import Image as BlImage, Texture as BlTexture, ImageTexture as BlImageTexture, Brush as BlBrush
from bpy.ops.file import unpack_all
from bpy import data as D

from sculpt_plus.path import SculptPlusPaths



'''
TARGET:
- Export images 
'''


''' Get Command Arguments.
Called from Blender.

Command arguments:
0. b3d exec.
1. blendlib path.
2. --background flag.
3. --python flag.
4. script path.
5. '--' empty break flag.
6. Export type (Brushes or Images).
'''
argv = sys.argv
print(argv)
BLENDLIB_FILEPATH = argv[1]
THIS_SCRIPT_FILEPATH = argv[4]
EXPORT_DATA_TYPE = argv[6]

USE_INPUT_FILE = EXPORT_DATA_TYPE == 'FILE'
EXPORT_BRUSHES = EXPORT_DATA_TYPE == 'BRUSH'
EXPORT_IMAGES = EXPORT_DATA_TYPE in {'TEXTURE', 'IMAGE'}

COMPATIBLE_IMAGE_EXTENSIONS = {'PNG', 'JPG', 'JPEG', 'TGA', 'TIFF', 'TIF', 'PSD'}

OUTPUT_DIR = Path(SculptPlusPaths.TEMP_THUMBNAILS(datetime.now().strftime("%Y%m%d_%H%M%S")))
OUTPUT_DIR.mkdir(exist_ok=True)
OUTPUT_HEADER_FILE = OUTPUT_DIR / 'header.json'


# UNPACK EVERYTHING TO MAKE THINGS EASIER!?
# TODO: just unpack specific images that are NOT .psd nor .tiff/.tif...
unpack_all()

def _verify_image_path(filepath: str) -> Path or None:
    image_path = Path(filepath)
    if not image_path.exists() or not image_path.is_file():
        return None
    if image_path.suffix[1:].upper() not in COMPATIBLE_IMAGE_EXTENSIONS:
        return None
    return image_path

def _verify_image(bl_image: BlImage) -> Path or None:
    if bl_image is None:
        return False
    if bl_image.type != 'IMAGE' or bl_image.source not in {'FILE', 'SEQUENCE'}:
        return False
    if len(bl_image.pixels) == 0:
        return False
    return _verify_image_path(bl_image.filepath_from_user())

def _verify_image_texture(bl_texture: BlTexture) -> Path or None:
    if bl_texture is None:
        return None
    if not isinstance(bl_texture, BlImageTexture):
        return None
    return _verify_image(bl_texture.image)

def add_uuid(datablock) -> str:
    id = datablock['id'] = uuid4().hex
    return id

def get_brush_icon_data(brush: BlBrush) -> Path or None:
    if not brush.use_custom_icon:
        return None
    return _verify_image_path(brush.icon_filepath)

def get_brush_image_texture_data(brush: BlBrush) -> Path or None:
    image_path = _verify_image_texture(brush.texture)
    if image_path is None:
        return None
    return {
        'name': 
        'id': add_uuid(brush.texture.image)
    }

def get_brush_data(brush: BlBrush) -> dict:
    texture_data: dict = get_brush_image_texture_data(brush)

    return add_uuid(brush), {
        'name': brush.name,
        'color': brush.color,
        'sculpt_tool': brush.sculpt_tool,
        'use_custom_icon': brush.use_custom_icon,
        'icon_filepath': str(get_brush_icon_data(brush)),
        'texture_filepath': str(),
    }



def _prepare_image(image: BlImage) -> BlImage:
    image.name = uuid4().hex
    return image

data_brushes: list[BlBrush] = [b for b in D.brushes if b.use_paint_sculpt]
with OUTPUT_HEADER_FILE.open('w', encoding='ascii') as json_file:
    items: dict[str, dict] = {}

    def _add_item_data(id, item_data):
        items[id] = item_data

    for brush in data_brushes:
        _add_item_data(get_brush_data(brush))

    json.dump(json_file, items, indent=4, ensure_ascii=True)
