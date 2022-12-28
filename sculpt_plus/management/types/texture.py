from typing import List, Union, Tuple
from uuid import uuid4
from pathlib import Path

import bpy
from bpy.types import ImageTexture as BlTexture, Image as BlImage, Brush as BlBrush, Context

from .image import Image, Thumbnail
from .cat_item import CategoryItem
from sculpt_plus.path import DBShelf, ThumbnailPaths


class Texture(CategoryItem):
    id: str
    name: str
    image: Image
    cat_id: str
    thumbnail: Thumbnail

    def __init__(self, texture: BlTexture, cat: str = '', fake_texture = None):
        super().__init__()

        self.name = texture.image.name
        self.image = Image(texture.image, 'TEXTURE@' + self.id)
        self.cat_id: str = cat
        self.thumbnail: Thumbnail = None

        if fake_texture is not None:
            self.from_fake_texture(fake_texture)
        else:
            self.load_icon(self.image.filepath)

    def from_fake_texture(self, fake_texture):
        self.id = fake_texture.id
        self.name = fake_texture.name
        if fake_texture.icon:
            self.thumbnail = Thumbnail.from_fake_item(fake_texture, 'TEXTURE')

    def to_brush(self, context: Context) -> None:
        from sculpt_plus.props import Props
        brush: BlBrush = context.tool_settings.sculpt.brush
        texture: BlTexture = Props.TextureSingleton(context)
        texture['id'] = self.id
        brush.texture = texture
        image: BlImage = Props.TextureImageSingleton(context)
        self.image.to_image(image)

    def load_icon(self, filepath: Union[str, Path]) -> str:
        if self.thumbnail is not None:
            del self.thumbnail
        self.thumbnail = Thumbnail(filepath, self.id, 'TEXTURE')
        return self.thumbnail.filepath

    def __del__(self) -> None:
        if path:= ThumbnailPaths.TEXTURE(self, check_exists=True):
            path.unlink()
        ## DBShelf.TEXTURES.remove(self)
