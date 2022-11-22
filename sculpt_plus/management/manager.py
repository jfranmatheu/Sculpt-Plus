from typing import Dict, Union, List, Set, Tuple
import shelve

from bpy.types import Brush as BlBrush, Texture as BlTexture, Image as BlImage

from sculpt_plus.path import SculptPlusPaths
from .types.cat import BruCat, TexCat, TexCatItem, BruCatItem
from .types.brush import Brush
from .types.texture import Texture


builtin_brush_names = (
    'Clay Strips',
    'Blob', 'Inflate/Deflate',
    'Draw Sharp', 'Crease', 'Pinch/Magnify',

    'Grab',
    'Elastic Deform',
    'Snake Hook',

    'Scrape/Peaks',
    'Pose', 'Cloth',
    #'Mask', 'Draw Face Sets'
)

class Manager:
    _instance = None

    brush_cats: Dict[str, BruCat]
    brushes: Dict[str, Brush]
    texture_cats: Dict[str, TexCat]
    textures: Dict[str, Texture]

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Manager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.brush_cats = {}
        self.brushes = {}

        self.texture_cats = {}
        self.textures = {}

    ''' Getters. '''
    @property
    def brush_list(self) -> List[Brush]:
        return self.brushes.values()

    @property
    def texture_list(self) -> List[Texture]:
        return self.textures.values()

    def get_brush(self, brush_id: str) -> Brush:
        return self.brushes[brush_id]

    def get_texture(self, texture_id: str) -> Texture:
        return self.textures[texture_id]

    def get_brush_cat(self, cat: Union[str, BruCatItem]) -> TexCat:
        return self.brush_cats[cat if isinstance(cat, str) else cat.cat_id]

    def get_texture_cat(self, cat: Union[str, TexCatItem]) -> TexCat:
        return self.texture_cats[cat if isinstance(cat, str) else cat.cat_id]


    ''' Remove Methods. '''
    @staticmethod
    def remove_db_entries(db_idname: str, *entries: str) -> None:
        path = SculptPlusPaths.APP_DATA(db_idname + '.db')
        with shelve.open(path) as db:
            for entry_idname in entries:
                del db[entry_idname]

    def remove_brush_item(self, brush_id: str) -> None:
        cat_item: BruCatItem = self.brushes.pop(brush_id)
        self.get_brush_cat(cat_item).items.remove(brush_id)
        del cat_item

        Manager.remove_db_entries("brushes", brush_id)

    def remove_texture_item(self, texture_id: str) -> None:
        cat_item: TexCatItem = self.textures.pop(texture_id)
        self.get_texture_cat(cat_item).items.remove_item(texture_id)
        del cat_item

        Manager.remove_db_entries("textures", texture_id)

    def remove_brush_cat(self, cat_id: str) -> None:
        brush_cat: BruCat = self.brush_cats.pop(cat_id)
        cat_item_ids: List[str] = brush_cat.item_ids
        for brush_id in cat_item_ids:
            del self.brushes[brush_id]
        brush_cat.items.clear()
        del brush_cat

        Manager.remove_db_entries("brush_cats", cat_id)
        Manager.remove_db_entries("brushes", *cat_item_ids)
    
    def remove_texture_cat(self, cat_id: str) -> None:
        texture_cat: TexCat = self.texture_cats.pop(cat_id)
        cat_item_ids: List[str] = texture_cat.item_ids
        for texture_id in cat_item_ids:
            del self.textures[texture_id]
        texture_cat.items.clear()
        del texture_cat

        Manager.remove_db_entries("texture_cats", cat_id)
        Manager.remove_db_entries("textures", *cat_item_ids)


    ''' Creation Methods. '''
    def duplicate_brush(self, base_brush_item: Union[BruCatItem, str]) -> Brush:
        if isinstance(base_brush_item, str):
            return self.new_brush(self.brushes[base_brush_item])
        if not isinstance(base_brush_item, BruCatItem):
            return None
        cat: BruCat = self.get_brush_cat(base_brush_item)
        new_brush_item: BruCatItem = base_brush_item.copy()
        cat.add_item(new_brush_item)


    def add_brushes_from_lib(self, lib_path: str):
        pass

    def add_texture_from_path(self, texture_path: str) -> None:
        texture = Texture(texture_path)
        self.textures[texture.id] = texture
