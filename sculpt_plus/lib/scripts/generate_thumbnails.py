import sys
import os
from pathlib import Path
from os.path import join
from PIL import Image
from sculpt_plus.core.sockets.pbar_client import PBarClient

argv = sys.argv
# print(argv)
outpath = argv[6]
previews_path = Path(outpath)
export_type = argv[7]
SOCKET_PORT = int(argv[8])
#brush_names = None if argv[7] == 'NONE' else argv[7].split('#$#')
#image_names = None if argv[8] == 'NONE' else argv[8].split('#$#')

EXPORT_BRUSHES = export_type.startswith('BRUSH') #brush_names is not None
EXPORT_BRUSH_TEXTURE = export_type=='BRUSH_TEXTURE'
EXPORT_IMAGES  = export_type=='TEXTURE' #image_names is not None


builtin_brushes = {'Blob', 'Boundary', 'Clay', 'Clay Strips', 'Clay Thumb', 'Cloth', 'Crease', 'Draw Face Sets', 'Draw Sharp', 'Elastic Deform', 'Fill/Deepen', 'Flatten/Contrast', 'Grab', 'Inflate/Deflate', 'Layer', 'Mask', 'Multi-plane Scrape', 'Multires Displacement Eraser', 'Multires Displacement Smear', 'Nudge', 'Paint', 'Pinch/Magnify', 'Pose', 'Rotate', 'Scrape/Peaks', 'SculptDraw', 'Simplify', 'Slide Relax', 'Smooth', 'Snake Hook', 'Thumb'}
builtin_images  = {'Render Result', 'Viewer Node'}

# print("Brushes:", brush_names)
# print("Images:", image_names)

# Cleanup.
for f in os.listdir(outpath):
    os.remove(join(outpath, f))


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
import numpy as np

def generate_thumbnail(filename: str, in_image_path: str):
    # print("Generate thumbnail from:", image_path)
    filename = ''.join(c for c in filename if c in valid_filename_chars)
    out_image_path = str(previews_path / (filename + '.jpg')) # '.thumbnail'
    image = Image.open(in_image_path)
    image.resize((100, 100)) #, Image.Resampling.LANCZOS)
    image.save(out_image_path, image.format)
    del image

    # generate_thumbnail_from_image(bpy.data.images.load(image_path))
    return out_image_path
    image_buf = imbuf.load(image_path)
    image_buf.resize((100, 100), method='FAST')
    # image_buf.filepath = join(outpath, name + '.png')
    imbuf.write(image_buf, filepath=join(outpath, name + '.png'))
    image_buf.free()

def generate_thumbnail_from_image(image):
    # print("Generate image from image:", image)
    if not image.pixels:
        return None

    image_filepath: Path = Path(image.filepath_from_user())
    if image_filepath.exists() and image_filepath.is_file() and image_filepath.is_absolute() and image_filepath.suffix in {'jpg', 'png', 'jpeg'}:
        return generate_thumbnail(image.name, str(image_filepath))
    else:
        image.scale(100, 100)
        pixels_to = np.empty(shape=(100*100*4), dtype=np.float32)
        image.pixels.foreach_get(pixels_to)

        _tmp_image = tmp_image.copy()
        _tmp_image.filepath = str(previews_path / (image.name + '.thumbnail'))
        _tmp_image.file_format = 'JPEG'
        #tmp_image.reload()
        #tmp_image.scale(100, 100)
        _tmp_image.pixels.foreach_set(pixels_to)
        _tmp_image.save()

        # print(_tmp_image.filepath)

        return _tmp_image.filepath


from bpy.path import abspath
import json

data = {}

if EXPORT_BRUSHES:
    out_brushes = []

    for brush in brushes:
        pbar_client.increase()

        if brush is None:
            continue

        if brush.name in builtin_brushes:
            continue

        brush_thumbnail = brush.sculpt_tool
        if brush.use_custom_icon:
            icon_filepath: Path = Path(abspath(brush.icon_filepath))
            if icon_filepath.exists() and icon_filepath.is_file() and icon_filepath.is_absolute():
                brush_thumbnail = generate_thumbnail(brush.name, str(icon_filepath))

        br_data = {
            'name': brush.name,
            'icon_filepath': brush_thumbnail,
        }

        if EXPORT_BRUSH_TEXTURE:
            if brush.texture and brush.texture.type == 'IMAGE' and brush.texture.image and brush.texture.image.source in {'FILE', 'SEQUENCE'}:
                brush_texture_thumbnail = generate_thumbnail_from_image(brush.texture.image)
                if not brush_texture_thumbnail:
                    print("WARN! Could not generate thumbnail for texture", brush.texture.name)
                    continue
                tex_data = {
                    'name': brush.texture.image.name,
                    'icon_filepath': brush_texture_thumbnail
                }
                br_data['texture'] = tex_data

        # brush_icons[brush.name] = (brush_thumbnail, brush_texture_thumbnail)
        out_brushes.append(br_data)

    data['brushes'] = out_brushes
    # print(out_brushes)

if EXPORT_IMAGES:
    out_images = []

    for image in images:
        pbar_client.increase()

        if image in builtin_images:
            continue

        if image is None or image.source not in {'FILE', 'SEQUENCE'}:
            continue

        brush_texture_thumbnail = str(generate_thumbnail_from_image(image))

        # texture_icons[image.name] = brush_texture_thumbnail
        out_images.append(
            {
                'name': image.name,
                'icon_filepath': brush_texture_thumbnail
            }
        )

    data['images'] = out_images

    
    # print(out_images)

pbar_client.stop()

with open(join(outpath, 'asset_importer_data.json'), 'w') as f:
    json.dump(data, f)
