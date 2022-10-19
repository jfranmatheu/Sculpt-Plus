import os
from os.path import join, dirname, abspath


class SculptPlusPaths:
    SRC = dirname(abspath(__file__))
    APP_DATA = join(os.getenv('APPDATA'), 'BlenderAddons', __package__)
    BRUSH_LIB = join(APP_DATA, 'brushes')
