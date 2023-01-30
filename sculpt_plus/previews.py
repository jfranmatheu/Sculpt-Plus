
import os
import bpy
from enum import Enum
import bpy.utils.previews

from .path import SculptPlusPaths


# We can store multiple preview collections here,
# however in this example we only store "main"
preview_collections = {}


class CallEnum(Enum):
    def __call__(self) -> int:
        collection = preview_collections.get(self.__class__.__name__, None)
        if collection is None:
            collection = bpy.utils.previews.new()
            preview_collections[self.__class__.__name__] = collection
            # return 0
        icon = collection.get(self.name, None)
        if icon is not None:
            return icon.icon_id
        # print("GEN:", self.name, self.value)
        collection.load(self.name, SculptPlusPaths.SRC_LIB_IMAGES_ICONS(self.value + '.png'), 'IMAGE')
        icon = collection.get(self.name, None)
        if icon is not None:
            return icon.icon_id
        return 0


class Previews:
    class Main(CallEnum):
        BRUSH = '.brush_icon'
        BRUSH_ADD = '.brushAdd_icon'
        FILL = '.icons8-fill-drip-32'
        MIRROR = '.Mirror_icon'
        SCALE_UP = '.ScaleUp_icon'
        SCALE_DOWN = '.ScaleDown_icon'

    class Mask(CallEnum):
        MASK = '.Mask_icon'
        CLEAR = '.MaskClear_icon'
        INVERT = '.MaskInvert_icon'
        GROW = '.MaskScaleUp_icon_flat' # '.MaskGrow_icon2'
        SHRINK = '.MaskScaleDown_icon_flat' # '.MaskShrink_icon2'
        SHARP = '.MaskSharp_icon'
        SMOOTH = '.MaskSmooth_icon'
        BOX = '.Box_Mask_icon'
        LASSO = '.Lasso_Mask_icon'
        CONTRAST_UP = '.MaskContrastUp_icon_flat'
        CONTRAST_DOWN = '.MaskContrastDown_icon_flat'
        EXTRACT = '.MaskExtract_icon2'
        SLICE = '.MaskSlice_icon'
        RANDOM = '.MaskRandom_icon'
        CAVITY = '.MaskCavity_icon'

    class FaceSets(CallEnum):
        FACE_SETS = '.FaceSets_icon'
        GROW = '.FaceSetsScaleUp_icon' # '.FaceSetGrow_icon2'
        SHRINK = '.FaceSetsScaleDown_icon' # .FaceSetShrink_icon2'
        BOX = '.Box_FaceSet_icon'
        LASSO = '.Lasso_FaceSet_icon'

'''
def register():
    # Note that preview collections returned by bpy.utils.previews
    # are regular py objects - you can use them to store custom data.
    return

    import bpy.utils.previews
    for collection_name in preview_collections.keys():
        pcoll = bpy.utils.previews.new()
        for item in getattr(Previews, collection_name):
            print(item.name, item.value)
            pcoll.load(item.name, SculptPlusPaths.SRC_LIB_IMAGES_ICONS(item.value + '.png'), 'IMAGE')
        preview_collections[collection_name] = pcoll
'''

def unregister():
    for pcoll in preview_collections.values():
        if pcoll is not None:
            bpy.utils.previews.remove(pcoll)
    preview_collections.clear()
