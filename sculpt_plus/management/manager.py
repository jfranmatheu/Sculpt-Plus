from typing import Dict, Union, List, Set, Tuple
import shelve
from os import path
import json
from collections import OrderedDict
from pathlib import Path

import bpy
from bpy.types import Brush as BlBrush, Texture as BlTexture, Image as BlImage

from sculpt_plus.path import DBShelf, SculptPlusPaths, DBShelfPaths, DBShelfManager, data_brush_dir, data_texture_dir
from .types.cat import BrushCategory, TextureCategory, Brush, Texture
from sculpt_plus.lib import Icon
from sculpt_plus.sculpt_hotbar.wg_view import FakeViewItem_Brush, FakeViewItem_Texture


builtin_brush_names = ('Blob', 'Boundary', 'Clay', 'Clay Strips', 'Clay Thumb', 'Cloth', 'Crease', 'Draw Face Sets', 'Draw Sharp', 'Elastic Deform', 'Fill/Deepen', 'Flatten/Contrast', 'Grab', 'Inflate/Deflate', 'Layer', 'Mask', 'Multi-plane Scrape', 'Multires Displacement Eraser', 'Multires Displacement Smear', 'Nudge', 'Paint', 'Pinch/Magnify', 'Pose', 'Rotate', 'Scrape/Peaks', 'SculptDraw', 'Simplify', 'Slide Relax', 'Smooth', 'Snake Hook', 'Thumb')
exclude_brush_names = {'Mask', 'Draw Face Sets', 'Simplify', 'Multires Displacement Eraser', 'Multires Displacement Smear'}
filtered_builtin_brush_names = tuple(b for b in builtin_brush_names if b not in exclude_brush_names)


class HotbarManager:
    brushes: List[str]
    selected: str
    
    alt_brushes: List[str]
    alt_selected: str
    
    use_alt: bool

    def __init__(self):
        self._brushes: List[str] = [None] * 10
        self._selected: str = None
        self.alt_selected: str = None
        self.alt_brushes: List[str] = [None] * 10
        self.use_alt: bool = False

    @property
    def brushes(self) -> List[str]:
        if self.use_alt:
            return self.alt_brushes
        return self._brushes

    @brushes.setter
    def brushes(self, brushes: List[str]):
        self._brushes = brushes

    @property
    def selected(self) -> str:
        if self.use_alt:
            return self.alt_selected
        return self._selected

    def toggle_alt(self) -> None:
        self.use_alt = not self.use_alt

    @selected.setter
    def selected(self, item):
        if isinstance(item, str):
            pass
        elif isinstance(item, int):
            item = self.brushes[item]
        elif isinstance(item, Brush):
            item = item.id
        else:
            item = None
            print(f'WARN! Invalid selected hotbar item: {item}')
            # raise ValueError(f'Invalid selected item: {item}')
        if self.use_alt:
            self.alt_selected = item
        else:
            self._selected = item

    def serialize(self) -> dict:
        ''' Serialize hotbar data to a dictionary. '''
        return {
            '_brushes': self._brushes,
            '_selected': self._selected,
            'alt_brushes': self.alt_brushes,
            'alt_selected': self.alt_selected
        }

    def deserialize(self, data: dict) -> None:
        ''' Load data from dictionary. '''
        for attr, value in data.items():
            setattr(self, attr, value)


