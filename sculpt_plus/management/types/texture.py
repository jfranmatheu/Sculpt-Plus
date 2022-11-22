from typing import List, Union, Tuple

import bpy
from bpy.types import Texture as BlTexture, Image as BlImage

from .image import Image


class Texture(BlTexture):
    id: str
    name: str

    image: Image

    def __init__(self, texture: BlTexture):
        pass
