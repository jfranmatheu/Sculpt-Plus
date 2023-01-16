from uuid import uuid4
from typing import List, Dict, Union
from pathlib import Path
from copy import deepcopy

from .image import Thumbnail
from sculpt_plus.path import DBPickle, DBShelf
from sculpt_plus.sculpt_hotbar.di import DiText, DiRct


class CategoryItem(object):
    fav: bool # Is favourite item.
    id: str
    cat_id: str
    type: str = 'NONE'
    # cat: Union['BrushCategory', 'TextureCategory']
    db_idname: str = 'undefined'
    thumbnail: Thumbnail

    def __init__(self, cat=None, _save=False, custom_id: str = None):
        super(CategoryItem, self).__init__()
        self.id = uuid4().hex if custom_id is None else custom_id
        self.fav = False
        self.cat_id = cat
        self.thumbnail: Thumbnail = Thumbnail.empty(self)

        #if _save:
        #    self._save()
        if _save:
            self.save_default()

        self.init()

    def init(self):
        pass

    def rename(self, new_name: str) -> None:
        self.name = new_name
        # self.save()

    def copy(self) -> 'CategoryItem':
        item_copy = deepcopy(self)
        item_copy.name = self.name + ' copy'
        item_copy.id = uuid4().hex
        ## item_copy.save()
        item_copy.save_default()
        self.cat.link_item(item_copy)
        return item_copy

    @property
    def cat(self): # -> Union['BrushCategory', 'TextureCategory']:
        ''' Property utility to get the brush category from Manager.instance. '''
        from ..manager import Manager
        if self.type == 'BRUSH':
            return Manager.get().get_brush_cat(self)
        elif self.type == 'TEXTURE':
            return Manager.get().get_texture_cat(self)

    def _save(self) -> None:
        ## self.save()
        self.save_default()

    def save(self) -> None:
        ''' Save the brush category to the database. '''
        pass

    def save_default(self) -> None:
        pass

    def draw_preview(self, p, s, act: bool = False, fallback = None, opacity: float = 1) -> None:
        if self.thumbnail and self.thumbnail.is_valid:
            self.thumbnail.draw(p, s, act, opacity=opacity)
        elif fallback is not None:
            fallback(p, s, act)
            if self.thumbnail is not None and self.thumbnail.is_loading:
                DiRct(p, s, (0, 0, 0, .5))
                DiText(p, "Loading...", 11, 1)


class BrushCatItem(CategoryItem):
    type: str = 'BRUSH'
    # cat: 'BrushCategory'
    db_idname: str = 'brushes'

    def save(self) -> None:
        ''' Save the brush category to the database. '''
        DBShelf.BRUSH_SETTINGS.write(self)

    def save_default(self) -> None:
        DBShelf.BRUSH_DEFAULTS.write(self)


class TextureCatItem(CategoryItem):
    type: str = 'TEXTURE'
    # cat: 'TextureCategory'
    db_idname: str = 'textures'

    def save(self) -> None:
        ''' Save the brush category to the database. '''
        DBShelf.TEXTURES.write(self)

    def save_default(self) -> None:
        pass
