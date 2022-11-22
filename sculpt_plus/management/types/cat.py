from uuid import uuid4
from typing import List, Dict, Union
from pathlib import Path

from .brush import Brush
from .image import Image
from .serializable import Serializable


class CategoryItem(Serializable):
    id: str
    name: str
    fav: bool # Is favourite item.
    cat_id: str
    data_id: str
    type: str = 'NONE'

    def __init__(self, data: Union[Brush, Image, str], cat: Union['BrushCategory', 'TextureCategory', str]):
        self.fav = False
        self.data_id = data if isinstance(data, str) else data.id
        self.cat_id  = cat if isinstance(cat, str) else cat.id

    @property
    def id(self) -> str:
        return self.data.id

    @property
    def name(self) -> str:
        return self.data.name

class BrushCategoryItem(CategoryItem):
    data: Brush
    type: str = 'BRUSH'

class TextureCategoryItem(CategoryItem):
    data: Image
    type: str = 'TEXTURE'

class Category(Serializable):
    id: str
    name: str
    items: List[CategoryItem]

    def __init__(self, name: str = 'Untitled Category'):
        self.id: str = uuid4().hex
        self.name: str = name

        self.items = []

    def add_item(self, data: Union[Brush, Image, str]) -> CategoryItem:
        item = CategoryItem(data, self.id)
        self._items.append(item)
        return item

class BrushCategory(Category):
    items: List[BrushCategoryItem]

    def add_item(self, data: Union[Brush, Image, str]) -> BrushCategoryItem:
        item = BrushCategoryItem(data, self.id)
        self._items.append(item)
        return item

class TextureCategory(Category):
    items: List[TextureCategoryItem]

    def add_item(self, data: Union[Brush, Image, str]) -> TextureCategoryItem:
        item = TextureCategoryItem(data, self.id)
        self._items.append(item)
        return item



# Alias.
TexCat = TextureCategory
BruCat = BrushCategory
