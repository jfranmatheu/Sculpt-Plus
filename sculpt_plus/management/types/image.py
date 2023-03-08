from typing import List, Union, Tuple, Dict
import numpy as np
from pathlib import Path
from uuid import uuid4
from shutil import copyfile, move as movefile
from os.path import basename, splitext, exists, isfile
from PIL import Image as PILImage

import bpy
from bpy.types import Image as BlImage
from gpu.types import Buffer, GPUTexture
import imbuf
from bpy.path import abspath

from sculpt_plus.utils import gpu as gpu_utils
from sculpt_plus.path import SculptPlusPaths, ThumbnailPaths
from sculpt_plus.sculpt_hotbar.di import DiImaOpGamHl
from sculpt_plus.utils.toast import Notify
from sculpt_plus.utils.gpu import gputex_from_image_file


thumb_image_size = (100, 100) # (128, 128)
thumb_px_size = 40000 # 65536


cache_tex: Dict[str, GPUTexture] = dict()
cache_thumbnail: Dict[str, GPUTexture] = dict()


class Image(object):
    bl_type = 'IMAGE'

    _bl_attributes = ('filepath_raw', 'source', 'use_half_precision') #, 'filepath_raw')

    pixels: np.ndarray
    filepath: str
    source: str
    use_half_precision: bool
    id: str
    use_optimize: bool
    px_size: int
    image_size: Tuple[int, int]
    is_valid: bool
    file_format: str
    extension: str
    # thumbnail: 'Thumbnail'

    def __init__(self, input_image: Union[BlImage, str], tex_id: str = None, optimize = False):
        ''' We'll be using the idname here to get the optimized image. '''
        self.id: str = tex_id if tex_id else uuid4().hex
        self.pixels: np.ndarray = None
        self.use_optimize = optimize

        if isinstance(input_image, BlImage):
            self.name = input_image.name
            self.from_image(input_image)
            # This provoke Blender loading image... ImBuffer and causing memory problems...
            # Blender not loading from metadata nor cached data.
            # **** Blender.
            # self.image_size = tuple(input_image.size)
            # self.px_size = self.image_size[0] * self.image_size[1] * 4
            self.filepath: str = input_image.filepath_from_user()
        else:
            self.filepath: str = input_image

        if optimize:
            self.image_size = thumb_image_size
            self.px_size = thumb_px_size
        else:
            # Initialized once image is loaded to replace current loaded image.
            self.image_size = None
            self.px_size = None

        if self.filepath:
            # if self.filepath.startswith('//'):
            #     self.filepath = abspath(self.filepath)
            self.extension: str = Path(self.filepath).suffix
            self.file_format = self.extension[1:].upper()
        else:
            # Usually when creating a Thumbnail.emty object.
            # Thumbnails by now are not stored as image file.
            self.extension = None
            self.file_format = None

        # del input_image

    def from_image(self, input_image: BlImage):
        for key in Image._bl_attributes:
            setattr(self, key, getattr(input_image, key))

    def save_to_addon_data(self, move: bool = False):
        if self.use_optimize:
            # Action not supported for optimizated images. (which are stored in the database)
            return
        filepath = Path(self.filepath)
        if not filepath.exists() or not filepath.is_file():
            print("ERROR! Image file does not exist! -> ", self.filepath)
            return
        ext = Path(self.filepath).suffix
        self.extension = ext
        src_filepath = self.filepath
        dst_filepath: str = SculptPlusPaths.DATA_TEXTURE_IMAGES(self.id + ext)
        if move:
            movefile(src_filepath, dst_filepath)
        else:
            copyfile(src_filepath, dst_filepath)
        self.filepath = dst_filepath

    def to_image(self, to_image: BlImage) -> BlImage or None:
        if self.use_optimize:
            # Action not supported for optimizated images.
            return

        #for key in Image._bl_attributes:
        #    setattr(to_image, key, getattr(self, key))
        #to_image.reload()
        #to_image.update()
        #return

        print("Is about to copy pixels from Image to BlImage", self, to_image)
        if to_image is None:
            print("WARN! Invalid image in texture image destination")
            return

        # from_image = bpy.data.images.load(self.filepath, check_existing=True)
        # from_image.name = '.' + self.id
        #for key in Image._bl_attributes:
        #    setattr(from_image, key, getattr(self, key))
        #from_image.update()
        from_image = self.get_bl_image()

        if self.image_size is None: # or self.px_size == 0:
            '''
            if self.source == 'SEQUENCE':
                # first time.
                for key in Image._bl_attributes:
                    setattr(from_image, key, getattr(self, key))
                from_image.filepath = self.filepath_raw
                # from_image.reload()
                print("Image is dirty:", from_image.is_dirty)
                print("Image has data:", from_image.has_data)
                print("Image is float:", from_image.is_float)
                if not from_image.has_data or not from_image.is_float:
                    from_image.update()
            '''
            self.image_size = tuple(from_image.size)
            self.px_size = self.image_size[0] * self.image_size[1] * 4

        if self.px_size == 0:
            print(f"WARN! Image '{from_image.name}' with invalid pixel size {len(to_image.pixels)}/{self.px_size} (given/expected)")
            Notify.WARNING("Invalid Source Image", f"Can't find any pixel data from {from_image.name}:\n- Invalid size: {self.image_size[0]}x{self.image_size[1]} px.\n- Image Source: {str(self.source)}.\n- Image Path: {self.filepath_raw}.")
            return

        if self.source == 'SEQUENCE':
            return from_image

        if to_image.size[0] != self.image_size[0] or to_image.size[1] != self.image_size[1]:
            to_image.scale(*self.image_size)
            print("Scaling image...")

        #if self.pixels is None:
        #    print("WARN! No pixels in source image to copy to dest image")
        #    return

        if self.px_size != len(to_image.pixels):
            print(f"WARN! Image '{from_image.name}' with invalid pixel size {len(to_image.pixels)}/{self.px_size} (given/expected)")
            Notify.WARNING("Invalid Image", f"{from_image.name} with invalid pixel size:\n- Given {len(to_image.pixels)} pixel size.\n- Expected {self.px_size} pixel size.")
            return

        if from_image.pixels is None or len(from_image.pixels) == 0:
            print(f"WARN! Image '{to_image.name}' has no pixel data! Requires a pixel size of", self.px_size)
            Notify.WARNING("Invalid Image", f"{to_image.name} has no pixel data, requires:\n- Pixel size of {len(self.px_size)}.\n- Image size of {self.image_size[0]}x{self.image_size[1]} px.")
            return

        # src_pixels = self.pixels
        # dst_pixels = to_image.pixels

        #for key in Image._bl_attributes:
        #    setattr(to_image, key, getattr(self, key))

        # NEW PROCESS TO REDUCE MEMORY USAGE.
        # self.pixels does not store the pixels data anymore.
        # instead we use bpy, to load image... check if exists and done.

        # to_image.source = self.source
        # to_image.use_half_precision = self.use_half_precision

        # to_image.pixels = from_image.pixels # .foreach_set(self.pixels)
        pixels_from = np.empty(self.px_size, dtype=np.float32)
        from_image.pixels.foreach_get(pixels_from)
        to_image.pixels.foreach_set(pixels_from)
        del pixels_from
        del from_image

        print("Nice image pixels are given!")
        return to_image


    def get_bl_image(self, paste_attributes: bool = False, ensure_float_buffer: bool = False) -> BlImage:
        if image := bpy.data.images.get('.' + self.id, None):
            return image
        image = bpy.data.images.load(self.filepath_raw, check_existing=False)
        image.name = '.' + self.id
        if paste_attributes:
            self.paste_bl_attributes(image)
        if ensure_float_buffer and image.is_float:
            image.update()
        return image


    def paste_bl_attributes(self, bl_image: BlImage) -> None:
        ''' In another world will be to_image. lol. '''
        for key in Image._bl_attributes:
            setattr(bl_image, key, getattr(self, key))


    def load_image(self, input_image: Union[BlImage, str]):
        ''' Load the image. '''
        # print("input:", input_image)
        if not input_image:
            print("WARN! Thumbnail::load_image : BlImage or image filepath is null")
            return None

        if self.use_optimize:
            type = self.id_type
            id = self.id #.split('@')
            if type == 'BRUSH':
                out_filepath: Path = ThumbnailPaths.BRUSH(id)
            elif type == 'CAT_BRUSH':
                out_filepath: Path = ThumbnailPaths.BRUSH_CAT(id)
            elif type == 'TEXTURE':
                out_filepath: Path = ThumbnailPaths.TEXTURE(id)
            elif type == 'CAT_TEXTURE':
                out_filepath: Path = ThumbnailPaths.TEXTURE_CAT(id)
            else:
                print("WARN! Thumbnail::load_image : What ID type is this?", self.id, self.filepath)
                return None

            out_filepath = str(out_filepath)
            # print("-> Output thumnail image path:", out_filepath)
            input_image = bpy.data.images.load(str(input_image), check_existing=True)

        if not input_image.pixels:
            if self.use_optimize:
                bpy.data.images.remove(input_image)
            return None

        if isinstance(input_image, BlImage):
            # METHOD 1: Using Blender API.
            filepath: str = input_image.filepath_from_user()

            if self.use_optimize:
                '''
                import imbuf
                img = imbuf.load(filepath)
                if img.size.x <= 128 and img.size.y <= 128:
                    optimized = True
                else:
                    optimized = False
                img.free()
                '''
                '''
                import imbuf
                img = imbuf.load(filepath)
                img.resize(thumb_image_size, method='BILINEAR')
                imbuf.write(img, filepath=out_filepath)
                img.free()
                '''
                _image: BlImage = input_image.copy()
                _image.scale(*thumb_image_size)
                # thumb_image.filepath_raw = out_filepath
                thumb_image = bpy.data.images.get(".thumb_image", None)
                if thumb_image is None:
                    thumb_image = bpy.data.images.new(".thumb_image", *thumb_image_size)
                    # image.use_alpha = True
                    # image.alpha_mode = 'STRAIGHT'
                    thumb_image.file_format = 'PNG'
                _thumb_image = thumb_image.copy()
                thumb_pixels = gpu_utils.get_nparray_from_image(_image)
                _thumb_image.pixels.foreach_set(thumb_pixels)
                _thumb_image.filepath_raw = out_filepath
                _thumb_image.save()
                bpy.data.images.remove(_image)
                bpy.data.images.remove(_thumb_image)

                self.pixels = thumb_pixels

                # is_packed = thumb_image.packed_file is not None
                # if not is_packed:
                #     thumb_image.pack()

                # else:
                #     thumb_image.save()

                # thumb_image.filepath = out_filepath
                # thumb_image.save()

                '''
                from PIL import Image as PilImage
                with PilImage.open(thumb_image.filepath_from_user()) as pil_img:
                    pil_img = pil_img.resize(thumb_image_size, PilImage.Resampling.BILINEAR)
                    pil_img.save(out_filepath, format='PNG')
                '''

                # if is_packed:
                #     thumb_image.pack()

                bpy.data.images.remove(thumb_image)

            else:
                self.image_size = list(input_image.size)

                self.pixels: np.ndarray = gpu_utils.get_nparray_from_image(input_image)

            del input_image

        elif isinstance(input_image, (str, Path)):
            # METHOD 2: Using PIL library.
            filepath: Path = Path(input_image) if isinstance(input_image, str) else input_image
            if not filepath.exists() or not filepath.is_file():
                print("WARN! Thumbnail::load_image : image not found at", filepath)
                return None

            from PIL import Image as PilImage
            with PilImage.open(filepath) as pil_img:
                if self.use_optimize:
                    pil_img = pil_img.resize(thumb_image_size, PilImage.Resampling.NEAREST)
                    pil_img.save(out_filepath, format='PNG')
                else:
                    self.image_size = list(pil_img.size)
                # print(pil_img.info)
                # print(pil_img.format, len(pil_img.getbands()))
                # mode_to_bpp = {"1": 1, "L": 8, "P": 8, "RGB": 24, "RGBA": 32, "CMYK": 32, "YCbCr": 24, "LAB": 24, "HSV": 24, "I": 32, "F": 32}
                # depth: int = mode_to_bpp[pil_img.mode]
                self.pixels: np.ndarray = np.asarray(pil_img).flatten()

        else:
            print("WARN! Thumbnail::load_image : Input image type is invalid (should be BlImage or str)")

        if self.use_optimize:
            self.filepath = out_filepath
        else:
            self.filepath = filepath

    def get_gputex(self):
        if self.use_optimize:
            gputex: GPUTexture = cache_thumbnail.get(self.id, None)
        else:
            return
            gputex: GPUTexture = cache_tex.get(self.id, None)
        if gputex is not None:
            return gputex
        if self.pixels is None:
            # self.load_image(self.filepath)
            if self.filepath:
                print("[Sculpt+] Loading image data from filepath...", self.filepath)
                gputex, pixels = gputex_from_image_file(self.filepath, self.image_size, self.id, get_pixels=True)
                self.pixels = pixels
            return None
        if len(self.pixels) != self.px_size:
            print(f"WARN! Image '{self.id}' at path '{self.filepath}' with invalid pixel size {len(self.pixels)}/{self.px_size}")
            return None

        buff: Buffer = Buffer(
            'FLOAT',
            self.px_size,
            self.pixels
        )

        gputex: GPUTexture = GPUTexture(
            self.image_size,
            layers=0,
            is_cubemap=False,
            format='RGBA16F' if self.file_format in {'PNG'} else 'RGB16F',
            data=buff
        )

        if self.use_optimize:
            cache_thumbnail[self.id] = gputex
        else:
            cache_tex[self.id] = gputex
        return gputex

    def __del__(self):
        if self.id in cache_tex:
            del cache_tex[self.id]
        if self.id in cache_thumbnail:
            del cache_thumbnail[self.id]
        del self.id
        del self.pixels
        del self.filepath