class Manager:
    _instance = None

    brush_cats: Dict[str, BrushCategory]
    brushes: Dict[str, Brush]
    texture_cats: Dict[str, TextureCategory]
    textures: Dict[str, Texture]

    active_brush_cat: BrushCategory
    active_texture_cat: TextureCategory

    selected_item: str

    hotbar: HotbarManager

    @classmethod
    def get(cls) -> 'Manager':
        if cls._instance is None:
            cls._instance = Manager()
        return cls._instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Manager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self._active_brush_cat: str = ''
        self._active_texture_cat: str = ''
        self._active_brush: str = ''
        self.active_texture: str = ''

        self.brush_cats = OrderedDict()
        self.brushes = dict()

        self.texture_cats = OrderedDict()
        self.textures = dict()

        self.hotbar: HotbarManager = HotbarManager()

    ''' Getters. '''
    @property
    def brush_list(self) -> List[Brush]:
        return self.brushes.values()

    @property
    def texture_list(self) -> List[Texture]:
        return self.textures.values()

    @property
    def active_brush_cat(self) -> Union[BrushCategory, None]:
        return self.brush_cats.get(self._active_brush_cat, None)

    @active_brush_cat.setter
    def active_brush_cat(self, value: Union[BrushCategory, str]):
        if isinstance(value, str):
            self._active_brush_cat = value
        elif isinstance(value, BrushCategory):
            self._active_brush_cat = value.id

    @property
    def active_brush(self) -> str:
        return self._active_brush

    @active_brush.setter
    def active_brush(self, brush: Union[Brush, str]):
        brush_id = brush.id if isinstance(brush, Brush) else brush
        self._active_brush = brush_id
        if brush_id and (brush := self.get_brush(brush_id)):
            self.active_texture = brush.texture_id

    @property
    def active_texture_cat(self) -> Union[TextureCategory, None]:
        return self.texture_cats.get(self._active_texture_cat, None)

    @active_texture_cat.setter
    def active_texture_cat(self, value: Union[TextureCategory, str]):
        if isinstance(value, str):
            self._active_texture_cat = value
        elif isinstance(value, TextureCategory):
            self._active_texture_cat = value.id

    @property
    def brushes_count(self) -> int:
        return len(self.brushes)

    @property
    def textures_count(self) -> int:
        return len(self.textures)

    @property
    def brush_cats_count(self) -> int:
        return len(self.brush_cats)

    @property
    def texture_cats_count(self) -> int:
        return len(self.texture_cats)

    def get_brush(self, brush_id: str) -> Brush:
        return self.brushes.get(brush_id, None)

    def get_texture(self, texture_id: str) -> Texture:
        return self.textures.get(texture_id, None)

    def get_brush_cat(self, cat: Union[str, Brush, int]) -> BrushCategory:
        if isinstance(cat, int):
            for brush_cat in self.brush_cats.values():
                if brush_cat.index == cat:
                    return brush_cat
            return None
        if isinstance(cat, str):
            return self.brush_cats.get(cat, None)
        if isinstance(cat, Brush):
            return self.brush_cats.get(cat.cat_id, None)
        return None

    def get_texture_cat(self, cat: Union[str, Texture, int]) -> TextureCategory:
        if isinstance(cat, int):
            for brush_cat in self.brush_cats.values():
                if brush_cat.index == cat:
                    return brush_cat
            return None
        if isinstance(cat, str):
            return self.texture_cats.get(cat, None)
        if isinstance(cat, Texture):
            return self.texture_cats.get(cat.cat_id, None)
        return None


    ''' Remove Methods. '''
    def remove_brush_item(self, brush_id: str) -> None:
        cat_item: Brush = self.brushes.pop(brush_id if isinstance(brush_id, str) else brush_id.id)
        self.get_brush_cat(cat_item).unlink_item(brush_id)
        del cat_item

        ## DBShelf.BRUSH_SETTINGS.remove(brush_id)
        ## DBShelf.BRUSH_DEFAULTS.remove(brush_id)

    def remove_texture_item(self, texture_id: str) -> None:
        cat_item: Texture = self.textures.pop(texture_id if isinstance(texture_id, str) else texture_id.id)
        self.get_texture_cat(cat_item).unlink_item(texture_id)
        del cat_item

        ## DBShelf.TEXTURES.remove(texture_id)

    def remove_brush_cat(self, cat: Union[str, BrushCategory]) -> None:
        if cat is None:
            return
        act_brush_cat: BrushCategory = self.active_brush_cat
        brush_cat: BrushCategory = self.brush_cats.pop(cat) if isinstance(cat, str) else self.brush_cats.pop(cat.id)
        if not brush_cat:
            return
        cat_item_ids: List[str] = brush_cat.item_ids
        hotbar = self.hotbar
        hotbar_brush_ids_set = set(hotbar.brushes)
        for brush_id in cat_item_ids:
            del self.brushes[brush_id]
            if brush_id in hotbar_brush_ids_set:
                hotbar.brushes[hotbar.brushes.index(brush_id)] = None

        if brush_cat == act_brush_cat:
            if self.brush_cats_count != 0:
                self.active_brush_cat = list(self.brush_cats.keys())[0]

        brush_cat.clear()
        del brush_cat

        # DBShelf.BRUSH_CAT.remove(cat_id)
        # DBShelf.BRUSH_SETTINGS.remove(*cat_item_ids)
        # DBShelf.BRUSH_DEFAULTS.remove(*cat_item_ids)

    def remove_texture_cat(self, cat: Union[str, TextureCategory]) -> None:
        if cat is None:
            return
        texture_cat: TextureCategory = self.texture_cats.pop(cat) if isinstance(cat, str) else self.brush_cats.pop(cat.id)
        if not texture_cat:
            return
        cat_item_ids: List[str] = texture_cat.item_ids
        for texture_id in cat_item_ids:
            del self.textures[texture_id]

        if texture_cat.id == self.active_texture_cat:
            if self.texture_cats_count != 0:
                self.active_texture_cat = list(self.texture_cats.keys())[0]

        texture_cat.clear()
        del texture_cat

        # DBShelf.TEXTURE_CAT.remove(cat_id)
        # DBShelf.TEXTURES.remove(*cat_item_ids)

    ''' Defaults. Reset. '''
    def reset_brushes(self, *brushes: str) -> None:
        with DBShelfManager.BRUSH_DEFAULTS() as def_db:
            with DBShelfManager.BRUSH_SETTINGS() as db:
                for brush_idname in brushes:
                    # Retrieve the brush default state settings.
                    def_brush: Brush = def_db.get(brush_idname)
                    # Replace the mutable copy of the brush in the DB.
                    db.write(def_brush)
                    # Replace brush data.
                    self.add_brush(def_brush)
                    # TODO: if the brush is the current active brush,
                    # we should call to_brush() to ensure it is updated.

    def reset_brush_cat(self, cat_id: Union[str, BrushCategory]) -> None:
        cat: BrushCategory = cat if isinstance(cat, BrushCategory) else self.get_brush_cat(cat_id)
        if cat:
            self.reset_brushes(*cat.item_ids)


    ''' Move from cat to cat. '''
    def move_brush(self, brush: Union[Brush, str], from_cat: Union[BrushCategory, str, None], to_cat: Union[BrushCategory, str]) -> None:
        brush = self.get_brush(brush, None) if isinstance(brush, str) else brush
        if not brush:
            return
        if from_cat is None:
            from_cat = self.get_brush_cat(brush)
        else:
            from_cat = self.get_brush_cat(from_cat) if isinstance(from_cat, str) else from_cat
        to_cat = self.get_brush_cat(to_cat) if isinstance(to_cat, str) else to_cat

        from_cat.unlink_item(brush) # no needed since link_item already unlinks from previous, but it is faster like this.
        to_cat.link_item(brush)

    def move_texture(self, texture: Union[Texture, str], from_cat: Union[TextureCategory, str, None], to_cat: Union[TextureCategory, str]) -> None:
        texture = self.get_texture(texture, None) if isinstance(texture, str) else texture
        if not texture:
            return None
        if from_cat is None:
            from_cat = self.get_texture_cat(texture)
        else:
            from_cat = self.get_texture_cat(from_cat) if isinstance(from_cat, str) else from_cat
        to_cat = self.get_texture_cat(to_cat) if isinstance(to_cat, str) else to_cat

        from_cat.unlink_item(texture) # no needed since link_item already unlinks from previous, but it is faster like this.
        to_cat.link_item(texture)


    ''' Creation Methods. '''
    def add_brush(self, brush: Brush) -> None:
        self.brushes[brush.id] = brush

    def add_texture(self, texture: Texture) -> None:
        self.textures[texture.id] = texture

    def new_brush_cat(self, cat_name: str = 'Untitled', cat_id: str = None, *brush_ids: List[str]) -> BrushCategory:
        brush_cat: BrushCategory = BrushCategory(cat_name, cat_id)
        for brush_id in brush_ids:
            brush_cat.link_item(brush_id)
        brush_cat.index = self.brush_cats_count
        self.brush_cats[brush_cat.id] = brush_cat
        self.active_brush_cat = brush_cat.id

        ## DBShelf.BRUSH_CAT.write(brush_cat)
        brush_cat.save()
        return brush_cat

    def new_texture_cat(self, cat_name: str = 'Untitled', cat_id: str = None, *texture_ids: List[str]) -> TextureCategory:
        texture_cat: TextureCategory = TextureCategory(cat_name, cat_id)
        for texture_id in texture_ids:
            texture_cat.link_item(texture_id)
        texture_cat.index = self.texture_cats_count
        self.texture_cats[texture_cat.id] = texture_cat
        self.active_texture_cat = texture_cat.id

        ## DBShelf.TEXTURE_CAT.write(texture_cat)
        texture_cat.save()
        return texture_cat

    def load_brushes_from_db(self) -> None:
        brushes_db_filepath: str = DBShelfPaths.BRUSH_SETTINGS
        brush_cats_db_filepath: str = DBShelfPaths.BRUSH_CAT
        config_filepath: str = SculptPlusPaths.CONFIG_FILE()
        if not path.exists(brush_cats_db_filepath + '.dat') or not path.isfile(brush_cats_db_filepath + '.dat'):
            print("WARN! BrushCategory Database not found: " + brush_cats_db_filepath)
            self.load_default_brushes()
            return
        if not path.exists(brushes_db_filepath + '.dat') or not path.isfile(brushes_db_filepath + '.dat'):
            print("WARN! Brush Database not found: " + brushes_db_filepath)
            return
        if not path.exists(config_filepath) or not path.isfile(config_filepath):
            print("WARN! Config file not found: " + config_filepath)
            return

        print("[SCULPT+] Loading config file...")
        config_data: dict = {}
        with open(config_filepath, 'r') as f:
            config_data = json.load(f)
            hotbar_config = config_data.pop('hotbar')
            self.hotbar.deserialize(hotbar_config)

        print("[SCULPT+] Loading brushes from database...")
        with shelve.open(brush_cats_db_filepath) as db__brush_cats:
            # print("Brush cats ids:", db__brush_cats.keys())
            for brush_cat_id, brush_cat_item in db__brush_cats.items():
                self.brush_cats[brush_cat_id] = brush_cat_item
        with shelve.open(brushes_db_filepath) as db__brushes:
            # print("Brushes ids:", db__brushes.keys())
            for brush_id, brush_item in db__brushes.items():
                self.brushes[brush_id] = brush_item

            # Resolve hotbar brushes.
            for i, brush_id in enumerate(list(self.hotbar.brushes)):
                if brush:= self.get_brush(brush_id):
                    # Make sure some Sculpt+ brush is selected.
                    if self.hotbar.selected is None:
                        brush.to_brush(bpy.context)
                        self.hotbar.selected = brush_id
                    break
                else:
                    self.hotbar.brushes[i] = None

        # Set Active Categories if cats exist.
        active_brush_cat: str = config_data['active_brush_cat']
        if active_brush_cat in self.brush_cats:
            self.active_brush_cat = active_brush_cat

        active_texture_cat: str = config_data['active_texture_cat']
        if active_texture_cat in self.texture_cats:
            self.active_texture_cat = active_texture_cat

    def load_brushes_from_datablock(self, cat_name: str, cat_id: str, brush_names: List[Union[str, BlBrush]], remove_brush_datablocks: bool = True) -> None:
        if remove_brush_datablocks:
            remove_brush = bpy.data.brushes.remove
            remove_image = bpy.data.images.remove
            remove_texture = bpy.data.textures.remove
        data_brushes: Dict[str, BlBrush] = bpy.data.brushes
        brush_cat: BrushCategory = self.new_brush_cat(cat_name, cat_id)
        undefined_texture_cat: TextureCategory = self.get_texture_cat('UNDEFINED')
        if undefined_texture_cat is None:
            undefined_texture_cat = self.new_texture_cat('Undefined', "UNDEFINED")
        with DBShelfManager.BRUSH_SETTINGS() as db, DBShelfManager.BRUSH_DEFAULTS() as db_defaults:
            for brush_name in brush_names:
                bl_brush: BlBrush = brush_name if isinstance(brush_name, BlBrush) else data_brushes.get(brush_name, None)
                if bl_brush is None:
                    continue

                brush: Brush = Brush(bl_brush)
                self.add_brush(brush)
                brush_cat.link_item(brush)

                bl_texture = bl_brush.texture
                if bl_texture:
                    if bl_texture.type == 'IMAGE' and (bl_image := bl_texture.image):
                        if bl_image.source in {'FILE', 'SEQUENCE'}:
                            image_path: Path = Path(bl_image.filepath_from_user())
                            if image_path.exists() and image_path.is_file():
                                texture: Texture = Texture(bl_texture)
                                self.add_texture(texture)
                                undefined_texture_cat.link_item(texture)

                                brush.texture_id = texture.id

                        if remove_brush_datablocks:
                            remove_image(bl_image)

                    if remove_brush_datablocks:
                        remove_texture(bl_texture)

                if remove_brush_datablocks:
                    remove_brush(bl_brush)

                db.write(brush)
                db_defaults.write(brush)

        return brush_cat

    def load_textures_from_datablock(self, cat_name: str, cat_id: str, image_names: List[Union[str, BlBrush]], remove_image_datablocks: bool = True) -> None:
        data_images: Dict[str, BlBrush] = bpy.data.images
        texture_cat: TextureCategory = self.new_texture_cat(cat_name, cat_id)

        class FakeBlTexture():
            def __init__(self, image):
                self.name = image.name
                self.image = image

        with DBShelfManager.BRUSH_SETTINGS() as db:
            for image_name in image_names:
                bl_image: BlImage = image_name if isinstance(image_name, BlImage) else data_images.get(image_name, None)
                if bl_image is None:
                    continue
                if bl_image.source not in {'FILE', 'SEQUENCE'}:
                    continue
                image_path: Path = Path(bl_image.filepath_from_user())
                if not image_path.exists() or not image_path.is_file():
                    continue

                texture: Texture = Texture(FakeBlTexture(bl_image))
                self.add_texture(texture)
                texture_cat.link_item(texture)
                db.write(texture_cat)

        # 3. Remove loaded brushes.
        if remove_image_datablocks:
            remove_image = data_images.remove
            for image_name in image_names:
                remove_image(image_name)

        return texture_cat

    def load_default_brushes(self) -> None:
        print("[SCULPT+] Loading default brushes...")
        brush_cat: BrushCategory = self.load_brushes_from_datablock('Default', 'DEFAULT', filtered_builtin_brush_names, remove_brush_datablocks=False)
        self.hotbar.brushes = [brush_id for brush_id in brush_cat.item_ids[:10]]
        brush_cat.load_icon(Icon.BRUSH_PENCIL_X.get_path())
        self.active_brush_cat = brush_cat
        # brush_cat.order = 0 # Sort order at Manager level.

    def duplicate_brush(self, base_brush_item: Union[Brush, str]) -> Brush:
        if isinstance(base_brush_item, str):
            return self.duplicate_brush(self.brushes[base_brush_item])
        if not isinstance(base_brush_item, Brush):
            return None
        base_brush_item.copy()

    def load_brushes_from_lib(self, cat_name: str, lib_path: str):
        # 1. load brushes (and textures) from lib.
        with bpy.data.libraries.load(lib_path) as (data_from, data_to):
            data_to.brushes = data_from.brushes
            # data_to.textures = data_from.textures
            # data_to.images = data_from.images

        # 2. Load brushes. Convert to brush objects.
        self.load_brushes_from_datablock(cat_name, None, data_to.brushes)

    def load_datablocks_from_lib(self, lib_path: str, datablocks: dict[str, list[str]]) -> None:
        with bpy.data.libraries.load(lib_path) as (data_from, data_to):
            for datablock_type, datablocks_ids in datablocks.items():
                # datablocks_ids_from = []
                setattr(data_to, datablock_type, datablocks_ids)

        if 'brushes' in datablocks and datablocks['brushes']:
            self.load_brushes_from_datablock('Blend-lib Cat', None, data_to.brushes)
        if 'images'  in datablocks and datablocks['images']:
            self.load_textures_from_datablock('Blend-lib Cat', None, data_to.images)

    def load_viewitems_from_lib(self, lib_path: str, type: str, items: List[Union[FakeViewItem_Brush, FakeViewItem_Texture]]) -> None:
        if not items:
            return

        with bpy.data.libraries.load(lib_path) as (data_from, data_to):
            if type == 'BRUSH':
                data_to.brushes = [brush.name for brush in items]
                # data_to.images = [brush.texture.name for brush in items if brush.texture is not None]
            elif type == 'TEXTURE':
                data_to.images = [texture.name for texture in items]

        if type == 'BRUSH':
            self.load_brushes_from_datablock('Blend-lib Cat', None, data_to.brushes)
        elif type == 'TEXTURE':
            self.load_textures_from_datablock('Blend-lib Cat', None, data_to.images)

    def new_texture_cat_from_directory(self, texture_dirpath: str) -> None:
        pass
        #texture = TexCatItem(texture_path)
        #self.textures[texture.id] = texture


    ''' Generic methods, load and save. '''
    def save_all(self) -> None:
        if not self.textures and not self.brushes:
            return
        if not self.texture_cats and self.brush_cats:
            return
        config_data = {
            'active_brush_cat'  : self.active_brush_cat.id   if self.active_brush_cat   else None,
            'active_texture_cat': self.active_texture_cat.id if self.active_texture_cat else None,
            'hotbar': self.hotbar.serialize(),
        }
        with open(SculptPlusPaths.CONFIG_FILE(), 'w') as f:
            json.dump(config_data, f, indent=4, ensure_ascii=True)

        for brush in self.brushes.values():
            brush.save()
        for brush_cat in self.brush_cats.values():
            brush_cat.save()
        for tex_cat in self.texture_cats.values():
            tex_cat.save()
        return
        for texture in self.textures.values():
            texture.save()
        for image in self.images.values():
            image.save()
