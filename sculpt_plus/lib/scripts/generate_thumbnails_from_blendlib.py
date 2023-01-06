import bpy
from bpy.types import Image as BlImage

from pathlib import Path
import numpy as np

from sculpt_plus.path import ThumbnailPaths, SculptPlusPaths


def convert_to_jpg(image: BlImage):
    ''' Blender BUG. Doing it this way doesn't work as expected as image size is greater LOL.
    image.pack()
    image.file_format = 'JPEG'
    image.filepath_raw = str(image_path.parent / (image_path.stem + '.jpg'))
    image.save()
    '''

    image_pixels = np.empty(len(image.pixels), dtype=np.float32)
    image.pixels.foreach_get(image_pixels)

    jpg_image = image.copy()
    # jpg_image.name = image.name + '.jpg'
    jpg_image.pixels.foreach_set(image_pixels)
    jpg_image.filepath_raw = SculptPlusPaths.DATA_TEXTURE_IMAGES(image['id'] + '.jpg')
    jpg_image.file_format = 'JPEG'
    jpg_image.save()


for image in bpy.data.images:
    pass
