from typing import Dict, Union, List, Set, Tuple

from .types.cat import BrushCategory as BrushCat
from .types.brush import Brush
from .types.texture import Texture


class BrushManager(object):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BrushManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.brush_cats: Dict[str, BrushCat] = dict()
        self.brushes: Dict[str, Brush]  = dict()

        self.textures: Dict[str, Texture] = dict()
