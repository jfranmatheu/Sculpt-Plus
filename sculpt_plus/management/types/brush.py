from os import path
from pathlib import Path
from typing import Union, Dict, List

import bpy
from bpy.types import Brush as BlBrush, Image as BlImage, Texture as BlTexture, TextureSlot as BlTextureSlot
from bpy.types import bpy_prop_array
from mathutils import Vector, Color
from .cat_item import BrushCatItem
from .image import Thumbnail
from .texture import Texture
from .brush_props import BaseBrush, brush_properties_per_sculpt_type
from sculpt_plus.path import SculptPlusPaths, DBShelf, ThumbnailPaths


cache__brush_icons: Dict[str, int] = {}


class TextureSlot:
    name: str
    map_mode: str
    offset: list[float]
    scale: list[float]

    _attributes = ('map_mode', 'offset', 'scale')

    def __init__(self, texture_slot: BlTextureSlot):
        if texture_slot is not None:
            self.from_texture_slot(texture_slot)

    def update_attr(self, attr, value):
        if isinstance(value, (bpy_prop_array, Vector, Color)):
            setattr(self, attr, tuple(value))
        else:
            setattr(self, attr, value)

    def from_texture_slot(self, texture_slot: BlTextureSlot) -> None:
        update_attr = self.update_attr
        for attr in TextureSlot._attributes:
            update_attr(attr, getattr(texture_slot, attr))

    def to_texture_slot(self, texture_slot: BlTextureSlot) -> None:
        for attr in TextureSlot._attributes:
            setattr(texture_slot, attr, getattr(self, attr))


class Brush(BrushCatItem, BaseBrush):
    use_texture: bool
    texture_id: str
    texture_slot: TextureSlot
    thumbnail: Thumbnail
    icon_filepath: str
    # icon_id: str -> is the same as brush.id

    def __init__(self, brush: BlBrush = None):
        self.texture_id = None
        super(Brush, self).__init__()
        self.thumbnail: Thumbnail = None
        self.texture_slot = TextureSlot(None)
        if brush is not None:
            self.from_brush(brush)
            print(f"New BrushItem {self.id} from BlenderBrush {brush.name}")

        ## DBShelf.BRUSH_DEFAULTS.write(self)
        ## DBShelf.BRUSH_SETTINGS.write(self)

    def load_icon(self, filepath: Union[str, Path]) -> str:
        if self.thumbnail is not None:
            del self.thumbnail
        self.thumbnail = Thumbnail(filepath, self.id, 'BRUSH')
        return self.thumbnail.filepath

    def update_attr(self, attr, value):
        if isinstance(value, (bpy_prop_array, Vector, Color)):
            setattr(self, attr, tuple(value))
        else:
            setattr(self, attr, value)

    def from_brush(self, brush: BlBrush) -> None:
        # LOAD ICON...
        update_attr = self.update_attr
        if brush.use_custom_icon:
            icon_filepath: Path = Path(brush.icon_filepath)
            if icon_filepath.exists() and icon_filepath.is_file():
                # data_brush_icons_path: str = SculptPlusPaths.DATA_BRUSH_PREVIEWS()
                if icon_filepath.stem == self.id: # icon_filepath.relative_to(data_brush_icons_path):
                    # It's ok. It is saved in the sculpt_plus/brush/icons folder
                    pass
                else:
                    # We have to create a thumbnail image for this image
                    # and store it in the proper place.
                    self.icon_filepath = brush.icon_filepath = self.load_icon(icon_filepath)
            else:
                brush.use_custom_icon = False

        for attr in brush_properties_per_sculpt_type[brush.sculpt_tool]:
            update_attr(attr, getattr(brush, attr))

        self.texture_slot.from_texture_slot(brush.texture_slot)

    def to_brush(self, brush: Union[BlBrush, bpy.types.Context]) -> None:
        if isinstance(brush, bpy.types.Context):
            brush: BlBrush = brush.tool_settings.sculpt.brush
            ''' Ensure that the current (now previous one) brush is updated before switching to the new one. '''
            if 'id' in brush and brush['id'] is not None:
                from sculpt_plus.props import Props
                prev_brush = Props.GetBrush(brush['id'])
                if prev_brush is not None:
                    prev_brush.from_brush(brush)
        brush['id'] = self.id
        brush.sculpt_tool = self.sculpt_tool
        for attr in brush_properties_per_sculpt_type[self.sculpt_tool]:
            setattr(brush, attr, getattr(self, attr))

        self.texture_slot.to_texture_slot(brush.texture_slot)

    def __del__(self) -> None:
        if path:= ThumbnailPaths.BRUSH(self, check_exists=True):
            path.unlink()
        ## DBShelf.BRUSH_DEFAULTS.remove(self)
        ## DBShelf.BRUSH_SETTINGS.remove(self)
