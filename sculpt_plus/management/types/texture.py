from typing import List, Union, Tuple
from uuid import uuid4
from pathlib import Path

import bpy
from bpy.types import ImageTexture as BlTexture, Image as BlImage, Brush as BlBrush, Context, ImageUser

from .image import Image, Thumbnail
from .cat_item import CategoryItem, TextureCatItem
from sculpt_plus.path import DBShelf, ThumbnailPaths


cache_tex_image_ids: dict[str, str] = {}


class ImageUserData:
    _bl_attributes: Tuple[str] = ('frame_current', 'frame_duration', 'frame_offset', 'frame_start') 

    frame_current: int
    frame_duration: int
    frame_offset: int
    frame_start: int

    # tile: int

    def __init__(self, image_user: ImageUser):
        self.from_image_user(image_user)

    def from_image_user(self, image_user: ImageUser):
        for key in ImageUserData._bl_attributes:
            setattr(self, key, getattr(image_user, key))

    def to_image_data(self, dst_image_user: ImageUser):
        for key in ImageUserData._bl_attributes:
            setattr(dst_image_user, key, getattr(self, key))


bl_texture_attributes = (
    # ALPHA
    'use_alpha', 'use_calculate_alpha', 'invert_alpha',
    # MAPPING
    'use_flip_axis', 'extension',
    'crop_min_x', 'crop_max_x', 'crop_min_y', 'crop_max_y',
    'repeat_x', 'repeat_y', 'use_mirror_x', 'use_mirror_y',
    'checker_distance', 'use_checker_even', 'use_checker_odd',
    # SAMPLING
    'use_interpolation', 'use_mipmap', 'use_mipmap_gauss',
    'filter_type', 'filter_eccentricity', 'filter_lightprobes', 'filter_size', 'use_filter_size_min',
    # COLOR
    'use_clamp', 'factor_red', 'factor_blue', 'factor_green',
    'intensity', 'contrast', 'saturation',
    # COLOR RAMP (Not supported yet)
)

class Texture(TextureCatItem):
    bl_type = 'TEXTURE'

    id: str
    name: str
    image: Image
    cat_id: str
    thumbnail: Thumbnail

    def __init__(self, texture: BlTexture, cat: str = '', fake_texture = None, custom_id: str = None): #, generate_thumbnail=False):
        super().__init__(cat=cat, custom_id=custom_id)

        self.name = texture.image.name
        self.image = Image(texture.image, self.id) # 'TEXTURE@' +  # , generate_thumbnail=(fake_texture is None and generate_thumbnail))
        self.cat_id: str = cat
        # self.thumbnail: Thumbnail = None

        if texture.image.source == 'SEQUENCE':
            # print("\t- Is sequence. Using image user...")
            self.image_user = ImageUserData(texture.image_user)
            self.image.filepath = texture.image.filepath_from_user(image_user=texture.image_user)
        else:
            self.image_user = None

        if fake_texture is not None:
            self.from_fake_texture(fake_texture)
        #elif generate_thumbnail:
        #    self.load_icon(self.image)

        self.copy_bl_attributes(texture)

    def init(self):
        pass

    def copy_bl_attributes(self, bl_texture: BlTexture):
        for key in bl_texture_attributes:
            setattr(self, key, getattr(bl_texture, key))

    def paste_bl_attributes(self, bl_texture: BlTexture):
        for key in bl_texture_attributes:
            setattr(bl_texture, key, getattr(self, key))

    def from_fake_texture(self, fake_texture):
        self.id = fake_texture.id
        self.name = fake_texture.name
        if fake_texture.icon:
            self.thumbnail = Thumbnail.from_fake_item(fake_texture, 'TEXTURE')

    def to_brush(self, context: Context) -> None:
        bl_brush: BlBrush = context.tool_settings.sculpt.brush

        if self.image_user:
            bl_texture = bpy.data.textures.get('.'+self.id, None)
            if not bl_texture:
                bl_texture = bpy.data.textures.new('.'+self.id, 'IMAGE')
            bl_image = self.image.get_bl_image(paste_attributes=False, ensure_float_buffer=True)
            bl_texture.image = bl_image
            self.image_user.to_image_data(bl_texture.image_user)
        else:
            from sculpt_plus.props import Props
            bl_texture: BlTexture = Props.TextureSingleton(context)
            bl_image: BlImage = Props.TextureImageSingleton(context)
            self.image.to_image(bl_image)
            bl_texture.image = bl_image

        self.paste_bl_attributes(bl_texture)

        bl_texture['id'] = self.id
        bl_image['id'] = self.image.id

        bl_brush.texture = bl_texture

        return
        '''
        image: BlImage = Props.TextureImageSingleton(context).copy()
        texture.image = image
        for key in Image._bl_attributes:
            setattr(image, key, getattr(self.image, key))
        image.filepath = self.image.filepath_raw
        if not image.has_data or not image.is_float:
            image.update()
        if self.image_user is not None:
            self.image_user.to_image_data(texture.image_user)

        if not image.has_data or not image.is_float:
            image.update()

        return
        '''

        image: BlImage = Props.TextureImageSingleton(context)
        if self.image_user is not None:
            texture.image = None
            self.image_user.to_image_data(texture.image_user)
        if image := self.image.to_image(image):
            texture.image = image

        #image.reload()

    #def load_icon(self, filepath: Union[BlImage, str, Path]) -> str:
    #    if self.thumbnail is not None:
    #        del self.thumbnail
    #    self.thumbnail = Thumbnail(filepath, self.id, 'TEXTURE')
    #    return self.thumbnail.filepath

    def __del__(self) -> None:
        if path:= ThumbnailPaths.TEXTURE(self, check_exists=True):
            path.unlink()
        ## DBShelf.TEXTURES.remove(self)
