import bpy
from os.path import join, dirname, abspath
import sys
import pathlib
from enum import Enum


b3d_user_path = bpy.utils.resource_path('USER')
b3d_config_path = join(b3d_user_path, "config")

b3d_appdata_path = dirname(bpy.utils.resource_path('USER'))


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


src_path = pathlib.Path(__file__).parent
app_dir = pathlib.Path(b3d_appdata_path) / "addon_data" / __package__

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
        # with version_file.open('w', encoding='ascii') as file:
        #     from . import bl_info
        #     file.write(f"{bl_info['version']}\n")

        data_dir.mkdir(parents=False)
        temp_dir.mkdir()

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
    SRC_LIB_IMAGES_ICONS = join(SRC_LIB, 'icons')
    SRC_LIB_IMAGES_BRUSHES = join(SRC_LIB_IMAGES, 'brushes')
    SRC_LIB_SCRIPTS = join(SRC_LIB, 'scripts')
    SRC_LIB_BLEND = join(SRC_LIB, 'blend')
    SRC_LIB_BRUSH_PACKS = join(SRC_LIB, 'brush_packs')
    BLEND_EMPTY = join(SRC_LIB_BLEND, 'empty.blend')
    BLEND_WORKSPACE = join(SRC_LIB_BLEND, 'sculpt_plus_workspace.blend')

    LIB_SHADERS = join(SRC_LIB, 'shaders')
    LIB_SHADERS_VERT = join(LIB_SHADERS, 'vert')
    LIB_SHADERS_FRAG = join(LIB_SHADERS, 'frag')
    LIB_SHADERS_BUILTIN = join(LIB_SHADERS, 'builtin')

    APP = app_dir
    APP__DATA = data_dir
    APP__TEMP = temp_dir

    CONFIG_FILE = data_dir / 'config.json'
    HOTBAR_DATA = data_dir / "hotbar"


    def __call__(self, *path, as_path: bool = False):
        if not path:
            return self.value if as_path else str(self.value)
        return self.value.joinpath(*path) if as_path else join(str(self.value), *path)

    def read(self, *path) -> str:
        with open(self(*path), mode='r') as f:
            return f.read()
