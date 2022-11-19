import os
from os.path import join, dirname, abspath
import sys
import pathlib
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
        return home / ".local/share/blender"
    elif sys.platform == "darwin":
        return home / "Library/Application Support/"

addon_data_dir = get_datadir() / "addon_data"
addon_data_dir = addon_data_dir / __package__
brush_sets_dir = addon_data_dir / "brushes"
config_file = addon_data_dir / "config.ini"

# First time creation.
try:
    addon_data_dir.mkdir(parents=True)
    brush_sets_dir.mkdir(parents=False)
except FileExistsError:
    pass

class SculptPlusPaths(Enum):
    SRC = dirname(abspath(__file__))
    SRC_LIB = join(SRC, 'lib')
    SRC_LIB_IMAGES = join(SRC_LIB, 'images')

    APP_DATA = str(addon_data_dir)
    DATA_BRUSHES = str(brush_sets_dir)
    DATA_BRUSH_ICONS = str(brush_sets_dir / "br_icons")
    DATA_CATS = str(brush_sets_dir / "cats")
    DATA_CAT_ICONS = str(brush_sets_dir / "cat_icons")

    def __call__(self, *path):
        if not path:
            return self.value
        return join(self.value, *path)
