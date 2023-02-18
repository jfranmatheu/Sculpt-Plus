import os
from os.path import join, dirname, abspath, exists as path_exists, isfile
import sys
import pathlib
from pathlib import Path
import shelve
import pickle
from enum import Enum


def get_datadir() -> pathlib.Path:
    """
    Returns a parent directory path
    where persistent application data can be stored.

    # linux: ~/.local/share
    # macOS: ~/Library/Application Support
    # windows: C:/Users/<USER>/AppData/Roaming
    """

    home = pathlib.Path.home()

    if sys.platform == "win32":
        return home / "AppData/Roaming/Blender Foundation/Blender"
    elif sys.platform == "linux":
        return home / ".config/blender" # ".local/share/blender" ## $HOME/.config/blender/3.4/
    elif sys.platform == "darwin":
        return home / "Library/Application Support/Blender" ## /Users/$USER/Library/Application Support/Blender/3.4/

addon_data_dir = get_datadir() / "addon_data"
app_dir = addon_data_dir / __package__
temp_dir = app_dir / "temp"
data_dir = app_dir / "data"
data_brush_dir = data_dir / "brush"
data_texture_dir = data_dir / "texture"
version_file = app_dir / "version.ini"
management_config_file = data_dir / "config.json"

def ensure_paths():
    # First time creation.
    try:
        app_dir.mkdir(parents=True, exist_ok=True)

        if not version_file.exists():
            version_file.touch()

        # TODO: Check version changes.
        # Do versioning code if needed.

        # Update the registered version.
        with version_file.open('w', encoding='ascii') as file:
            from . import bl_info
            file.write(f"{bl_info['version']}\n")

        data_dir.mkdir(parents=False)
        # data_brush_dir.mkdir()
        # data_texture_dir.mkdir()
        temp_dir.mkdir()
        (data_brush_dir / "settings" / "defaults").mkdir(parents=True)
        (data_brush_dir / "cats").mkdir()
        (data_brush_dir / "previews").mkdir()
        (data_texture_dir / "settings" / "defaults").mkdir(parents=True)
        (data_texture_dir / "cats").mkdir()
        (data_texture_dir / "previews").mkdir()
        (data_texture_dir / "images").mkdir()
        (temp_dir / "fake_items").mkdir()
        (temp_dir / "thumbnails").mkdir()
        if not management_config_file.exists():
            management_config_file.touch()
            with management_config_file.open('w', encoding='ascii') as file:
                file.write('{ }')
    except FileExistsError:
        pass

ensure_paths()

class SculptPlusPaths(Enum):
    SRC = dirname(abspath(__file__))
    SRC_LIB = join(SRC, 'lib')
    SRC_LIB_IMAGES = join(SRC_LIB, 'images')
    SRC_LIB_IMAGES_ICONS = join(SRC_LIB_IMAGES, 'icons')
    SRC_LIB_IMAGES_BRUSHES = join(SRC_LIB_IMAGES, 'brushes')
    SRC_LIB_SCRIPTS = join(SRC_LIB, 'scripts')
    SRC_LIB_BLEND = join(SRC_LIB, 'blend')
    BLEND_EMPTY = join(SRC_LIB_BLEND, 'empty.blend')

    LIB_SHADERS = join(SRC_LIB, 'shaders')
    LIB_SHADERS_VERT = join(LIB_SHADERS, 'vert')
    LIB_SHADERS_FRAG = join(LIB_SHADERS, 'frag')
    LIB_SHADERS_BUILTIN = join(LIB_SHADERS, 'builtin')

    APP = str(app_dir)
    APP__DATA = str(data_dir)
    APP__TEMP = str(temp_dir)

    CONFIG_FILE = str(data_dir / 'config.json')
    HOTBAR_CONFIG = str(data_brush_dir / "hotbar.txt")

    DATA_BRUSH_SETTINGS = str(data_brush_dir / "settings")
    DATA_BRUSH_DEFAULTS = str(data_brush_dir / "settings" / "defaults")
    DATA_BRUSH_CATS = str(data_brush_dir / "cats")
    DATA_BRUSH_PREVIEWS = str(data_brush_dir / "previews")
    DATA_BRUSH_CAT_ICONS = str(data_brush_dir / "cats")

    DATA_TEXTURE_SETTINGS = str(data_texture_dir / "settings")
    # DATA_TEXTURE_DEFAULTS = str(data_texture_dir / "settings" / "default")
    DATA_TEXTURE_CATS = str(data_texture_dir / "cats")
    DATA_TEXTURE_PREVIEWS = str(data_texture_dir / "previews")
    DATA_TEXTURE_IMAGES = str(data_texture_dir / "images")
    DATA_TEXTURE_CAT_ICONS = str(data_texture_dir / "cats")

    TEMP_FAKE_ITEMS = str(temp_dir / "fake_items")
    TEMP_THUMBNAILS = str(temp_dir / "thumbnails")

    def __call__(self, *path):
        if not path:
            return self.value
        return join(self.value, *path)

    def read(self, *path) -> str:
        with open(self(*path), mode='r') as f:
            return f.read()


