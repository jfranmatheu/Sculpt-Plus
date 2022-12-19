from enum import Enum

from . rct import *
from . img import *
from . point import *


__all__ = [
    'ShaderGeom'
]


class ShaderGeom(Enum):
    BUILTIN_IMG = BuiltIn_Img_Geo
    IMG = Img_Geo

    RCT = Rct_Geo
    RCT_BOTLEFT = RctBotLeft_Geo
    RCT_CENT = RctCent_Geo
    RCT_TOPLEFT = RctTopLeft_Geo
    
    # RCT_BOTLEFT_RND = RctBotLeft_Rdn_Geo
    # RCT_RND = Rct_Rnd_Geo

    POINT = Point_Geo
    CIR_CENT = Point_Geo

    def __call__(self, *args):
      return self.value(*args[0])
