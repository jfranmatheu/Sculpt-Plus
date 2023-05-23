import sys
import os
from pathlib import Path
from os.path import join
from PIL import Image
from sculpt_plus.core.sockets.pbar_client import PBarClient
import numpy as np

from bpy.ops import file as file_ops

argv = sys.argv

from PIL import __version__
PIL_VERSION = float(''.join(__version__.split('.')[:-1]))
if PIL_VERSION >= 9.0:
    PIL_RESAMPLING_NEAREST = Image.Resampling.NEAREST
else:
    PIL_RESAMPLING_NEAREST = Image.NEAREST

print(argv)
outpath = argv[6]
PREVIEWS_PATH = Path(outpath)
TMP_PATH = PREVIEWS_PATH
export_type = argv[7]
LIB_PATH = Path(argv[1])
SOCKET_PORT = int(argv[8])
#brush_names = None if argv[7] == 'NONE' else argv[7].split('#$#')
#image_names = None if argv[8] == 'NONE' else argv[8].split('#$#')


EXPORT_BRUSHES = export_type.startswith('BRUSH') #brush_names is not None
EXPORT_BRUSH_TEXTURE = export_type=='BRUSH' # 'BRUSH_TEXTURE'
GENERATE_BRUSH_TEXTURE_THUMBNAILS = False
EXPORT_IMAGES  = export_type=='TEXTURE' #image_names is not None

NP_PREVIEWS_FILE_PATH = TMP_PATH / 'previews.npz'

builtin_brushes = {'Blob', 'Boundary', 'Clay', 'Clay Strips', 'Clay Thumb', 'Cloth', 'Crease', 'Draw Face Sets', 'Draw Sharp', 'Elastic Deform', 'Fill/Deepen', 'Flatten/Contrast', 'Grab', 'Inflate/Deflate', 'Layer', 'Mask', 'Multi-plane Scrape', 'Multires Displacement Eraser', 'Multires Displacement Smear', 'Nudge', 'Paint', 'Pinch/Magnify', 'Pose', 'Rotate', 'Scrape/Peaks', 'SculptDraw', 'Simplify', 'Slide Relax', 'Smooth', 'Snake Hook', 'Thumb'}
builtin_images  = {'Render Result', 'Viewer Node'}

# print("Brushes:", brush_names)
# print("Images:", image_names)

# Cleanup.
#for f in os.listdir(outpath):
#    os.remove(join(outpath, f))

file_ops.unpack_all()

pbar_client = PBarClient(SOCKET_PORT)

import bpy

if EXPORT_BRUSHES:
    data_brushes = bpy.data.brushes
    brushes = data_brushes # [data_brushes[brush_name] for brush_name in brush_names if brush_name in data_brushes]
    pbar_client.set_increment_rate(step_count=len(brushes))

if EXPORT_IMAGES:
    data_images  = bpy.data.images
    images  = data_images # [data_images[image_name]  for image_name in image_names if image_name in data_images]
    pbar_client.set_increment_rate(step_count=len(images))

pbar_client.start()


tmp_image = bpy.data.images.new("*NiceImage*", 100, 100)
# tmp_image.filepath = join(outpath, 'test.png')
# tmp_image.save()

import string
valid_filename_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)

import imbuf

THUMBNAIL_SIZE = (100, 100)
THUMBNAIL_PIXEL_SIZE = 100 * 100 * 4

def generate_thumbnail(filename: str, in_image_path: str):
    # print("Generate thumbnail from:", image_path)
    filename = ''.join(c for c in filename if c in valid_filename_chars)
    image = Image.open(in_image_path)
    # out_image_path = str(PREVIEWS_PATH / (filename + image.file_format)) # '.thumbnail'
    # if image.width > 256 or image.height > 256:
    image = image.resize(THUMBNAIL_SIZE, PIL_RESAMPLING_NEAREST) #, Image.Resampling.LANCZOS)
    # image.save(out_image_path, image.file_format)
    image_size = (image.width, image.height)
    image = image.transpose(Image.Transpose.FLIP_TOP_BOTTOM if hasattr(Image, 'Transpose') else Image.FLIP_TOP_BOTTOM)
    thumb_pixels = np.array(image, dtype=np.float32).reshape(image.width*image.height*4) / 255
    '''
    try:
        # NOTE: WTF IS THIS.
        thumb_pixels = np.array(image, dtype=np.float32).reshape(image.width*image.height*4) / 255
    except ValueError:
        thumb_pixels = np.array(image, dtype=np.float32).reshape(image.width*image.height) / 255
    '''
    del image

    # generate_thumbnail_from_image(bpy.data.images.load(image_path))
    return in_image_path, image_size, thumb_pixels # out_image_path
    image_buf = imbuf.load(image_path)
    image_buf.resize(THUMBNAIL_SIZE, method='FAST')
    # image_buf.filepath = join(outpath, name + '.png')
    imbuf.write(image_buf, filepath=join(outpath, name + '.png'))
    image_buf.free()

