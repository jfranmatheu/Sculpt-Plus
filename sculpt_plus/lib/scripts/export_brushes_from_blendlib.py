from pathlib import Path
import sys
from math import floor
from threading import Thread
from multiprocessing import cpu_count

from bpy import ops as OP
from bpy import data as D
from bpy.path import abspath


from sculpt_plus.path import DBShelfManager
from sculpt_plus.props import builtin_brushes, Brush, Texture
from sculpt_plus.core.sockets.pbar_client import PBarClient


##############################################################################
# ARGUMENTS.
##############################################################################
''' Get Command Arguments.
Called from Blender.

Command arguments:
0. b3d exec.
1. blendlib path.
2. --background flag.
3. --python flag.
4. script path.
5. '--' empty break flag.
6. Socket communication PORT.
'''
argv = sys.argv
PYTHON_EXEC = argv[0]
BLENDLIB_FILEPATH = argv[1]
THIS_SCRIPT_FILEPATH = argv[4]
SOCKET_PORT = int(argv[-1])
USE_DEBUG = '--debug' in argv

if USE_DEBUG:
    from bpy.types import Brush as BlBrush, ImageTexture as BlImageTexture
    from time import time
    print(argv)
    start_time = time()
    print("[Sculpt+][SUB::ExportBrushesFromBlendlib] START")
else:
    BlBrush = None
    BlImageTexture = None


##############################################################################
# CONSTANTS.
##############################################################################
COMPATIBLE_IMAGE_EXTENSIONS = {'PNG', 'JPG', 'JPEG', 'TGA', 'TIFF', 'TIF', 'PSD'}

##############################################################################
# UTIL FUNCTIONS.
##############################################################################


def insert_custom_property(ID, name: str, value) -> None:
    ID[name] = value


def verify_brush_texture(bl_brush: BlBrush) -> bool:
    if bl_brush.texture is None:
        print("\t- Brush has not texture ->", bl_brush.name)
        return False
    if bl_brush.texture.type != 'IMAGE': # not isinstance(bl_brush.texture, BlImageTexture):
        print("\t- Brush Texture is not image type ->", bl_brush.name, bl_brush.texture.name)
        return False
    bl_image = bl_brush.texture.image
    if bl_image is None:
        print("\t- Brush Texture has no image ->", bl_brush.name, bl_brush.texture.name)
        return False
    if bl_image.source not in {'FILE', 'SEQUENCE'}:
        print("\t- Invalid Blender image source ->", bl_image.name)
        return False
    filepath = bl_image.filepath_raw # filepath_from_user()
    if not filepath:
        print("\t- Invalid image filepath! ->", bl_image.name)
        return False
    filepath = Path(filepath)
    if not filepath.exists() or not filepath.is_file():
        print("\t- Could not find image in path! ->", bl_image.name, str(filepath))
        return False
    #if bl_image.size[0] == 0 or bl_image.size[1] == 0:
    #    print("\t- Invalid image size (0x0px)! ->", bl_image.name, str(filepath))
    #    return False
    #if len(bl_image.pixels) == 0:
    #   print("\t- Image pixel data not found! ->", bl_image.name, str(filepath))
    #   return False
    return True


##############################################################################
# PROCESS...
##############################################################################

''' Create a client Socket to communicate the progress to the invoker process. '''
client_progress = PBarClient(port=SOCKET_PORT)
client_progress.start()


''' Get sculpt brushes. Ignore builtin brushes. '''
brushes: list[BlBrush] = [b for b in D.brushes if b.use_paint_sculpt and b.name not in builtin_brushes]


''' Count will be useful to determine the interval for progress reporting.
    As well as to split brushes in several async loops for concurrent or parallel processing.'''
brush_count: int = len(brushes)
client_progress.set_increment_rate(step_count=brush_count+1)


''' Unpack all images from brush textures packed in the .blend library. '''
OP.file.unpack_all()
OP.file.make_paths_absolute()


''' MULTI-THREADING '''
brush_items: list[Brush] = []

def new_brush_item(bl_brush: BlBrush) -> Brush:
    client_progress.increase()
    if USE_DEBUG:
        print("\t- Creating brush", bl_brush.name)
    return Brush(
        bl_brush,
        fake_brush=None,
    )

def new_texture_item(bl_texture: BlImageTexture) -> Texture:
    return Texture(
        bl_texture,
        fake_texture=None,
    )

def run_thread(input_bl_brushes: list[BlBrush]):
    if USE_DEBUG:
        print("[Sculpt+][SUB::ExportBrushesFromBlendlib] Start Thread")
    for bl_brush in input_bl_brushes:
        brush_item: Brush = new_brush_item(bl_brush)

        if verify_brush_texture(bl_brush):
            tex_item: Texture = new_texture_item(bl_brush.texture)
            tex_item.thumbnail.set_filepath(tex_item.image.filepath_raw, lazy_generate=False)
            brush_item.attach_texture(tex_item)

        if brush_item.use_custom_icon:
            brush_item.icon_filepath = abspath(brush_item.icon_filepath)
            icon_path: Path = Path(brush_item.icon_filepath)
            if not icon_path.exists() or not icon_path.is_file():
                brush_item.icon_filepath = ''
                brush_item.use_custom_icon = False
            else:
                brush_item.thumbnail.set_filepath(brush_item.icon_filepath, lazy_generate=False)

        brush_items.append(brush_item)

    print("[Sculpt+][SUB::ExportBrushesFromBlendlib] Finish Thread")


min_brushes_per_thread = 10
thread_count: int = int(cpu_count() / 2)
if thread_count > (brush_count / min_brushes_per_thread):
    # Does not need too many threads.
    thread_count = floor(brush_count / min_brushes_per_thread)

_brushes_per_loop: int = brush_count / thread_count
brushes_per_loop = [floor(_brushes_per_loop)] * thread_count
if _brushes_per_loop % 1 != 0:
    brushes_per_loop[0] += int(_brushes_per_loop % 1 * thread_count)

if USE_DEBUG:
    print("[Sculpt+][SUB::ExportBrushesFromBlendlib] - Total threads ->", thread_count)

threads: list[Thread] = []

index = 0
for count in brushes_per_loop:
    thread = Thread(target=run_thread, args=(brushes[index:index+count],), daemon=False)
    index += count

    threads.append(thread)

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()


''' Write to the shelve temporal database
    all retrieved items from async loops. '''
with DBShelfManager.TEMPORAL(cleanup=True) as db_temp:
    {db_temp.write(brush_item) for brush_item in brush_items}


client_progress.complete(stop=True)


if USE_DEBUG:
    print("================================")
    print("[TIME] Finished in %.2f seconds" % (time() - start_time))
    print("================================")
