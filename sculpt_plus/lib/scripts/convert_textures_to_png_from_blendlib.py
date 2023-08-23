'''
Code executed from the PsdConverter object.
PsdConverter is called from operators.pu in management after importing assets...
when finding assets with PSD format, it will call some subprocess to convert all texture images to PNG
as PSD is not really nice supported because sequence source instead of file and behaves strangely.
'''

import bpy
from bpy.types import Image as BlImage
import numpy as np
import sys

from sculpt_plus.path import SculptPlusPaths


tex_items = {
    i[32:]: i[:32] for i in
    sys.argv[sys.argv.index('--')+1:]
}
tex_names = set(tex_items.keys())


def convert_to_jpg(image: BlImage, output: str):
    ''' Blender BUG. Doing it this way doesn't work as expected as image size is greater LOL.
    image.pack()
    image.file_format = 'JPEG'
    image.filepath_raw = str(image_path.parent / (image_path.stem + '.jpg'))
    image.save()
    '''

    image_pixels = np.empty(len(image.pixels), dtype=np.float32)
    image.pixels.foreach_get(image_pixels)

    # jpg_image = image.copy()
    jpg_image = bpy.data.images.new(image.name + '.png', *image.size, alpha=True)
    # jpg_image.name = image.name + '.jpg'
    jpg_image.pixels.foreach_set(image_pixels)
    #jpg_image.filepath_raw = SculptPlusPaths.DATA_TEXTURE_IMAGES(image['uuid'] + '.png')
    jpg_image.file_format = 'PNG'
    jpg_image.save(filepath=output, quality=80)


for image in bpy.data.images:
    if image.name not in tex_names:
        continue
    convert_to_jpg(image, SculptPlusPaths.DATA_TEXTURE_IMAGES(tex_items[image.name] + '.png'))
