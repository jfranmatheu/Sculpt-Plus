from enum import Enum

from bpy.types import Image, Brush
from bpy.path import abspath

from sculpt_plus.utils.image import load_image, load_image_from_filepath


class BrushIcon(Enum):
    # SCULPT MDOE
    DEFAULT = ".Default_icon"
    DRAW = '.Draw_icon'
    DRAW_SHARP = '.Draw_Sharp_icon'
    CLAY = '.Clay_icon'
    CLAY_STRIPS = '.Clay_Strips_icon'
    CLAY_THUMB = '.Clay_Thumb_icon'
    LAYER = '.Layer_icon'
    INFLATE = '.Inflate_icon'
    BLOB = '.Blob_icon'
    CREASE = '.Crease_icon'
    SMOOTH = '.Smooth_icon'
    FLATTEN = '.Flatten_icon'
    FILL = '.Fill_icon'
    SCRAPE = '.Scrape_icon'
    MULTIPLANE_SCRAPE = '.Scrape_MultiPlane_icon'
    PINCH = '.Pinch_icon'
    GRAB = '.Grab_icon'
    ELASTIC_DEFORM = '.ElasticDeform_icon'
    SNAKE_HOOK = '.SnakeHook_icon'
    THUMB = '.Thumb_icon'
    POSE = '.Pose_icon'
    NUDGE = '.Nudge_icon'
    ROTATE = '.Rotate_icon'
    #TOPOLOGY = '.Topology_icon'
    #BOUNDARY = '.Boundary_icon'
    CLOTH = '.Cloth_icon'
    SIMPLIFY = '.Simplify_icon'
    MASK = '.Mask_icon'
    PAINT = '.Paint_icon'
    SMEAR = '.Paint_Smear_icon'
    DRAW_FACE_SETS = '.Draw_FaceSets_icon'

    # 2.91
    BOUNDARY = '.Boundary_icon'
    DISPLACEMENT_ERASER = '.Displacement_Eraser_icon'

    def __call__(self) -> Image:
        return load_image(self.value, '.png', 'brushes')
    
    @staticmethod
    def from_brush(brush: Brush) -> Image:
        return get_brush_icon(brush)


def get_brush_icon(brush: Brush) -> Image:
    if not brush:
        return BrushIcon.DEFAULT()
    if brush.use_custom_icon and brush.icon_filepath:
        ico = load_image_from_filepath(abspath(brush.icon_filepath))
        if not ico:
            return BrushIcon.DEFAULT() 
        return ico
    else:
        attr = getattr(BrushIcon, brush.sculpt_tool, None)
        if not attr:
            return BrushIcon.DEFAULT()
        return attr()


class Icon(Enum):
    SEARCH = '.Search_icon'
    ARROW_RIGHT = '.RightArrow_icon'

    MASK = '.Mask_icon'
    MASK_CLEAR = '.MaskClear_icon'
    MASK_INVERT = '.MaskInvert_icon'
    MASK_SMOOTH = '.MaskSmooth_icon'
    MASK_SHARP = '.MaskSharp_icon'
    
    EXPAND = '.Expand_icon'
    SHRINK = '.Shrink_icon'
    
    TRANSFORM_TRANSLATE = '.TransformTranslate_icon'
    TRANSFORM_ROTATE = '.TransformRotate_icon'
    TRANSFORM_SCALE = '.TransformScale_icon'
    TRANSFORM_MULTI = '.TransformMulti_icon'

    MASK_GROW = '.MaskGrow_icon'
    MASK_SHRINK = '.MaskShrink_icon'
    FACESET_GROW = '.FaceSetGrow_icon'
    FACESET_SHRINK = '.FaceSetShrink_icon'

    def __call__(self) -> Image:
        return load_image(self.value, '.png', 'icons')
