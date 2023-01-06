from time import time
from pathlib import Path
import shutil
from math import floor
import sys

from bpy.types import Image as BlImage
import imbuf
import bpy

from PIL import Image
import numpy as np


LEADERBOARD = {
    'IMBUF': 135, # Multithreaded -> ???
    'PIL': 334, # Multithreaded -> 2500-2600
    'BlImage': 131, # Multithreaded -> ???
}

TEXTURES_FOLDER = Path("D:\\B3D Asset Library\\Brushes\\Blender_Brushes_Stylized\\Textures\\Alphas")
OUTPUT_FOLDER = TEXTURES_FOLDER / "Thumbnails"

THUMBNAIL_SIZE = 100, 100
THUMBNAIL_PIXEL_SIZE = THUMBNAIL_SIZE[0] * THUMBNAIL_SIZE[1] * 4
IMAGE_FILE_FORMATS = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.tga')
IMBUF_RESIZE_METHOD = "FAST"
PIL_TIF_FACTOR_MULT = 1./256

REZIZE_METHODS = ('PIL', ) # ('IMBUF', 'PIL', 'BlImage')
RESIZE_METHOD = "PIL" # 'IMBUF' # 'PIL' # 'BlImage'

data_images = bpy.data.images

THUMBNAIL_BLIMAGE = data_images.new('.thumbnail', *THUMBNAIL_SIZE)

IS_WINDOWS_PLATFORM = sys.platform == "Windows"


def _is_image_file(filename: str) -> bool:
    return filename.endswith(IMAGE_FILE_FORMATS) # any(filename.endswith(extension) for extension in IMAGE_FILE_FORMATS)


def get_images_in_directory(directory: Path) -> list[Path]:
    images = []
    for path in directory.iterdir():
        # Get from subdirectories too.
        if path.is_dir():
            images += get_images_in_directory(path)
        else:
            if _is_image_file(path.name):
                images.append(path)
    return images


def _get_thumbnail_path(image_path: Path, ext='.jpg') -> Path:
    return OUTPUT_FOLDER / (image_path.stem + 'thumbnail' + ext)


def _remove_exif(image_path: Path, image: Image):
    # Remove corrupted image data.
    if not image.getexif():
        return image
    print('removing EXIF from', image_path.name, '...')
    data = list(image.getdata())
    image_without_exif = Image.new(image.mode, image.size)
    image_without_exif.putdata(data)
    image_without_exif.save(image_path)
    return image_without_exif


class ResizeImage:
    @staticmethod
    def imbuf(image_path: Path):
        # Load image with 'imbuf' module of Blender, resize the image to a thumbnail size and write it to the output directory.
        image_buf = imbuf.load(str(image_path))
        image_buf.resize(THUMBNAIL_SIZE, method=IMBUF_RESIZE_METHOD)
        imbuf.write(image_buf, filepath=str(_get_thumbnail_path(image_path)))
        image_buf.free()
        del image_buf

    @staticmethod
    def pil(image_path: Path):
        # Load image with PIL module, resize it and write it to the output directory.
        image_pil = Image.open(str(image_path))
        if image_path.suffix in {'.tif', '.tiff'}:
            # image_pil = _remove_exif(image_path, image_pil)
            format = image_pil.format
            ext = image_path.suffix
            # BUG. We need to first convert from the image of 16 bits single channel (TIFF)...
            ##if image_pil.mode == 'L':
            ##    image_pil = image_pil.convert('RGB')
            ##else:
            ##    image_pil = image_pil.convert('L').convert('RGB')
                #image_pil.mode = 'I'
                #image_pil = image_pil.point(lambda i:i*PIL_TIF_FACTOR_MULT).convert('L')
            # image_pil = image_pil.convert('RGB')
            args = {}
        else:
            format = 'JPEG'
            ext = '.jpg'
            args = {
                'optimize': True,
                'quality': 80
            }
        image_pil.thumbnail(THUMBNAIL_SIZE, resample=Image.Resampling.NEAREST)
        image_pil.save(_get_thumbnail_path(image_path, ext=ext), format=format, **args)
        if IS_WINDOWS_PLATFORM:
            # Windows file management is pure evil.
            try:
                image_pil.close()
            except OSError as e:
                pass
        else:
            image_pil.close()
        del image_pil

    @staticmethod
    def blimage(image_path: Path):
        bl_image: BlImage = data_images.load(str(image_path))
        bl_image.scale(*THUMBNAIL_SIZE)
        thumb_pixels = np.empty(THUMBNAIL_PIXEL_SIZE, dtype=np.float32)
        bl_image.pixels.foreach_get(thumb_pixels)
        bl_thumb_image: BlImage = THUMBNAIL_BLIMAGE.copy()
        bl_thumb_image.filepath_raw = str(_get_thumbnail_path(image_path))
        bl_thumb_image.pixels.foreach_set(thumb_pixels)
        bl_thumb_image.save()
        del bl_image
        del bl_thumb_image
        del thumb_pixels


image_paths: list[Path] = get_images_in_directory(TEXTURES_FOLDER)

for METHOD in REZIZE_METHODS:
    OUTPUT_FOLDER.mkdir(exist_ok=True)
    resize_function: callable = getattr(ResizeImage, METHOD.lower())

    allow_multiprocess = METHOD in {'PIL'}
    if allow_multiprocess:
        from threading import Thread
        from multiprocessing import cpu_count

        thread_count = int(cpu_count() / 4)

        start_time = time()

        tot_images = len(image_paths)
        _images_per_thread = tot_images / thread_count
        images_per_thread = [floor(_images_per_thread)] * thread_count
        if _images_per_thread % 1 != 0:
            images_per_thread[0] += int(_images_per_thread % 1 * thread_count)

        def resize_images(image_paths: list[Path], resize_function: callable):
            for image_path in image_paths:
                resize_function(image_path)

        threads = []

        image_path_index = 0
        for image_count in images_per_thread:
            thread = Thread(target=resize_images, args=(image_paths[image_path_index:image_path_index+image_count], resize_function), daemon=True)
            image_path_index += image_count

            threads.append(thread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        time_to_finish = time() - start_time
        print(f"Processed {tot_images} images in {round(time_to_finish, 2)} seconds.")
        #from os import listdir
        #thumbnail_count = len(listdir(str(OUTPUT_FOLDER)))
        #images_per_60s = thumbnail_count * 60 / time_to_finish
        #print(f"Method {METHOD}, processed {images_per_60s} images in 60 seconds.")

    else:
        images_processed_count: int = 0
        start_time = time()

        for image_path in image_paths:
            resize_function(image_path)

            images_processed_count += 1
            if time()-start_time > 60:
                break

        print(f"Method {METHOD}, processed {images_processed_count} images in {round(time()-start_time, 2)} seconds.")
        
    shutil.rmtree(OUTPUT_FOLDER)
