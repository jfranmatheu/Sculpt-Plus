from os.path import realpath, relpath, abspath, join, basename, dirname, exists, isfile
import bpy
from blf import load

fonts_folder = join(dirname(__file__), 'fonts')

class Fonts:
    DEFAULT = 0
    NUNITO = load(join(fonts_folder, 'Nunito-Regular.ttf'))
