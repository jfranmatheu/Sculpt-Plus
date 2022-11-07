import os
from os.path import join, dirname, abspath
import sys
import pathlib


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
brush_sets_dir = addon_data_dir / "brush_sets"
config_file = addon_data_dir / "config.ini"

# First time creation.
try:
    addon_data_dir.mkdir(parents=True)
    brush_sets_dir.mkdir(parents=False)
except FileExistsError:
    pass

class SculptPlusPaths:
    SRC = dirname(abspath(__file__))
    SRC_LIB = join(SRC, 'lib')
    SRC_LIB_IMAGES = join(SRC_LIB, 'images')

    APP_DATA = addon_data_dir.name
    BRUSH_SETS_LIB = brush_sets_dir.name
