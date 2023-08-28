from os.path import realpath, relpath, abspath, join, basename, dirname, exists, isfile
import bpy
from blf import load, unload

fonts_folder = join(dirname(__file__), 'fonts')

NUNITO_FILEPATH = join(fonts_folder, 'Nunito-Regular.ttf')

class Fonts:
    DEFAULT = 0
    NUNITO = 0


def register():
    Fonts.NUNITO = load(NUNITO_FILEPATH)


def unregister():
    print("Unregistering fonts...")
    Fonts.NUNITO = 0
    try:
        unload(NUNITO_FILEPATH)
    except Exception as e:
        print("FUCK BLENDER FONT AND FILE SYSTEM MANAGEMENT, ALSO FUCK WINDOWS")
        print(e)
