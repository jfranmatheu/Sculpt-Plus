from time import time, sleep
from pathlib import Path
import sys
from uuid import uuid4
from math import floor
import asyncio
from threading import Thread
import multiprocessing

from bpy.types import ID as BlID, Image as BlImage, Texture as BlTexture, ImageTexture as BlImageTexture, Brush as BlBrush
from bpy import ops as OP
from bpy import data as D
from bpy.path import abspath

from sculpt_plus.path import SculptPlusPaths, DBShelfManager
from sculpt_plus.props import builtin_brushes, Texture, Brush
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
print(argv)
PYTHON_EXEC = argv[0]
BLENDLIB_FILEPATH = argv[1]
THIS_SCRIPT_FILEPATH = argv[4]
SOCKET_PORT = int(argv[6])


##############################################################################
# CONSTANTS.
##############################################################################
COMPATIBLE_IMAGE_EXTENSIONS = {'PNG', 'JPG', 'JPEG', 'TGA', 'TIFF', 'TIF', 'PSD'}


##############################################################################
# UTIL FUNCTIONS.
##############################################################################

def insert_custom_property(ID: BlID, name: str, value) -> None:
    ID[name] = value


##############################################################################
# PROCESS...
##############################################################################
start_time = time()

''' Create a client Socket to communicate the progress to the invoker process. '''
client_progress = PBarClient(port=SOCKET_PORT)
client_progress.start()

''' Get sculpt brushes. Ignore builtin brushes. '''
brushes: list[BlBrush] = [b for b in D.brushes if b.use_paint_sculpt and b.name not in builtin_brushes]

''' Generate UUIDs for every brush. '''
{insert_custom_property(brush, 'sculpt_plus_id', uuid4().hex) for brush in brushes}

''' Count will be useful to determine the interval for progress reporting.
    As well as to split brushes in several async loops for concurrent or parallel processing.'''
brush_count: int = len(brushes)
client_progress.set_increment_rate(step_count=brush_count+1)

''' Unpack all images from brush textures packed in the .blend library. '''
OP.file.unpack_all()

''' Read txt storing the relationship between the brush names and their UUIDs. '''
# brush_ids: dict[str, str] = {}
# with open(SculptPlusPaths.APP__TEMP("import_lib_ids.txt"), "r") as f:
#     brush_ids = {line[:32]: line[32:].replace('\n', '') for line in f.readlines()}

''' Create BrushItem objects per Blender Brush. '''
''' SYNCRONOUS
def _new_brush_item(brush: BlBrush) -> Brush:
    client_progress.increase()
    # print("\t- Creating brush", brush.name)
    return Brush(
        brush,
        fake_brush=None,
        generate_thumbnail=False,
        #custom_id=brush_ids[brush.name])
    )

brush_items: list[Brush] = [
    _new_brush_item(brush) for brush in brushes
]
'''

''' MULTI-THREADING '''
brush_items: list[Brush] = []

def new_brush_item(brush: BlBrush) -> Brush:
    client_progress.increase()
    # print("\t- Creating brush", brush.name)
    return Brush(
        brush,
        fake_brush=None,
        generate_thumbnail=False,
        #custom_id=brush_ids[brush.name])
    )

def run_thread(input_bl_brushes: list[BlBrush]):
    # icon_paths: list[Path] = []
    for bl_brush in input_bl_brushes:
        brush_item: Brush = new_brush_item(bl_brush)

        if brush_item.use_custom_icon:
            icon_path: Path = Path(brush_item.icon_filepath)
            if icon_path.exists() or not icon_path.is_file():
                brush_item.icon_filepath = ''
                brush_item.use_custom_icon = False

        brush_items.append(brush_item)

min_brushes_per_thread = 10
thread_count: int = int(multiprocessing.cpu_count() / 2)
if thread_count > (brush_count / min_brushes_per_thread):
    # Does not need too many threads.
    thread_count = floor(brush_count / min_brushes_per_thread)

_brushes_per_loop: int = brush_count / thread_count
brushes_per_loop = [floor(_brushes_per_loop)] * thread_count
if _brushes_per_loop % 1 != 0:
    brushes_per_loop[0] += int(_brushes_per_loop % 1 * thread_count)

threads = []

index = 0
for count in brushes_per_loop:
    thread = Thread(target=run_thread, args=(brushes[index:index+count],), daemon=True)
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

print("================================")
print("[TIME] Finished in %.2f seconds" % (time() - start_time))
print("================================")
