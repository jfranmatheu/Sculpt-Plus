import bpy
from bpy.types import Brush, Texture, ImageTexture, Image
from gpu.types import GPUTexture
from mathutils import Vector

from typing import Union
from os.path import exists, isfile
import numpy as np
from pathlib import Path
from uuid import uuid4

from sculpt_plus.utils.gpu import gputex_from_image_file, get_brush_type_tex, gputex_from_pixels
from sculpt_plus.management.types.brush_props import sculpt_tool_items
from sculpt_plus.management.types import Brush, Texture


sculpt_tool_items_set = set(sculpt_tool_items)
COMPATIBLE_IMAGE_EXTENSIONS = {'PNG', 'JPG', 'JPEG', 'TGA', 'TIFF', 'TIF', 'PSD'}


def _verify_image_path(filepath: str) -> Path or None:
    image_path = Path(filepath)
    if not image_path.exists() or not image_path.is_file():
        return None
    format = image_path.suffix[1:].upper()
    if format not in COMPATIBLE_IMAGE_EXTENSIONS:
        return None
    return format


class FakeViewItemThumbnail:
    # TODO: ADD CLASSMETHOD TO CREATE NEW FROM FILEPATH, WHICH WILL GENERATE THE THUMBNAIL TO TEMP FAKE ITEMS FOLDER.

    # gputex: GPUTexture
    pixels: np.ndarray
    size: tuple[int, int]
    filepath: str

    def __init__(self, idname: str, filepath: str, size: tuple[int, int] = (100, 100), pixels = None):
        self.id = idname
        self.pixels = pixels
        self.size = size
        self.filepath = filepath

    def load_gputex(self) -> GPUTexture:
        if self.pixels:
            return gputex_from_pixels(self.size, self.id, self.pixels)
        elif self.filepath:
            gputex, pixels = gputex_from_image_file(self.filepath, self.size, self.id)
            if pixels:
                self.pixels = pixels
            return gputex
        return None # DEFAULT Icon

    def draw(self, p, s) -> None:
        if gputex := self.load_gputex():
            pass


class FakeViewItem:
    id: str
    name: str
    icon: FakeViewItemThumbnail

    def __init__(self, name: str = '', icon_filepath: str = '', icon_size: tuple = (100, 100), icon_pixels = None, id: str = None) -> None:
        self.id = id if id else uuid4().hex
        self.name = name
        if icon_filepath or icon_pixels:
            self.icon = FakeViewItemThumbnail(self.id, icon_filepath, icon_size, icon_pixels)
        else:
            self.icon = None

    def draw(self, p, s):
        if self.icon:
            self.icon.draw(p, s)
        else:
            self.draw_default(p, s)

    def draw_default(self, p, s):
        ''' To be overrided in subclasses. '''
        pass

    def set_icon(self, filepath: str, size: tuple[int, int] = (100, 100), pixels = None) -> Union['FakeViewItem_Brush', 'FakeViewItem_Texture']:
        self.icon = FakeViewItemThumbnail(self.id, filepath, size, pixels)
        return self

    def come_true(self) -> None:
        ''' Turn fake item into a real item! Save thumbnail and image, brush info...
            whatever info in corresponding folder and database. '''
        pass


class FakeViewItem_Texture(FakeViewItem):
    @classmethod
    def from_bl_image(cls, image: Image, generate_thumbnail: bool = True):
        image['id'] = uuid4().hex
        fake_texture = cls(
            name=image.name,
            id=image['id'],
            # icon_filepath=image.filepath_from_user(),
            # icon_size=image.size,
        )
        if generate_thumbnail:
            from sculpt_plus.path import SculptPlusPaths
            from sculpt_plus.props import Props
            filepath: str = SculptPlusPaths.TEMP_FAKE_ITEMS(image['id'] + '.jpg')
            base_thumb_image = Props.get_temp_thumbnail_image()
            thumb_image: Image = base_thumb_image.copy()
            thumb_image.scale(100, 100)
            thumb_image.filepath_raw = filepath
            thumb_image.save()
            thumb_pixels = np.empty(40000, dtype=np.float32)
            thumb_image.pixels.foreach_get(thumb_pixels)
            # image.save_render(filepath, quality=75)
            fake_texture.set_icon(filepath, size=(100, 100), pixels=thumb_pixels)
            bpy.data.images.remove(thumb_image)
        #else:
        #    fake_texture.set_icon(filepath, size=image.size)
        return fake_texture
    
    def come_true(self) -> None:
        ''' Turn fake item into a real item! Save thumbnail and image, brush info...
            whatever info in corresponding folder and database. '''
        pass


