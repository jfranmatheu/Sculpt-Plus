import sys
from pathlib import Path
import numpy as np
from time import time
#import multiprocessing

import bpy
from bpy.types import Image as BlImage

#from sculpt_plus.core.sockets.pbar_client import PBarClient
#from sculpt_plus.management.manager import Manager, Brush, Texture, BrushCategory, TextureCategory
from sculpt_plus.path import SculptPlusPaths, DBShelfManager #, DBShelfPaths, DBShelf


''' Get Command Arguments. '''
argv = sys.argv
print(argv)
BLENDLIB_PATH = argv[1]
INPUT_FILE = argv[6]

EXPORT_TYPE = 'WEBP' # NPY # NPZ # WEBP # JPG # PNG
SAVE_THUMBNAIL_AS_IMAGE = False
'''
INPUTS A TEXT FILE WITH THE IMAGES NAMES SEPARATED BY LINES.
each line has ID (32 characters eg. 'af739105d560452f9e5df4775f1d0751') and Name separated
'''

THUMBNAIL_SIZE = (100, 100)
THUMBNAIL_PIXEL_SIZE = 100 * 100 * 4
THUMB_IMAGE_BASE = bpy.data.images.new('.thumbnail', *THUMBNAIL_SIZE)

data_images = bpy.data.images

# bpy.ops.file.unpack_all()


''' Export Images. '''
def get_image_ndarray(image: BlImage) -> np.ndarray:
    # return np.array(image.pixels, dtype=np.float16).reshape(-1)
    arr = np.empty(len(image.pixels), dtype=np.float32)
    image.pixels.foreach_get(arr)
    return arr


def copy_pixels(image_from: BlImage, image_to: BlImage):
    pixels = get_image_ndarray(image_from)
    image_to.pixels.foreach_set(pixels) # image_to.pixels)


def save_image_ndarray(image_id: str, image: BlImage) -> None:
    np.save(
        SculptPlusPaths.DATA_TEXTURE_IMAGES(image_id + '.npy'),
        get_image_ndarray(image))

'''
def bl_save_thumbnail(filename: str, in_image_path: str):
    # print("Generate thumbnail from:", image_path)
    filename = ''.join(c for c in filename if c in valid_filename_chars)
    image = Image.open(in_image_path)
    # out_image_path = str(PREVIEWS_PATH / (filename + image.file_format)) # '.thumbnail'
    if image.width > 256 or image.height > 256:
        image = image.resize(THUMBNAIL_SIZE, Image.Resampling.NEAREST) #, Image.Resampling.LANCZOS)
    # image.save(out_image_path, image.file_format)
    image_size = (image.width, image.height)
    image = image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    try:
        # NOTE: WTF IS THIS.
        thumb_pixels = np.array(image, dtype=np.float32).reshape(image.width*image.height*4) / 255
    except ValueError:
        thumb_pixels = np.array(image, dtype=np.float32).reshape(image.width*image.height) / 255
    del image
'''

def unfuck_image(fucked_image: BlImage) -> BlImage:
    unfucked_image = bpy.data.images.new(fucked_image.name + '.jpg', *fucked_image.size)
    # fucked_image.pixels.foreach_get(unfucked_image.pixels) # SLOW... IDK WHY BUT LOL.
    # unfucked_image.pixels = fucked_image.pixels # FASTER... LOL.
    copy_pixels(fucked_image, unfucked_image)
    return unfucked_image

def bl_save_image(image_id: str, image: BlImage, generate_thumbnail: bool = True) -> None:
    if len(image.pixels) == 0:
        print("WARN! Image with no pixels! -> ", image.name)
        return

    if image.packed_file is not None:
        image.unpack()

    image_path: Path = Path(image.filepath_from_user())
    image_ext: str = image_path.suffix[1:].upper()

    if image_ext in {'PSD'}:
        # FUCK. Should not support this oversized and unsupported shit. But here we go...
        _image = unfuck_image(image)
        del image

    else:
        _image = image.copy()

    _image.file_format = 'JPEG'
    _image.filepath_raw = SculptPlusPaths.DATA_TEXTURE_IMAGES(image_id + '.jpg')
    _image.save()

    _image.scale(*THUMBNAIL_SIZE)
    _image.use_half_precision = True
    _thumb_pixels = np.empty(THUMBNAIL_PIXEL_SIZE, dtype=np.float32)
    _image.pixels.foreach_get(_thumb_pixels)

    del _image
    del image

    if not generate_thumbnail:
        return None

    if SAVE_THUMBNAIL_AS_IMAGE:
        _thumb_image: BlImage = THUMB_IMAGE_BASE.copy()
        _thumb_image.file_format = 'JPEG'
        _thumb_image.filepath_raw = SculptPlusPaths.DATA_TEXTURE_IMAGES(image_id + '.thumbnail.jpg')
        _thumb_image.use_half_precision = True
        # _thumb_image.pixels.foreach_get(image_path.read_bytes ())
        _thumb_image.pixels.foreach_set(_thumb_pixels)
        _thumb_image.save()

        del _thumb_image

    np.save(SculptPlusPaths.DATA_TEXTURE_IMAGES(image_id + '.thumbnail.npy'), _thumb_pixels)

    '''
    cpy_image: BlImage = image.copy()
    # cpy_image.name = image_id
    cpy_image.scale()
    cpy_image.filepath_raw = SculptPlusPaths.DATA_TEXTURE_IMAGES(image_id + '.jpg')
    cpy_image.save()
    del cpy_image
    '''


start_time = time()
with open(INPUT_FILE, 'r', encoding='ascii') as f: # , DBShelfManager.TEXTURE_THUMBNAILS() as db_thumbnail_manager:
    for line in f.readlines():
        if not line and line == '\n':
            continue
        image_id = line[:32] # 32 characters long ID.
        image_name = line[32:-1] if line[-1] == '\n' else line[32:]
        print(f"Saving image {image_id}@{image_name} to .jpg and thumbnail to .npy ...")
        if image := data_images.get(image_name, None):
            bl_save_image(image_id, image, generate_thumbnail=True)


print("[SCRIPT] Generate images and thumbnails from datablocks -> %.2f seconds" % (time()-start_time))