class ScriptPaths:
    GENERATE_THUMBNAILS = SculptPlusPaths.SRC_LIB_SCRIPTS('generate_thumbnails.py')
    GENERATE_NPZ_FROM_BLENDLIB = SculptPlusPaths.SRC_LIB_SCRIPTS('generate_images_n_thumbnails.py')
    EXPORT_BRUSHES_FROM_BLENDLIB = SculptPlusPaths.SRC_LIB_SCRIPTS('export_brushes_from_blendlib.py')
    CONVERT_TEXTURES_TO_PNG_FROM_BLENDLIB = SculptPlusPaths.SRC_LIB_SCRIPTS('convert_textures_to_png_from_blendlib.py')
    EXPORT_TEXTURES_FROM_DIRECTORY = SculptPlusPaths.SRC_LIB_SCRIPTS('export_textures_from_directory.py')
    GENERATE_NPY_FROM_IMAGE_PATHS = SculptPlusPaths.SRC_LIB_SCRIPTS('generate_npy_from_image_paths.py')


class ThumbnailPaths:
    @staticmethod
    def _GET_PATH(_path: SculptPlusPaths, item: str, ext: str = '.png', check_exists: bool = False) -> Path or str:
        item_id: str = item if isinstance(item, str) else item.id
        filepath: str = _path(item_id + ext)
        if not check_exists:
            return filepath
        path: Path = Path(filepath)
        return path if path.exists() and path.is_file() else None

    @classmethod
    def BRUSH(cls, brush, check_exists: bool = False) -> Path or None:
        return cls._GET_PATH(SculptPlusPaths.DATA_BRUSH_PREVIEWS, brush, ext='.png', check_exists=check_exists)

    @classmethod
    def TEXTURE(cls, texture, check_exists: bool = False) -> Path or None:
        return cls._GET_PATH(SculptPlusPaths.DATA_TEXTURE_PREVIEWS, texture, ext='.png', check_exists=check_exists)

    @classmethod
    def BRUSH_CAT(cls, cat, check_exists: bool = False) -> Path or None:
        return cls._GET_PATH(SculptPlusPaths.DATA_BRUSH_CAT_ICONS, cat, ext='.png', check_exists=check_exists)

    @classmethod
    def TEXTURE_CAT(cls, cat, check_exists: bool = False) -> Path or None:
        return cls._GET_PATH(SculptPlusPaths.DATA_TEXTURE_CAT_ICONS, cat, ext='.png', check_exists=check_exists)

    @classmethod
    def get_texture_image_path(cls, texture, check_exists: bool = False) -> Path or None:
        return cls._GET_PATH(SculptPlusPaths.DATA_TEXTURE_CAT_ICONS, texture, ext=texture.image.ext, check_exists=check_exists)

    @classmethod
    def remove_brush_previews(cls, brush_ids: list[str]) -> None:
        for brush_id in brush_ids:
            if path := cls.BRUSH(brush_id):
                path.unlink()

    @classmethod
    def remove_texture_previews(cls, tex_ids: list[str]) -> None:
        for tex_id in tex_ids:
            if path := cls.TEXTURE(tex_id):
                path.unlink()


class DBPickle(Enum):
    BRUSH_SETTINGS = SculptPlusPaths.DATA_BRUSH_SETTINGS
    BRUSH_DEFAULTS = SculptPlusPaths.DATA_BRUSH_DEFAULTS
    BRUSH_CAT = SculptPlusPaths.DATA_BRUSH_CATS
    TEXTURE_CAT = SculptPlusPaths.DATA_TEXTURE_CATS
    TEXTURES = SculptPlusPaths.DATA_TEXTURE_SETTINGS

    def load(self, item):
        item_id: str = item if isinstance(item, str) else item.id
        path: str = self.value(item_id)
        with open(path, 'rb') as f:
            return pickle.load(f)
    
    def write(self, item):
        path: str = self.value(item.id)
        with open(path, 'wb') as f:
            pickle.dump(item, f)

    def remove(self, item):
        item_id: str = item if isinstance(item, str) else item.id
        path: str = self.value(item_id)
        os.remove(path)