class FakeViewItem_Brush(FakeViewItem):
    use_custom_icon: bool
    sculpt_tool: str

    @classmethod
    def from_bl_brush(cls, brush: Brush, generate_thumbnail: bool = True, generate_tex_thumbnail: bool = True):
        brush['id'] = uuid4().hex
        fake_brush = cls(
            name=brush.name,
            sculpt_tool=brush.sculpt_tool,
            id=brush['id']
        )
        if brush.use_custom_icon:
            if generate_thumbnail:
                from sculpt_plus.path import SculptPlusPaths
                filepath: str = SculptPlusPaths.TEMP_FAKE_ITEMS(brush['id'] + '.jpg')
                fake_brush.generate_from_filepath(
                    brush.icon_filepath,
                    filepath,
                    'JPEG'
                 )
            else:
                fake_brush.set_icon(
                    filepath=brush.icon_filepath,
                )
        if texture := brush.texture:
            if isinstance(texture, ImageTexture) and (image := texture.image):
                if image.type == 'IMAGE' and image.source in {'FILE', 'SEQUENCE'} and len(image.pixels) > 0:
                    fake_brush.set_texture(
                        FakeViewItem_Texture.from_bl_image(image, generate_thumbnail=generate_tex_thumbnail)
                    )
        return fake_brush

    def generate_from_filepath(self, filepath, output, format: str = 'JPEG'):
        from PIL import Image as PilImage
        image = PilImage.open(filepath)
        image.thumbnail((100, 100), resample=PilImage.Resampling.NEAREST if hasattr(PilImage, 'Resampling') else PilImage.NEAREST)
        image = image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        thumb_pixels = np.array(image, dtype=np.float32).reshape(40000) / 255
        if format == 'JPEG':
            image.save(output, format=format, optimize=True, quality=80)
        else:
            image.save(output, format=format)
        self.set_icon(output, size=(100, 100), pixels=thumb_pixels)
        image.close()
        del image

    def __init__(self, name: str = '', sculpt_tool: str = 'DRAW', id: str = None): # icon_filepath: str = '', icon_size: tuple = (100, 100), icon_pixels = None, texture_data: dict = None) -> None:
        self.use_custom_icon = False # icon_filepath not in sculpt_tool_items_set
        self.sculpt_tool = sculpt_tool
        self.texture = None
        super().__init__(name, id=id)
        # print("pixels:", icon_pixels)
        '''
        super().__init__(name, icon_filepath, icon_size, icon_pixels)
        if texture_data:
            self.texture = FakeViewItem_Texture(**texture_data)
        else:
            self.texture = None
        '''

    def set_icon(self, filepath: str, size: tuple[int, int] = (100, 100), pixels=None) -> Union['FakeViewItem_Brush', 'FakeViewItem_Texture']:
        if exists(filepath) and isfile(filepath):
            self.use_custom_icon = True
        super().set_icon(filepath, size, pixels)

    def load_icon(self):
        if self.use_custom_icon:
            super().load_icon()
        else:
            self.icon = get_brush_type_tex(self.icon_filepath)

    def set_texture(self, fake_texture: FakeViewItem_Texture) -> 'FakeViewItem_Brush':
        self.texture = fake_texture
        return self

    def new_texture(self, name: str = '', icon_filepath: str = '', icon_size: tuple = (100, 100), icon_pixels = None, id: str = None):
        fake_texture = FakeViewItem_Texture(
            name=name,
            icon_filepath=icon_filepath,
            icon_size=icon_size,
            icon_pixels=icon_pixels,
            id=id
        )
        self.set_texture(fake_texture)
        return fake_texture

    def come_true(self) -> None:
        ''' Turn fake item into a real item! Save thumbnail and image, brush info...
            whatever info in corresponding folder and database. '''
        if self.texture is not None:
            self.texture.come_true()
        
        # Brush come true...
