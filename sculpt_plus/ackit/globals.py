import bpy
import sys
from pathlib import Path
import platform
import ctypes

from .. import __package__ as __main_package__#, bl_info


def is_junction(path):
    # Check if the path exists
    if not path.exists():
        return False

    if platform.system() != 'Windows':
        return False

    # Use GetFileAttributes to check if it's a reparse point and a directory
    file_attributes = ctypes.windll.kernel32.GetFileAttributesW(str(path))

    if file_attributes == -1:
        return False

    is_reparse_point = (file_attributes & 0x400) != 0
    is_directory = (file_attributes & 0x10) != 0

    return is_reparse_point and is_directory


class GLOBALS:
    PYTHON_PATH = sys.executable

    BLENDER_VERSION = bpy.app.version
    IN_BACKGROUND = bpy.app.background

    ADDON_MODULE = __main_package__
    ADDON_MODULE_SHORT = __main_package__.split('.')[-1] if BLENDER_VERSION >= (4, 2, 0) else __main_package__
    ADDON_MODULE_UPPER = ADDON_MODULE_SHORT.upper().replace('_', '')
    ADDON_SOURCE_PATH = Path(__file__).parent.parent
    ADDON_MODULE_NAME = ADDON_MODULE_SHORT.replace('_', ' ').title().replace(' ', '')
    #ADDON_NAME = bl_info['name']
    #ADDON_VERSION = bl_info['version']
    #SUPPORTED_BLENDER_VERSION = bl_info['blender']
    ICONS_PATH = ADDON_SOURCE_PATH / 'lib' / 'icons'

    IN_DEVELOPMENT = (hasattr(sys, 'gettrace') and sys.gettrace() is not None) and is_junction(ADDON_SOURCE_PATH) # Just a nice HACK! ;-)
    IN_PRODUCTION  = not IN_DEVELOPMENT

    check_in_development = lambda : (hasattr(sys, 'gettrace') and sys.gettrace() is not None) and is_junction(GLOBALS.ADDON_SOURCE_PATH)
    check_in_production = lambda : not GLOBALS.check_in_development()


    class CodeGen:
        TYPES = 'types.py'
        ICONS = 'icons.py'
        OPS = 'ops.py'

    @staticmethod
    def get_addon_global_value(key: str, default_value = None):
        return getattr(bpy, GLOBALS.ADDON_MODULE).get(key, default_value)

    @staticmethod
    def set_addon_global_value(key: str, value) -> None:
        getattr(bpy, GLOBALS.ADDON_MODULE)[key] = value


setattr(bpy, GLOBALS.ADDON_MODULE, dict())
