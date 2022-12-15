from typing import List, Union, Tuple, Dict
import numpy as np
from os.path import exists
from pathlib import Path
from uuid import uuid4

import bpy
from bpy.types import Image as BlImage
from gpu.types import Buffer, GPUTexture

from sculpt_plus.utils import gpu as gpu_utils
from sculpt_plus.path import SculptPlusPaths, ThumbnailPaths
from sculpt_plus.sculpt_hotbar.di import DiImaOpGamHl


thumb_image_size = (100, 100) # (128, 128)
thumb_px_size = 40000 # 65536


cache_tex: Dict[str, GPUTexture] = dict()
cache_thumbnail: Dict[str, GPUTexture] = dict()


class Image(object):
    pixels: np.ndarray
    filepath: str
    id: str
    use_optimize: bool
    px_size: int
    image_size: Tuple[int, int]
    is_valid: bool

    def __init__(self, input_image: Union[BlImage, str], tex_id: str = None, optimize = None):
        ''' We'll be using the idname here to get the optimized image. '''
        self.id: str = tex_id if tex_id else uuid4().hex
        self.pixels: np.ndarray = None
        self.filepath: str = input_image.filepath_from_user() if isinstance(input_image, BlImage) else input_image
        self.use_optimize = optimize
        self.load_image(input_image)
        if optimize:
            self.image_size = thumb_image_size
            self.px_size = thumb_px_size
        else:
            self.px_size = self.image_size[0] * self.image_size[1] * 4

    def to_image(self, to_image: BlImage):
        print("Is about to copy pixels from Image to BlImage", self, to_image)
        if to_image is None:
            print("WARN! Invalid image in texture image destination")
            return
        print(list(to_image.size), self.image_size)
        if to_image.size[0] != self.image_size[0] or to_image.size[1] != self.image_size[1]:
            to_image.scale(*self.image_size)
            print("Scaling image...")

        if self.pixels is None:
            print("WARN! No pixels in source image to copy to dest image")
            return
        
        if self.px_size != len(to_image.pixels):
            print(f"WARN! Image '{to_image.name}' with invalid pixel size {len(to_image.pixels)}/{self.px_size} (given/expected)")

        # src_pixels = self.pixels
        # dst_pixels = to_image.pixels
        to_image.pixels.foreach_set(self.pixels)

        print("Nice image pixels are given!")
        


    def load_image(self, input_image: Union[BlImage, str]):
        ''' Load the image. '''
        # print("input:", input_image)
        if input_image is None:
            print("WARN! Thumbnail::load_image : BlImage or image filepath is null")
            return None

        if self.use_optimize:
            type, id = self.id.split('@')
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

        if isinstance(input_image, BlImage):
            # METHOD 1: Using Blender API.
            filepath: str = input_image.filepath_from_user()
            
            if self.use_optimize:
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
                    pil_img = pil_img.resize(thumb_image_size, PilImage.Resampling.BILINEAR)
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
            gputex: GPUTexture = cache_tex.get(self.id, None)
        if gputex is not None:
            return gputex
        if self.pixels is None:
            self.load_image(self.filepath)
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
            format='RGBA16F',
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

    def __init__(self, image_path: str, idname: str, _type: str) -> None:
        print(f"New thumbnail for {_type} with id {idname} using image from {image_path}")
        self.id_type = _type
        super().__init__(image_path, _type + '@' + idname, optimize=True)

    @property
    def is_valid(self) -> bool:
        return self.pixels is not None and self.filepath

    def draw(self, p, s, act: bool = False, opacity: float = 1) -> None:
        if self.is_valid:
            DiImaOpGamHl(p, s, self.get_gputex(),_op=opacity,_hl=int(act))
        else:
            print(f"Error drawing thumbnail for {self.id_type} with id {self.id.split('@')[1]} and filepath: {self.filepath}")
        #DiIma(p, s, self.get_gputex())