class DBShelfPaths:
    BRUSH_SETTINGS = SculptPlusPaths.APP__DATA('brush_settings')
    BRUSH_DEFAULTS = SculptPlusPaths.APP__DATA('brush_defaults')
    BRUSH_CAT = SculptPlusPaths.APP__DATA('brush_cats')
    TEXTURE_CAT = SculptPlusPaths.APP__DATA('texture_cats')
    TEXTURES = SculptPlusPaths.APP__DATA('textures')

    TEMPORAL = SculptPlusPaths.APP__TEMP('temporal_items')


class DBShelf(Enum):
    BRUSH_SETTINGS = DBShelfPaths.BRUSH_SETTINGS
    BRUSH_DEFAULTS = DBShelfPaths.BRUSH_DEFAULTS
    BRUSH_CAT = DBShelfPaths.BRUSH_CAT
    TEXTURE_CAT = DBShelfPaths.TEXTURE_CAT
    TEXTURES = DBShelfPaths.TEXTURES

    TEMPORAL = DBShelfPaths.TEMPORAL

    def destroy(self) -> None:
        Path(self.value).unlink()

    def items(self) -> dict:
        path: str = self.value # item.id
        with shelve.open(path) as db:
            return db.items()
    
    def values(self) -> list:
        path: str = self.value # item.id
        with shelve.open(path) as db:
            return list(db.values())

    def write(self, *items: tuple):
        path: str = self.value# item.id
        with shelve.open(path) as db:
            for item in items:
                db[item.id] = item

    def remove(self, *items: tuple[str]):
        path: str = self.value# item_id
        with shelve.open(path) as db:
            for item in items:
                item_id: str = item if isinstance(item, str) else item.id
                del db[item_id]

    def reset(self) -> None:
        """ Remove everything from this database. """
        db = shelve.open(self.value, flag='n')
        db.close()


class DBShelfManager:
    @classmethod
    def TEMPORAL(cls, cleanup: bool = True) -> 'DBShelfManager':
        return cls(DBShelfPaths.TEMPORAL, cleanup=cleanup)

    @classmethod
    def BRUSH_SETTINGS(cls) -> 'DBShelfManager':
        return cls(DBShelfPaths.BRUSH_SETTINGS)

    @classmethod
    def BRUSH_DEFAULTS(cls) -> 'DBShelfManager':
        return cls(DBShelfPaths.BRUSH_DEFAULTS)

    @classmethod
    def BRUSH_CAT(cls) -> 'DBShelfManager':
        return cls(DBShelfPaths.BRUSH_CAT)

    @classmethod
    def TEXTURE_CAT(cls) -> 'DBShelfManager':
        return cls(DBShelfPaths.TEXTURE_CAT)

    @classmethod
    def TEXTURE(cls) -> 'DBShelfManager':
        return cls(DBShelfPaths.TEXTURES)

    def __init__(self, path: str, cleanup: bool = False):
        self.db_path = path

        if cleanup:
            dat_filepath = Path(path + '.dat')
            if dat_filepath.exists() and dat_filepath.is_file():
                dat_filepath.unlink()
            dir_filepath = Path(path + '.dir')
            if dir_filepath.exists() and dir_filepath.is_file():
                dir_filepath.unlink()
            bak_filepath = Path(path + '.bak')
            if bak_filepath.exists() and bak_filepath.is_file():
                bak_filepath.unlink()

    def __enter__(self):
        self.db = shelve.open(self.db_path)
        return self

    def get(self, key: str):
        return self.db[key]

    def write(self, component):
        self.db[component.id] = component

    def remove(self, component):
        item_id: str = component if isinstance(component, str) else component.id
        del self.db[item_id]

    def get_items(self) -> list:
        return list(self.db.items())

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.db.close()

    def reset(self) -> None:
        """ Remove everything from this database. """
        self.db.close()
        self.db = shelve.open(self.db_path, flag='n')
