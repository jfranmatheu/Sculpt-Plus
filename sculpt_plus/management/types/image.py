from typing import List, Union, Tuple
import numpy as np
from os.path import exists
from PIL import Image as PilImage

import bpy
from bpy.types import Image as BlImage
from gpu.types import Buffer, GPUTexture

from sculpt_plus.utils import gpu as gpu_utils


image_size = (128, 128)
px_size = 65536

class Image(object):
    def __init__(self, image: Union[BlImage, str], idname: str):
        ''' We'll be using the idname here to get the optimized image. '''
        self.id: str = idname
        self.is_optimized: bool = False
        self.pixels: np.ndarray = None
        self.filepath: str = ''
        self.load_image(image)

    def load_image(self, image: Union[BlImage, str]):
        ''' Load the image. '''
        if image is None:
            return None

        if isinstance(image, BlImage):
            filepath = image.filepath_from_user()
            self.is_optimized = True
            self.pixels = image.pixels
            img: Image = image.scale(*image_size)
            self.pixels: np.ndarray = gpu_utils.get_nparray_from_image(img)
            bpy.data.images.remove(img)
            del img

        elif isinstance(image, str):
            filepath = image
            if filepath is None or not exists(filepath):
                return None

        # METHOD 1: Using Blender API.
        # 

        # METHOD 2: Using PIL library.
        image = PilImage.open(self.filepath)
        


    def get_gputex(self):
        gputex: GPUTexture = gpu_utils.cache_tex.get(self.id, None)
        if gputex is not None:
            return gputex

        buff: Buffer = Buffer(
            'FLOAT',
            px_size,
            self.pixels
        )

        gputex: GPUTexture = GPUTexture(
            image_size,
            layers=0,
            is_cubemap=False,
            format='RGBA16F',
            data=buff
        )

        

        gpu_utils.cache_tex[self.id] = gputex
        return gputex
