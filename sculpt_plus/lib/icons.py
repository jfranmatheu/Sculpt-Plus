from enum import Enum

from bpy.types import Image, Brush
from bpy.path import abspath

from sculpt_plus.utils.image import load_image, load_image_from_filepath
from sculpt_plus.path import SculptPlusPaths


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
    TOPOLOGY = '.Topology_icon'
    BOUNDARY = '.Boundary_icon'
    CLOTH = '.Cloth_icon'
    SIMPLIFY = '.Simplify_icon'
    MASK = '.Mask_icon'
    DRAW_FACE_SETS = '.Draw_FaceSets_icon'

    # 2.91
    DISPLACEMENT_ERASER = '.Displacement_Eraser_icon'
    DISPLACEMENT_SMEAR = 'Displacement_Smear_icon'

    PAINT = '.Paint_icon'
    SMEAR = '.Smear_icon'

    def __call__(self) -> Image:
        return load_image(self.value, '.png', 'brushes')
    
    @staticmethod
    def from_brush(brush: Brush) -> Image:
        return get_brush_icon(brush)

    def get_path(self) -> str:
        return SculptPlusPaths.SRC_LIB_IMAGES_BRUSHES(self.value + '.png')


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

    BRUSH_SET_1 = '.icons8_brushes_1_64'
    BRUSH_SET_2 = '.icons8_brushes_2_64'
    BRUSH_LIB = '.icons8_brushlib_64'
    BOOKS = '.icons8-books-96'
    BOOK_SHELF = '.icons8-book-shelf-96'
    BRUSH_PAINT = '.icons8-paintbrush-64'
    BRUSH_BROOM = '.icons8-broom-64'
    PENCIL_CASE_1 = '.icons8-pencil-case-64'
    PENCIL_CASE_2 = '.icons8-pencil-case-96'
    BRUSH_PENCIL_X = '.icons8-drawing-100'
    MOVE_UP_ROW = '.icons8-move-up-row-30'
    MOVE_DOWN_ROW = '.icons8-move-down-row-30'
    REMOVE_TRASH = '.icons8-remove-30'
    ADD_WEBPAGE = '.icons8-add-webpage-48'
    ADD_INBOX = '.icons8-add-to-inbox-24'
    ADD_CALENDAR = '.icons8-calendar-plus-30'
    IMPORT = '.icons8-import-48'
    DOWNLOAD = '.icons8-download-52'
    ADD_ROW = '.icons8-add-row-50'
    REMOVE_MINUS = '.icons8-minus-64'
    CLOSE = '.icons8-close-48'
    ADD_PLUS_1 = '.icons8-add-67'
    ADD_PLUS_2 = '.icons8-add_2-67'
    LINES_DIAGONAL = '.icons8-diagonal-lines-60'
    IMAGE = '.icons8-image-64'
    TEXTURE_SMALL = '.icons8-texture-small-24'
    TEXTURE = '.icons8-texture-48'
    TEXTURE_OPACITY = '.icons8-texture-opacity-48'
    PAINT_BRUSH = '.icons8-paint-brush-50'

    def __call__(self) -> Image:
        return load_image(self.value, '.png', 'icons')

    def get_path(self) -> str:
        return SculptPlusPaths.SRC_LIB_IMAGES_ICONS(self.value + '.png')
