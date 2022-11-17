from bpy.types import Brush
from os import path
import imbuf
from imbuf.types import ImBuf
from sculpt_plus.path import brush_sets_dir


def resize_and_save_brush_icon(brush: Brush):
    """ Resize and save the brush icon.
        Args:
            brush (Brush): The brush to resize and save.
    """
    if not path.exists(brush.icon_filepath):
        return
    image_buffer: ImBuf = imbuf.load(brush.icon_filepath)
    image_buffer.resize((128, 128), method='BILINEAR')
    save_path = str(brush_sets_dir / 'br_icon' / (brush['id'] + 'png'))
    imbuf.save(image_buffer, filepath=save_path)
    image_buffer.free()
    brush.icon_filepath = save_path