class Thumbnail(Image):
    is_valid: bool
    id_type: str
    format: str

    @classmethod
    def empty(cls, item) -> 'Thumbnail':
        return cls(None, item.id, item.bl_type)

    @classmethod
    def from_fake_item(cls, fake_item, type: str) -> 'Thumbnail':
        thumb: Thumbnail = cls(None, fake_item.id, type)
        thumb.filepath = fake_item.icon_filepath
        thumb.pixels = fake_item.icon_pixels
        if fake_item.id in gpu_utils.cache_tex:
            gpu_utils.cache_tex.pop(fake_item.id)
        if fake_item.icon:
            cache_thumbnail[thumb.id] = fake_item.icon
        return thumb

    def __init__(self, image_path: Union[BlImage, str], idname: str, _type: str) -> None:
        #if image_path:
        #    print(f"New thumbnail for {_type} with id {idname} using image from {image_path}")
        self.id_type = _type
        self._status: str = 'NONE'
        super().__init__(image_path, idname, optimize=True)

    @property
    def is_valid(self) -> bool:
        return self.pixels is not None and self.filepath and self.status == 'READY'

    @property
    def is_loading(self) -> bool:
        return self.status == 'LOADING'

    @property
    def is_unsupported(self) -> bool:
        return self.status == 'UNSUPPORTED'

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, status: str):
        self._status = status

    def set_filepath(self, filepath: str, lazy_generate: bool = True) -> None:
        self.filepath = filepath
        self.extension: str = Path(self.filepath).suffix
        self.file_format = self.extension[1:].upper()
        self.status = 'NONE'
        if self.id in cache_thumbnail:
            gputex = cache_thumbnail.pop(self.id)
            del gputex
        if lazy_generate:
            from ..thumbnailer import Thumbnailer
            Thumbnailer.push(self)

    def draw(self, p, s, act: bool = False, opacity: float = 1) -> None:
        if not self.use_optimize:
            # ONLY OPTIMIZED IMAGES ARE SUPPORTED FOR DRAWING...
            print("WARN! Only optimized images are supported for drawing!")
            return
        DiImaOpGamHl(p, s, self.get_gputex(),_op=opacity,_hl=int(act))
