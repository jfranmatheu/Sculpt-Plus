import sys, numpy as np, bpy#, multiprocessing
from sculpt_plus.path import SculptPlusPaths
from time import sleep
from pathlib import Path

argv = sys.argv
# pid = str(multiprocessing.active_children().pid) # function. str(os.getpid())
arg_idx = argv.index('--') + 1
pid = argv[arg_idx]
input_images: list[tuple[str, str]] = [
    (arg[:32], arg[32:]) for arg in argv[arg_idx+1:]
]

data_images = bpy.data.images

print("[Subprocess %s] Started!" % pid)

data = {}
for (image_id, image_path) in input_images:
    print(f"\t- [{pid}] Generating thumbnail {image_id} from path {image_path}")
    image = data_images.load(image_path)
    if not image.pixels:
        continue
    image.scale(100, 100)
    arr = np.empty(40000, dtype=np.float32)
    image.pixels.foreach_get(arr)
    data[image_id] = arr
    del image

output_path = Path(SculptPlusPaths.TEMP_THUMBNAILS()) / (pid + '.npz')
print("[Subprocess %s] Saving thumbnails data to:" % pid, output_path)
np.savez(output_path, **data)
sleep(1.0)
