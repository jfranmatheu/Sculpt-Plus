from typing import Dict, Union, List, Set, Tuple
import shelve
from os import path
import json
from collections import OrderedDict
from pathlib import Path
from time import time

import bpy
from bpy.types import Brush as BlBrush, Texture as BlTexture, Image as BlImage

from sculpt_plus.path import DBShelf, SculptPlusPaths, DBShelfPaths, DBShelfManager, data_brush_dir, data_texture_dir
from .types.cat import BrushCategory, TextureCategory, Brush, Texture
from sculpt_plus.lib import Icon
from sculpt_plus.management.types.fake_item import FakeViewItem_Brush, FakeViewItem_Texture


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

    def __del__(self):
        self._selected = None
        self.alt_selected = None
        self._brushes.clear()
        self.alt_brushes.clear()

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
    active_sculpt_tool: str

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

    def __del__(self):
        self._active_brush = None
        self.active_texture = None
        self._active_brush_cat = None
        self._active_texture_cat = None
        self.active_sculpt_tool = None
        self.brushes.clear()
        self.textures.clear()
        self.brush_cats.clear()
        self.texture_cats.clear()
        del self.hotbar

    def __init__(self):
        self.initilized: bool = False
        self.is_data_loaded: bool = False

        self._active_brush_cat: str = ''
        self._active_texture_cat: str = ''
        self._active_brush: str = ''
        self._active_texture: str = ''
        self._active_sculpt_tool: str = ''

        self.brush_cats = OrderedDict()
        self.brushes = dict()

        self.texture_cats = OrderedDict()
        self.textures = dict()

        self.hotbar: HotbarManager = HotbarManager()

        self._remove_atexit__brushes = []
        self._remove_atexit__textures = []
        self._remove_atexit__brush_cats = []
        self._remove_atexit__texture_cats = []

    def ensure_data(self) -> None:
        if self.is_data_loaded:
            if self.brush_cats_count == 0 or self.brushes_count == 0:
                self.load_default_brushes()
            # print(self.brush_cats_count, self.brushes_count)
        else:
            self.load_data()

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
            self.active_sculpt_tool = brush.sculpt_tool

    @property
    def active_texture(self) -> str:
        return self._active_texture

    @active_texture.setter
    def active_texture(self, texture: Union[Texture, str]):
        texture_id = texture.id if isinstance(texture, Texture) else texture
        self._active_texture = texture_id

    @property
    def active_sculpt_tool(self) -> str:
        return self._active_sculpt_tool

    @active_sculpt_tool.setter
    def active_sculpt_tool(self, tool: Union[Brush, str]):
        self._active_sculpt_tool = tool.sculpt_tool if isinstance(tool, Brush) else tool

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
            if brush_cat := self.brush_cats.get(cat, None):
                return brush_cat
            for brush_cat in self.brush_cats.values():
                if brush_cat.name == cat:
                    return brush_cat
            return None
        if isinstance(cat, Brush):
            return self.brush_cats.get(cat.cat_id, None)
        return None

    def get_texture_cat(self, cat: Union[str, Texture, int]) -> TextureCategory:
        if isinstance(cat, int):
            for text_cat in self.texture_cats.values():
                if text_cat.index == cat:
                    return text_cat
            return None
        if isinstance(cat, str):
            if text_cat := self.texture_cats.get(cat, None):
                return text_cat
            for text_cat in self.texture_cats.values():
                if text_cat.name == cat:
                    return text_cat
            return None
        if isinstance(cat, Texture):
            return self.texture_cats.get(cat.cat_id, None)
        return None


    ''' Remove Methods. '''
    def remove_brush_item(self, brush_id: str) -> None:
        cat_item: Brush = self.brushes.pop(brush_id if isinstance(brush_id, str) else brush_id.id)
        self.get_brush_cat(cat_item).unlink_item(brush_id)
        self._remove_atexit__brushes.append(cat_item.id)
        del cat_item

        ## DBShelf.BRUSH_SETTINGS.remove(brush_id)
        ## DBShelf.BRUSH_DEFAULTS.remove(brush_id)

    def remove_texture_item(self, texture_id: str) -> None:
        cat_item: Texture = self.textures.pop(texture_id if isinstance(texture_id, str) else texture_id.id)
        self.get_texture_cat(cat_item).unlink_item(texture_id)
        self._remove_atexit__textures.append(cat_item.id)
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

        self._remove_atexit__brushes.extend(cat_item_ids)
        self._remove_atexit__brush_cats.append(cat.id)

        if brush_cat == act_brush_cat:
            if self.brush_cats_count != 0:
                self.active_brush_cat = list(self.brush_cats.keys())[0]

        brush_cat.clear()
        del brush_cat

        # DBShelf.BRUSH_CAT.remove(cat_id)
        # DBShelf.BRUSH_SETTINGS.remove(*cat_item_ids)
        # DBShelf.BRUSH_DEFAULTS.remove(*cat_item_ids)

    def remove_texture_cat(self, cat: Union[str, TextureCategory]) -> None:
        if not cat:
            return
        texture_cat: TextureCategory = self.texture_cats.pop(cat) if isinstance(cat, str) else self.texture_cats.pop(cat.id)
        if not texture_cat:
            return
        cat_item_ids: List[str] = texture_cat.item_ids
        for texture_id in cat_item_ids:
            del self.textures[texture_id]
        
        self._remove_atexit__textures.extend(cat_item_ids)
        self._remove_atexit__texture_cats.append(cat.id)

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
                    def_brush.to_brush(bpy.context)

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

    def new_brush_cat(self, cat_name: str = 'Untitled', cat_id: str = None, check_exists: bool = False, brush_items: List[Brush] = []) -> BrushCategory:
        if check_exists and (tex_cat := self.get_brush_cat(cat_name)):
            return tex_cat
        brush_cat: BrushCategory = BrushCategory(cat_name, cat_id)
        for brush_item in brush_items:
            brush_cat.link_item(brush_item)
        brush_cat.index = self.brush_cats_count
        self.brush_cats[brush_cat.id] = brush_cat
        self.active_brush_cat = brush_cat.id

        DBShelf.BRUSH_CAT.write(brush_cat)
        ## brush_cat.save()
        return brush_cat

    def new_texture_cat(self, cat_name: str = 'Untitled', cat_id: str = None, check_exists: bool = False, texture_items: List[Texture] = []) -> TextureCategory:
        if check_exists and (tex_cat := self.get_texture_cat(cat_name)):
            return tex_cat
        texture_cat: TextureCategory = TextureCategory(cat_name, cat_id)
        for texture_item in texture_items:
            texture_cat.link_item(texture_item)
        texture_cat.index = self.texture_cats_count
        self.texture_cats[texture_cat.id] = texture_cat
        self.active_texture_cat = texture_cat.id

        DBShelf.TEXTURE_CAT.write(texture_cat)
        ## texture_cat.save()
        return texture_cat

    def load_brushes_from_datablock(self, cat_name: str, cat_id: str, brush_names: List[Union[str, BlBrush]], fake_items: dict = {}, remove_brush_datablocks: bool = True) -> None:
        if remove_brush_datablocks:
            remove_brush = bpy.data.brushes.remove
            remove_image = bpy.data.images.remove
            remove_texture = bpy.data.textures.remove
        data_brushes: Dict[str, BlBrush] = bpy.data.brushes
        brush_cat: BrushCategory = self.new_brush_cat(cat_name, cat_id, check_exists=True)
        # undefined_texture_cat: TextureCategory = self.get_texture_cat('UNDEFINED')
        # if undefined_texture_cat is None:
        #     undefined_texture_cat = self.new_texture_cat('Undefined', "UNDEFINED")
        texture_cat: TextureCategory = self.new_texture_cat(cat_name, cat_id, check_exists=True)

        use_fake = fake_items is not None
        fake_brush = None
        fake_texture = None
        generate_thumbnails = not use_fake

        # with DBShelfManager.BRUSH_SETTINGS() as db, DBShelfManager.BRUSH_DEFAULTS() as db_defaults:
        for brush_name in brush_names:
            ## start_iter_time = time()
            bl_brush: BlBrush = brush_name if isinstance(brush_name, BlBrush) else data_brushes.get(brush_name, None)
            if bl_brush is None:
                continue

            if use_fake: fake_brush = fake_items.get(bl_brush.name, None)

            brush: Brush = Brush(bl_brush, fake_brush=fake_brush) #, generate_thumbnail=generate_thumbnails)
            self.add_brush(brush)
            brush_cat.link_item(brush)

            if bl_texture := bl_brush.texture:
                if bl_texture.type == 'IMAGE' and (bl_image := bl_texture.image):
                    if bl_image.source in {'FILE', 'SEQUENCE'} and bl_image.pixels:
                        image_path: Path = Path(bl_image.filepath_from_user())
                        if image_path.exists() and image_path.is_file():

                            if fake_brush: fake_texture = fake_brush.texture

                            texture: Texture = Texture(bl_texture, fake_texture=fake_texture) #, generate_thumbnail=generate_thumbnails) # NOTE: Marked as false to avoid waiting for infinity.)
                            self.add_texture(texture)
                            texture_cat.link_item(texture)

                            brush.texture_id = texture.id

                    if remove_brush_datablocks:
                        remove_image(bl_image)

                if remove_brush_datablocks:
                    remove_texture(bl_texture)

            if remove_brush_datablocks:
                remove_brush(bl_brush)

            #db.write(brush)
            #db_defaults.write(brush)
            ## print(f"[TIME] Brush {brush.name} -> {round(time() - start_iter_time, 3)} seconds")

        return brush_cat

    def load_textures_from_datablock(self, cat_name: str, cat_id: str, image_names: List[Union[str, BlBrush]], fake_items: List[FakeViewItem_Texture]=None, remove_image_datablocks: bool = True) -> None:
        data_images: Dict[str, BlBrush] = bpy.data.images
        texture_cat: TextureCategory = self.new_texture_cat(cat_name, cat_id)

        class FakeBlTexture():
            def __init__(self, image):
                self.name = image.name
                self.image = image

        use_fake = fake_items is not None
        generate_thumbnails = not use_fake

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
                
                fake_texture = fake_items.get(bl_image.name, None) if use_fake else None

                texture: Texture = Texture(FakeBlTexture(bl_image), fake_texture=fake_texture, generate_thumbnail=generate_thumbnails)
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
        brush_cat: BrushCategory = self.load_brushes_from_datablock('Default', None, filtered_builtin_brush_names, remove_brush_datablocks=False)
        self.hotbar.brushes = [brush_id for brush_id in brush_cat.item_ids[:10]]
        brush_cat.load_icon(Icon.BRUSH_PENCIL_X.get_path())
        self.active_brush_cat = brush_cat
        # brush_cat.order = 0 # Sort order at Manager level.

    def duplicate_brush(self, base_brush_item: Union[Brush, str]) -> Brush:
        if isinstance(base_brush_item, str):
            return self.duplicate_brush(self.brushes[base_brush_item])
        if not isinstance(base_brush_item, Brush):
            return None
        self.add_brush(base_brush_item.copy())

    def load_brushes_from_lib(self, cat_name: str, lib_path: str):
        # 1. load brushes (and textures) from lib.
        with bpy.data.libraries.load(lib_path) as (data_from, data_to):
            data_to.brushes = data_from.brushes
            # data_to.textures = data_from.textures
            # data_to.images = data_from.images

        # 2. Load brushes. Convert to brush objects.
        self.load_brushes_from_datablock(cat_name, None, data_to.brushes)

    def load_datablocks_from_lib(self, lib_path: str, datablocks: dict[str, list[str]]) -> None:
        with bpy.data.libraries.load(lib_path, link=True) as (data_from, data_to):
            for datablock_type, datablocks_ids in datablocks.items():
                # datablocks_ids_from = []
                setattr(data_to, datablock_type, datablocks_ids)

        if 'brushes' in datablocks and datablocks['brushes']:
            self.load_brushes_from_datablock('Blend-lib Cat', None, data_to.brushes, remove_brush_datablocks=True)
        if 'images'  in datablocks and datablocks['images']:
            self.load_textures_from_datablock('Blend-lib Cat', None, data_to.images, remove_image_datablocks=True)

        if lib := bpy.data.libraries.get(Path(lib_path).name, None):
            bpy.data.libraries.remove(lib, do_unlink=True)


    def load_viewitems_from_lib(self, lib_path: str, type: str, items: List[Union[FakeViewItem_Brush, FakeViewItem_Texture]]) -> None:
        if not items:
            return

        cat_name: str = Path(lib_path).stem

        dict_fake_items: dict[str, str] = {}
        def _prepare_item(item, datablocks) -> bool:
            if item is None:
                return False
            if item.name in datablocks:
                # Ensure that the datablock does not exist,
                # to avoid name collision when creating the item.
                datablocks.remove(datablocks[item.name])
            dict_fake_items[item.name] = item
            return True

        start_time = time()
        with bpy.data.libraries.load(lib_path, link=True) as (data_from, data_to):
            if type == 'BRUSH':
                data_to.brushes = [brush.name for brush in items if _prepare_item(brush, bpy.data.brushes)]
                # data_to.textures = [brush.texture.name for brush in items if brush.texture is not None] #_prepare_item(brush.texture, bpy.data.textures)]
            elif type == 'TEXTURE':
                data_to.images = [texture.name for texture in items if _prepare_item(texture, bpy.data.images)]
        print("[TIME] Linking datablocks from library -> %.2fs" % (time() - start_time))

        #print(dict_name_id_relation.keys())
        start_time = time()
        if type == 'BRUSH':
            self.load_brushes_from_datablock(cat_name, None, data_to.brushes, fake_items=dict_fake_items, remove_brush_datablocks=True)
            # self._load_viewitem_brushes_from_datablock(cat_name, items, data_to.brushes)
        elif type == 'TEXTURE':
            self.load_textures_from_datablock(cat_name, None, data_to.images, fake_items=dict_fake_items, remove_image_datablocks=True)
        print("[TIME] Create items from datablocks -> %.2fs" % (time() - start_time))

        if lib := bpy.data.libraries.get(Path(lib_path).name, None):
            bpy.data.libraries.remove(lib, do_unlink=True)
        del dict_fake_items
        del items


    def new_texture_cat_from_directory(self, texture_dirpath: str) -> None:
        pass
        #texture = TexCatItem(texture_path)
        #self.textures[texture.id] = texture


    def load_brushes_from_temporal_data(self) -> None:
        ''' Load Brushes data from temporal (fake items) data. '''
        # Get fake items data in temporal files.
        pass


    ''' Generic methods, load and save. '''
    def load_data(self) -> None:
        self.is_data_loaded = True
        brushes_db_filepath: str = DBShelfPaths.BRUSH_SETTINGS
        brush_cats_db_filepath: str = DBShelfPaths.BRUSH_CAT
        config_filepath: str = SculptPlusPaths.CONFIG_FILE()
        if not path.exists(brush_cats_db_filepath + '.dat') or not path.isfile(brush_cats_db_filepath + '.dat'):
            print("WARN! BrushCategory Database not found: " + brush_cats_db_filepath)
            self.load_default_brushes()
            return
        if not path.exists(brushes_db_filepath + '.dat') or not path.isfile(brushes_db_filepath + '.dat'):
            print("WARN! Brush Database not found: " + brushes_db_filepath)
            self.load_default_brushes()
            return
        if not path.exists(config_filepath) or not path.isfile(config_filepath):
            print("WARN! Config file not found: " + config_filepath)
            self.load_default_brushes()
            return

        print("[SCULPT+] Loading brushes from database...")
        with DBShelfManager.BRUSH_SETTINGS() as shelf_manager__brushes:
            for (brush_id, brush_data) in shelf_manager__brushes.get_items():
                print("\t> ", brush_data.name)
                self.brushes[brush_id] = brush_data

        print("[SCULPT+] Loading brush categories from database...")
        with DBShelfManager.BRUSH_CAT() as shelf_manager__brush_cats:
            for (brush_cat_id, brush_cat_data) in shelf_manager__brush_cats.get_items():
                print("\t> ", brush_cat_data.name)
                self.brush_cats[brush_cat_id] = brush_cat_data

        print("[SCULPT+] Loading textures from database...")
        with DBShelfManager.TEXTURE() as shelf_manager__textures:
            for (texture_id, texture_data) in shelf_manager__textures.get_items():
                print("\t> ", texture_data.name)
                self.textures[texture_id] = texture_data

        print("[SCULPT+] Loading texture categories from database...")
        with DBShelfManager.TEXTURE_CAT() as shelf_manager__texture_cats:
            for (texture_cat_id, texture_cat_data) in shelf_manager__texture_cats.get_items():
                print("\t> ", texture_cat_data.name)
                self.texture_cats[texture_cat_id] = texture_cat_data

        # TODO: Make a brush initializer handler timer.
        # That checks for active brush / active texture. Hotbar selected etc.
        # Ensure that the named brush/texture exist, and select it '.to_brush'.
        # If not, put null values into those fields.
        # Exit condition: enters in sculpt mode and above process done.
        # Continue condition: not in sculpt mode, wait for 1 second or so.
        # Note: Maybe can use a msgbus trigger instead.

        print("[SCULPT+] Loading config file...")
        config_data: dict = {}
        with open(config_filepath, 'r') as f:
            config_data = json.load(f)
            print("[SCULPT+] Loading hotbar config...")
            hotbar_config = config_data.pop('hotbar')
            self.hotbar.deserialize(hotbar_config)

        # Set Active Categories if cats exist.
        active_brush_cat: str = config_data['active_brush_cat']
        if active_brush_cat in self.brush_cats:
            self.active_brush_cat = active_brush_cat

        active_texture_cat: str = config_data['active_texture_cat']
        if active_texture_cat in self.texture_cats:
            self.active_texture_cat = active_texture_cat

        active_brush: str = config_data['active_brush']
        if active_brush in self.brushes:
            self.active_brush = active_brush

        active_texture: str = config_data['active_texture']
        if active_texture in self.textures:
            self.active_texture = active_texture

        if self.brushes_count == 0 or self.brush_cats_count == 0:
            self.load_default_brushes()

    def save_all(self) -> None:
        if not self.brushes_count and not self.textures_count and not self.brush_cats_count and not self.texture_cats_count:
            print("[Sculpt+] No data to save...")
            return
        print("[Sculpt+] Saving UI config...")
        config_data = {
            'active_brush': self._active_brush if self._active_brush else None,
            'active_texture': self._active_texture if self._active_texture else None,
            'active_brush_cat'  : self._active_brush_cat   if self._active_brush_cat   else None,
            'active_texture_cat': self._active_texture_cat if self._active_texture_cat else None,
            'hotbar': self.hotbar.serialize(),
        }
        with open(SculptPlusPaths.CONFIG_FILE(), 'w') as f:
            json.dump(config_data, f, indent=4, ensure_ascii=True)

        if self.brushes_count != 0:
            print("[Sculpt+] Saving brushes..")
            with DBShelfManager.BRUSH_SETTINGS() as shelf_manager__brushes:
                for brush in self.brushes.values():
                    shelf_manager__brushes.write(brush)
                    # brush.save()
                for remove_brush in self._remove_atexit__brushes:
                    shelf_manager__brushes.remove(remove_brush)
                self._remove_atexit__brushes.clear()
        if self.textures_count != 0:
            print("[Sculpt+] Saving textures..")
            with DBShelfManager.TEXTURE() as shelf_manager__textures:
                for texture in self.textures.values():
                    shelf_manager__textures.write(texture)
                    # texture.save()
                for remove_texture in self._remove_atexit__textures:
                    shelf_manager__textures.remove(remove_texture)
                self._remove_atexit__textures.clear()
        if self.brush_cats_count != 0:
            print("[Sculpt+] Saving brush_cats..")
            with DBShelfManager.BRUSH_CAT() as shelf_manager__brush_cats:
                for brush_cat in self.brush_cats.values():
                    shelf_manager__brush_cats.write(brush_cat)
                    print("\t> ", brush_cat.name)
                    # brush_cat.save()
                for remove_brush_cat in self._remove_atexit__brush_cats:
                    shelf_manager__brush_cats.remove(remove_brush_cat)
                self._remove_atexit__brush_cats.clear()
        if self.texture_cats_count != 0:
            print("[Sculpt+] Saving texture_cats..")
            with DBShelfManager.TEXTURE_CAT() as shelf_manager__texture_cats:
                for tex_cat in self.texture_cats.values():
                    shelf_manager__texture_cats.write(tex_cat)
                    print("\t> ", tex_cat.name)
                    # tex_cat.save()
                for remove_texture_cat in self._remove_atexit__texture_cats:
                    shelf_manager__texture_cats.remove(remove_texture_cat)
                self._remove_atexit__texture_cats.clear()

