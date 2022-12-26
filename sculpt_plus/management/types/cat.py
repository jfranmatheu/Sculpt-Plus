from uuid import uuid4
from typing import List, Dict, Union
from pathlib import Path
from copy import deepcopy

from .brush import Brush
from .image import Image, Thumbnail
from .texture import Texture

from sculpt_plus.path import ThumbnailPaths, DBShelf, DBShelfManager


class Category(object):
    id: str
    name: str
    index: int
    item_ids: List[str]
    items: Union[Brush, Texture]
    icon: Thumbnail
    items_count: int
    type: str

    def __init__(self, name: str = 'Untitled Category', _id: str = None):
        self.id: str = _id if _id else uuid4().hex
        self.name: str = name
        self.index: int = 0
        self.icon: Thumbnail = None
        self.item_ids: List[str] = []
        print(f"New Category {self.id} with name {self.name}")
        ## self.save()

    @property
    def items_count(self) -> int:
        return len(self.item_ids)

    def get_items(self, all_items: Dict[str, Union[Brush, Texture]]) -> List[Union[Brush, Texture]]:
        return [all_items[id] for id in self.item_ids]

    def link_item(self, item: Union[Brush, Texture]) -> None:
        if item.cat_id:
            item.cat.unlink_item(item)
        self.item_ids.append(item.id)
        item.cat_id = self.id

    def unlink_item(self, item: Union[Brush, Texture]) -> None:
        self.item_ids.remove(item.id)
        item.cat_id = None

    def move_up(self) -> None:
        self.index = max(0, self.index - 1)

    def move_down(self) -> None:
        self.index += 1

    def clear(self) -> None:
        self.item_ids.clear()

    def reset(self) -> None:
        pass

    def save(self) -> None:
        ''' Save the brush category to the database. '''
        pass

    def load_icon(self, filepath: Union[str, Path]) -> str:
        if self.icon is not None:
            del self.icon
        self.icon = Thumbnail(filepath, self.id, 'CAT_' + self.type)
        return self.icon.filepath

    def draw_preview(self, p, s, act: bool = False, fallback=None) -> None:
        if self.icon:
            self.icon.draw(p, s, act)
        elif fallback:
            fallback(p, s, act)


class BrushCategory(Category):
    type: str = 'BRUSH'

    @property
    def items(self) -> List[Brush]:
        from ..manager import Manager
        return self.get_items(Manager.get().brushes)

    def reset(self) -> None:
        from ..manager import Manager
        Manager.get().reset_brush_cat(self)
    
    def save(self) -> None:
        DBShelf.BRUSH_CAT.write(self)

    def save_default(self) -> None:
        with DBShelfManager.BRUSH_DEFAULTS() as shelf:
            for b in self.items:
                shelf.write(b)

    def reset_default(self) -> None:
        from sculpt_plus.props import Props
        with DBShelfManager.BRUSH_DEFAULTS() as def_shelf, DBShelfManager.BRUSH_SETTINGS() as shelf:
            for b in self.items:
                def_brush = def_shelf.get(b.id)
                # b.from_brush(def_brush)
                shelf.write(def_brush)
                Props.BrushManager().brushes[b.id] = def_brush

    def __del__(self) -> None:
        if path:= ThumbnailPaths.BRUSH_CAT(self, check_exists=True):
            path.unlink()
        DBShelf.BRUSH_CAT.remove(self)


class TextureCategory(Category):
    type: str = 'TEXTURE'

    @property
    def items(self) -> List[Texture]:
        from ..manager import Manager
        return self.get_items(Manager.get().textures)

    def reset(self) -> None:
        from ..manager import Manager
        Manager.get().reset_texture_cat(self)

    def save(self) -> None:
        DBShelf.TEXTURE_CAT.write(self)

    def save_default(self) -> None:
        pass
    
    def reset_default(self) -> None:
        pass

    def __del__(self) -> None:
        if path:= ThumbnailPaths.TEXTURE_CAT(self, check_exists=True):
            path.unlink()
        ## DBShelf.TEXTURE_CAT.remove(self)


# Alias.
TexCat = TextureCategory
BruCat = BrushCategory
# TexCatItem = TextureCatItem
# BruCatItem = BrushCatItem
