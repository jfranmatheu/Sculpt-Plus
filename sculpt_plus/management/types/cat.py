from uuid import uuid4
from typing import List, Dict, Union
from pathlib import Path

from .brush import Brush
from .image import Image
from .serializable import Serializable


class CategoryItem(Serializable):
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

    @classmethod
    def from_cat_item(cls, cat_item: 'CategoryItem') -> 'CategoryItem':
        pass

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

    @property
    def item_ids(self) -> List[str]:
        return [item.data_id for item in self.items]

    def add_item(self, data: Union[Brush, Image, str]) -> CategoryItem:
        item = CategoryItem(data, self.id)
        self.items.append(item)
        return item

class BrushCategory(Category):
    items: List[BrushCategoryItem]

    def add_item(self, data: Union[Brush, Image, str, BrushCategoryItem]) -> BrushCategoryItem:
        if isinstance(data, BrushCategoryItem):
            self.items.append(data)
            return data

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
TexCatItem = TextureCategoryItem
BruCatItem = BrushCategoryItem
