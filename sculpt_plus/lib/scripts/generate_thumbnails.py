import sys
import os
from pathlib import Path
from os.path import join

argv = sys.argv
# print(argv)
outpath = argv[6]
brush_names = None if argv[7] == 'NONE' else argv[7].split('#$#')
image_names = None if argv[8] == 'NONE' else argv[8].split('#$#')

EXPORT_BRUSHES = brush_names is not None
EXPORT_IMAGES  = image_names is not None

# print("Brushes:", brush_names)
# print("Images:", image_names)

# Cleanup.
for f in os.listdir(outpath):
    os.remove(join(outpath, f))


import bpy

if EXPORT_BRUSHES:
    data_brushes = bpy.data.brushes
    brushes = [data_brushes[brush_name] for brush_name in brush_names if brush_name in data_brushes]

if EXPORT_IMAGES:
    data_images  = bpy.data.images
    images  = [data_images[image_name]  for image_name in image_names if image_name in data_images]


tmp_image = bpy.data.images.new("*NiceImage*", 100, 100)
# tmp_image.filepath = join(outpath, 'test.png')
# tmp_image.save()


import imbuf
import numpy as np

def generate_thumbnail(name: str, image_path: str):
    # print("Generate thumbnail from:", image_path)
    generate_thumbnail_from_image(bpy.data.images.load(image_path))
    return
    image_buf = imbuf.load(image_path)
    image_buf.resize((100, 100), method='FAST')
    # image_buf.filepath = join(outpath, name + '.png')
    imbuf.write(image_buf, filepath=join(outpath, name + '.png'))
    image_buf.free()

def generate_thumbnail_from_image(image):
    # print("Generate image from image:", image)
    if not image.pixels:
        return None
    image.scale(100, 100)
    pixels_to = np.empty(shape=(100*100*4), dtype=np.float32)
    image.pixels.foreach_get(pixels_to)

    _tmp_image = tmp_image.copy()
    _tmp_image.filepath = join(outpath, image.name + '.jpg')
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
        if brush is None:
            continue

        brush_thumbnail = brush.sculpt_tool
        if brush.use_custom_icon:
            icon_filepath: Path = Path(abspath(brush.icon_filepath))
            if icon_filepath.exists() and icon_filepath.is_file() and icon_filepath.is_absolute():
                generate_thumbnail(brush.name, str(icon_filepath))
                brush_thumbnail = str(icon_filepath)

        if brush.texture and brush.texture.type == 'IMAGE' and brush.texture.image and brush.texture.image.source in {'FILE', 'SEQUENCE'}:
            brush_texture_thumbnail = generate_thumbnail_from_image(brush.texture.image)
            if not brush_texture_thumbnail:
                print("WARN! Could not generate thumbnail for texture", brush.texture.name)
                continue
            texture_data = {
                'name': brush.texture.image.name,
                'icon_filepath': brush_texture_thumbnail
            }
        else:
            texture_data = {}

        # brush_icons[brush.name] = (brush_thumbnail, brush_texture_thumbnail)
        out_brushes.append(
            {
                'name': brush.name,
                'icon_filepath': brush_thumbnail,
                'texture': texture_data
            }
        )

    data['brushes'] = out_brushes
    # print(out_brushes)

if EXPORT_IMAGES:
    out_images = []

    for image in images:
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

with open(join(outpath, 'asset_importer_data.json'), 'w') as f:
    json.dump(data, f)