def generate_thumbnail_from_image(image):
    # print("Generate image from image:", image)
    #if len(image.pixels) == 0:
    #    print("Image file is invalid! No pixel data found!")
    #    return None, None, None

    image_filepath: Path = Path(image.filepath_from_user())
    ok_image = image_filepath.exists() and image_filepath.is_file() and image_filepath.is_absolute()
    if not ok_image:
        print("Image file does not exist!")
        return None, None, None

    if image_filepath.suffix in {'.jpg', '.png', '.jpeg', '.tiff', '.tif', '.tga', '.dds'}:
        return generate_thumbnail(image.name, str(image_filepath))
    else:
        image.scale(*THUMBNAIL_SIZE)
        pixels_to = np.empty(shape=THUMBNAIL_PIXEL_SIZE, dtype=np.float32)
        image.pixels.foreach_get(pixels_to)

        # _tmp_image = tmp_image.copy()
        # _tmp_image.filepath = str(PREVIEWS_PATH / (image.name + '.thumbnail'))
        # _tmp_image.file_format = 'JPEG'
        # _tmp_image.pixels.foreach_set(pixels_to)
        # _tmp_image.save()

        # print(_tmp_image.filepath)

        return str(image_filepath), THUMBNAIL_SIZE, pixels_to # _tmp_image.filepath


from bpy.path import abspath
import json

data = {}
previews = {}

DEFAULT_THUMBNAIL_SIZE = (100, 100)

if EXPORT_BRUSHES:
    out_brushes = []

    for brush in brushes:
        pbar_client.increase()

        if brush is None:
            continue

        if brush.name in builtin_brushes:
            continue

        brush_thumbnail = brush.sculpt_tool
        thumb_pixels = None
        br_icon_size = DEFAULT_THUMBNAIL_SIZE
        if brush.use_custom_icon:
            icon_filepath: Path = Path(abspath(brush.icon_filepath))
            if icon_filepath.exists() and icon_filepath.is_file() and icon_filepath.is_absolute():
                brush_thumbnail, br_icon_size, thumb_pixels = generate_thumbnail(brush.name, str(icon_filepath)) # str(icon_filepath) #
                previews[brush.name] = thumb_pixels

        br_data = {
            'name': brush.name,
            'icon_size': br_icon_size,
            'icon_filepath': brush_thumbnail,
            # 'icon_pixels': thumb_pixels.tolist() if thumb_pixels is not None else None,
        }

        if EXPORT_BRUSH_TEXTURE:
            tex_icon_size = DEFAULT_THUMBNAIL_SIZE
            thumb_pixels = None
            if (bl_texture := brush.texture) and brush.texture.type == 'IMAGE' and (bl_image := brush.texture.image) and brush.texture.image.source in {'FILE', 'SEQUENCE'}:
                if len(bl_image.pixels) == 0:
                    print("Image file is invalid! No pixel data found! - ", bl_image.name)
                    continue
                if GENERATE_BRUSH_TEXTURE_THUMBNAILS:
                    icon_filepath, tex_icon_size, thumb_pixels = generate_thumbnail_from_image(bl_image)
                    if not icon_filepath and thumb_pixels is None:
                        print("WARN! Could not generate thumbnail for texture", bl_texture.name)
                        continue
                else:
                    icon_filepath, tex_icon_size, thumb_pixels = None, None, None
                tex_data = {
                    'name': bl_image.name,
                    'icon_size': tex_icon_size,
                    'icon_filepath': icon_filepath, # None HACK: to avoid generate gputex but the icon pixels are saved in the Texture object for further load.
                    # 'icon_pixels': thumb_pixels.tolist() if thumb_pixels is not None else None,
                }
                previews['TEX@' + bl_image.name] = thumb_pixels
                br_data['texture'] = tex_data

        # brush_icons[brush.name] = (brush_thumbnail, brush_texture_thumbnail)
        out_brushes.append(br_data)

    data['brushes'] = out_brushes
    # print(out_brushes)

if EXPORT_IMAGES:
    out_images = []

    for bl_image in images:
        pbar_client.increase()

        if bl_image in builtin_images:
            continue

        if bl_image is None or bl_image.source not in {'FILE', 'SEQUENCE'}:
            continue

        if len(bl_image.pixels) == 0:
            print("Image file is invalid! No pixel data found! - ", bl_image.name)
            continue

        icon_filepath, icon_size, thumb_pixels = generate_thumbnail_from_image(bl_image)

        # texture_icons[image.name] = brush_texture_thumbnail
        out_images.append(
            {
                'name': bl_image.name,
                'icon_size': icon_size,
                'icon_filepath': icon_filepath
            }
        )
        previews[bl_image.name] = thumb_pixels

    data['images'] = out_images


    # print(out_images)

pbar_client.complete()

with open(join(outpath, 'asset_importer_data.json'), 'w') as f:
    json.dump(data, f)
del data


if previews:
    np.savez_compressed(NP_PREVIEWS_FILE_PATH, **previews)
    del previews

pbar_client.stop()
del pbar_client

# import shutil
# shutil.copyfile(LIB_PATH, TMP_PATH / LIB_PATH.name)
