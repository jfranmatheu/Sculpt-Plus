from os.path import realpath, relpath, abspath, join, basename, dirname, exists, isfile
import bpy
from blf import load, unload

fonts_folder = join(dirname(__file__), 'fonts')

NUNITO_FILEPATH = join(fonts_folder, 'Nunito-Regular.ttf')

class Fonts:
    DEFAULT = 0
    NUNITO = load(NUNITO_FILEPATH)


def unregister():
    unload(NUNITO_FILEPATH)
