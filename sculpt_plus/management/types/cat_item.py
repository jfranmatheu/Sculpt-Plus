from uuid import uuid4
from copy import deepcopy
from colorsys import hsv_to_rgb

from mathutils import Vector

from .image import Thumbnail
from ..thumbnailer import Thumbnailer
from sculpt_plus.path import DBShelf
from sculpt_plus.lib import Icon
from sculpt_plus.utils.math import map_value
from sculpt_plus.sculpt_hotbar.di import DiIcoCol, DiText, DiRct, DiCage, DiBr, DiIcoOpGamHl


class CategoryItem(object):
    fav: bool # Is favourite item.
    id: str
    cat_id: str
    type: str = 'NONE'
    # cat: Union['BrushCategory', 'TextureCategory']
    db_idname: str = 'undefined'
    thumbnail: Thumbnail

    def __init__(self, cat=None, _save=False, custom_id: str = None):
        # super(CategoryItem, self).__init__()
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

    def draw_preview(self, p: Vector, s: Vector, act: bool = False, opacity: float = 1, parent_widget = None, fallback=None) -> None:
        if self.thumbnail and self.thumbnail.is_valid:
            self.thumbnail.draw(p, s, act, opacity=opacity)
        elif fallback is not None:
            # error = self.thumbnail.is_error or self.thumbnail.is_unsupported
            fallback(p, s, act, opacity) # self.thumbnail)


class BrushCatItem(CategoryItem):
    type: str = 'BRUSH'
    # cat: 'BrushCategory'
    db_idname: str = 'brushes'

    def save(self) -> None:
        ''' Save the brush category to the database. '''
        DBShelf.BRUSH_SETTINGS.write(self)

    def save_default(self) -> None:
        DBShelf.BRUSH_DEFAULTS.write(self)

    def draw_preview(self, p: Vector, s: Vector, act: bool = False, opacity: float = 1, view_widget = None, fallback=None) -> None:
        if self.thumbnail and self.thumbnail.is_valid:
            self.thumbnail.draw(p, s, act, opacity=opacity)
        elif fallback is not None:
            fallback(p, s, act, opacity)
        else:
            DiBr(p, s, self.sculpt_tool, act)
            if self.thumbnail.is_loading:
                DiRct(p, s, (0, 0, 0, .5*opacity))
                DiText(p+Vector((2, 2)), "Loading...", 12, 1, shadow_props={})
            elif self.use_custom_icon and self.icon_filepath:
                Thumbnailer.push(self.thumbnail)


class TextureCatItem(CategoryItem):
    type: str = 'TEXTURE'
    # cat: 'TextureCategory'
    db_idname: str = 'textures'

    def save(self) -> None:
        ''' Save the brush category to the database. '''
        DBShelf.TEXTURES.write(self)

    def save_default(self) -> None:
        pass

    def draw_preview(self, p: Vector, s: Vector, act: bool = False, opacity: float = 1, view_widget = None, fallback=None) -> None:
        if self.thumbnail and self.thumbnail.is_valid:
            self.thumbnail.draw(p, s, act, opacity)
        elif fallback is not None:
            # error = self.thumbnail.is_error or self.thumbnail.is_unsupported
            fallback(p, s, act, opacity)
        elif self.thumbnail is not None:
            if self.thumbnail.is_unsupported:
                #_pad = s.x *.1
                #pad = Vector((_pad, _pad))
                #ico_p = p + pad
                #ico_s = s - pad * 2
                format = self.thumbnail.file_format
                if format == 'PSD':
                    DiIcoOpGamHl(p, s, Icon.FILE_PSD_1, 0.8*opacity, int(act))
                    # DiIcoCol(ico_p, ico_s, Icon.FILE_PSD_2, color)
            else:
                if view_widget:
                    rel_pos = p - view_widget.view_pos
                    x = rel_pos.x / view_widget.view_size.x
                    y = (rel_pos.y + view_widget.scroll) / view_widget.view_size.y
                    x = map_value(x, (0, 1), (.2, .8))
                    color = (*hsv_to_rgb(y, x, 0.9), 0.9 * opacity)
                else:
                    color = (.9, .9, .9, .9*opacity)

                DiIcoCol(p, s, Icon.TEXTURE_OPACITY, color)
                if self.thumbnail.is_loading:
                    DiRct(p, s, (0, 0, 0, .5*opacity))
                    DiText(p+Vector((2, 2)), "Loading...", 12, 1, shadow_props={})
                else:
                    Thumbnailer.push(self.thumbnail)
