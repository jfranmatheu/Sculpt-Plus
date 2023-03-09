from threading import Thread, Timer
from multiprocessing import cpu_count, Process, Queue
import subprocess
from os import listdir
from os.path import exists, isfile
from typing import Tuple, Union, List, Dict, Set
from uuid import uuid4
from pathlib import Path
from math import floor
from collections import defaultdict
import numpy as np
import bpy
from time import sleep, time
from PIL import Image
from collections import deque

from sculpt_plus.management.types.image import Thumbnail
from sculpt_plus.path import SculptPlusPaths, ScriptPaths


MAX_PROCESSES = max(1, int(cpu_count() / 2.0))
MAX_THUMBNAILS_PER_PROCESS = 6
MIN_THUMBNAILS_PER_PROCESS = 4

MAX_THREADS = max(1, int(cpu_count() / 2.0))
MAX_THUMBNAILS_PER_THREAD = 32

THUMBNAIL_SIZE = 100, 100
THUMBNAIL_PIXEL_SIZE = 100 * 100 * 4

USE_DEBUG = True


def generate_thumbnail_with_bpy(image_path: str) -> np.ndarray:
    # AVOID USE BLENDER API AS IT IS SLOW, BLOCKS EVERYTHING AND CAN'T DO MULTI-THREADING LOL.
    # YES. BLENDER API IS SHIT.
    data_images = bpy.data.images
    image = data_images.load(image_path)
    image.scale(*THUMBNAIL_SIZE)
    pixels = np.empty(THUMBNAIL_PIXEL_SIZE, dtype=np.float32)
    image.pixels.foreach_get(pixels)
    data_images.remove(image)
    del image
    return pixels


def generate_thumbnail_with_pil(image_path: str, format: str) -> np.ndarray:
    image = Image.open(image_path, mode='r')
    # thumbnail preserve aspect ratio, some artists might use non-squared textures.
    # image.thumbnail(THUMBNAIL_SIZE, Image.Resampling.NEAREST)
    # NOTE BUG: thumbnail maintain aspect ratio.... which lead to errors... currently... must fix this somehow...
    image = image.resize(THUMBNAIL_SIZE, Image.Resampling.NEAREST)
    image = image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    image_size = image.size
    bands = len(image.getbands())
    px_size = image_size[0]*image_size[1]*bands
    pixels = np.array(image, dtype=np.float32).reshape(px_size) / 255
    image.close()
    del image
    return pixels, image_size, px_size


class SubProcess(object):
    def __init__(self):
        '''
        self.process = subprocess.Popen(
            [
                bpy.app.binary_path,
                # bpy.data.filepath,
                '--background',
                '--python',
                ScriptPaths.GENERATE_THUMBNAILS_FROM_IMAGE_FILES_USING_BPY,
                '--',
                *[thumbnail.filepath for thumbnail in thumbnails if thumbnail.filepath]
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            shell=False
        )
        '''
        self.id = uuid4().hex
        self.process = Process(target=self.update, name="ThumbnailerSubProcess_" + self.id)
        self.queue: Queue = Queue(maxsize=MAX_THUMBNAILS_PER_PROCESS)

    @property
    def queue_size(self) -> int:
        return self.queue.qsize()

    def put_thumbnail(self, thumbnail: Thumbnail) -> bool:
        """ Return if action was successful or not. """
        if self.queue.full:
            return False
        self.queue.put_nowait(thumbnail)
        return True


    def get_thumbnail(self, timeout: float = 1.0) -> Thumbnail:
        try:
            thumbnail = self.queue.get(block=True, timeout=timeout)
            return thumbnail
        except self.queue.empty:
            return None

    def update(self):
        while 1:
            if thumbnail := self.get_thumbnail(timeout=1.0):
                thumbnail.pixels = generate_thumbnail_with_bpy(thumbnail.filepath)
                thumbnail.status = 'READY'
            else:
                break


class Thumbnailer(object):
    _instance = None

    @classmethod
    def kill(cls):
        thumbnailer = cls.get_instance()
        thumbnailer.subprocess_controller = None
        for process in thumbnailer.processes:
            process.kill()

    def __init__(self):
        self.threads: List[Tuple[Thread, str]] = []
        self.thread_items: Dict[str, Set[Thumbnail]] = defaultdict(set)

        self.fucked_thumbnails: List[Thumbnail] = [] # deque() # List[Thumbnail] = []
        self.processes: List[Tuple[subprocess.Popen, str]] = []
        self.process_items: Dict[str, List[Thumbnail]] = defaultdict(list)
        self.subprocess_controller: Thread = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = Thumbnailer()
        return cls._instance


    @property
    def thread_count(self):
        return len(self.threads)

    def import_thumbnail_data(self, pid: str):
        npz_filepath: Path = Path(SculptPlusPaths.TEMP_THUMBNAILS()) / (pid + '.npz')
        if npz_filepath.exists():
            npz_data: dict = np.load(npz_filepath, 'r')
            for thumbnail in self.process_items[pid]:
                thumbnail.pixels = npz_data.get(thumbnail.id, None)
                if thumbnail.pixels is not None:
                    thumbnail.status = 'READY'
                    thumbnail.px_size = len(thumbnail.pixels)
                    if thumbnail.px_size != THUMBNAIL_PIXEL_SIZE:
                        print("WARN! Thumbnail pixel size mismatch:", thumbnail.px_size)
                else:
                    thumbnail.status = 'ERROR'
            del npz_data
            npz_filepath.unlink()
        else:
            print("ERROR! Couldn't find thumbnail data for pid", pid, str(npz_filepath))
            for thumbnail in self.process_items[pid]:
                thumbnail.status = 'ERROR'

    def check_processes(self) -> bool:
        alive_processes = []
        idx = len(self.processes) - 1
        # paths: List[str] = listdir(SculptPlusPaths.TEMP_THUMBNAILS())
        for (process, pid) in reversed(list(self.processes)):
            if process.poll() is None:
                alive_processes.append(pid)
                #elif thumbnail_id := process.communicate(timeout=1.0)[0].decode("utf-8"):
            else:
                # killed_processes.append(idx)
                self.import_thumbnail_data(pid)
                self.processes.pop(idx)
                del self.process_items[pid]

            idx -= 1

        return alive_processes != []


    def add_fucked_thumbnail(self, thumbnail: Thumbnail) -> None:
        if self.subprocess_controller is None:
            self.start_subprocess_controller()

        # if len(self.processes):
        thumbnail.status = 'LOADING'
        self.fucked_thumbnails.append(thumbnail)


    def stop_subprocess_controller(self):
        self.subprocess_controller = None


    def start_subprocess_controller(self):
        def _controller_loop(thumbnailer: Thumbnailer, start_time: float):
            prev_time = start_time
            print("[Sculpt+][Thumbnailer] Starting subprocess controller...")
            empty_time = None
            while 1:
                if thumbnailer.subprocess_controller is None:
                    # Thread killed externally. (just a hacky signal)
                    break

                any_process_alive = thumbnailer.check_processes()

                # lifetime = time() - start_time
                time_since_last_update = time() - prev_time

                if self.fucked_thumbnails == []:
                    if empty_time is None:
                        empty_time = time()
                    elif time() - empty_time > 10:
                        # 10 seconds without receiving any item more.
                        # Let's kill it! ONLY if not alive processes...
                        if not any_process_alive:
                            thumbnailer.subprocess_controller = None
                            break
                        # Skip break if there's still any process alive...
                    sleep(0.25)
                    continue

                empty_time = None

                tot_processes = len(self.processes)
                if tot_processes >= MAX_PROCESSES:
                    sleep(0.1)
                    continue

                tot_thumbnails: int = len(self.fucked_thumbnails)
                if tot_thumbnails < MAX_THUMBNAILS_PER_PROCESS:
                    if time_since_last_update < 1.0:
                        sleep(0.1)
                        continue

                    # JUST 1 PROCESS.
                    thumbnails = list(self.fucked_thumbnails)
                    self.fucked_thumbnails = []
                    self.start_new_subprocess(thumbnails)

                else:
                    # NEEDS TO SLICE LIST AND OPEN SOME PROCESSES.
                    needed_processes = int(tot_thumbnails / MAX_THUMBNAILS_PER_PROCESS)
                    free_process_count: int = MAX_PROCESSES - tot_processes
                    if needed_processes > free_process_count:
                        # MEH.
                        # Limiting to the max.
                        tot_thumbnails: int = free_process_count * MAX_THUMBNAILS_PER_PROCESS
                        thumbnails = self.fucked_thumbnails[:tot_thumbnails]
                        self.fucked_thumbnails = self.fucked_thumbnails[tot_thumbnails:]

                        # Not limiting to the max to manage several thumbnails at once.
                        #needed_processes = free_process_count
                        #thumbnails = list(self.fucked_thumbnails)
                        #self.fucked_thumbnails = []
                    else:
                        # LIFE IS BEAUTIFUL.
                        thumbnails = list(self.fucked_thumbnails)
                        self.fucked_thumbnails = []

                    _thumbnails_per_thread = tot_thumbnails / needed_processes
                    thumbnails_per_thread = [floor(_thumbnails_per_thread)] * needed_processes
                    if _thumbnails_per_thread % 1 != 0:
                        thumbnails_per_thread[0] += int(_thumbnails_per_thread % 1 * needed_processes)

                    off = 0
                    for count in thumbnails_per_thread:
                        self.start_new_subprocess(thumbnails[off:off+count])
                        off += count

                prev_time = time()
                sleep(.25)

            # KILL THREAD TIMER.
            print("[Sculpt+][Thumbnailer] Stopping subprocess controller...")

        self.subprocess_controller = Thread(name="ThumbnailerSubprocessController", target=_controller_loop, args=(self, time()), daemon=False)
        self.subprocess_controller.start()


    def start_new_subprocess(self, thumbnails: List[Thumbnail]) -> subprocess.Popen:
        # self.processes.append(SubProcess())
        pid = uuid4().hex
        process = subprocess.Popen(
            [
                bpy.app.binary_path,
                SculptPlusPaths.BLEND_EMPTY(),
                '--background',
                '--python',
                ScriptPaths.GENERATE_NPY_FROM_IMAGE_PATHS,
                '--',
                pid,
                *[
                    (thumbnail.id + thumbnail.filepath) for thumbnail in thumbnails if thumbnail.filepath
                ]
            ],
            stdin=None, # subprocess.PIPE,
            stdout=None, # subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            shell=True
        )

        self.processes.append((process, pid))
        self.process_items[pid] = thumbnails

    @classmethod
    def push(cls, *input_thumbnails: Thumbnail):
        if USE_DEBUG:
            print("[Sculpt+][Thumbnailer] Pushing %i thumbnails..." % len(input_thumbnails))

        thumbnails = []
        # FILTER THUMBNAILS. JUST FOR SECURITY.
        for thumbnail in input_thumbnails:
            if thumbnail.status in {'ERROR', 'UNSUPPORTED', 'LOADING'}:
                print("[Sculpt+][Thumbnailer] thumbnail status is in {'ERROR', 'UNSUPPORTED', 'LOADING'}!")
                continue
            if thumbnail.filepath is None:
                thumbnail.status = 'ERROR'
                if USE_DEBUG:
                    print("[Sculpt+][Thumbnailer] thumbnail filepath is null!")
                continue
            thumbnail.status = 'LOADING'
            filepath = Path(thumbnail.filepath)
            if not filepath.exists() or not filepath.is_file():
                thumbnail.status = 'ERROR'
                print("[Sculpt+][Thumbnailer] thumbnail filepath does not exist!")
                continue
            file_format = filepath.suffix[1:].upper()
            if file_format in {'PSD'}:
                thumbnail.file_format = file_format
                thumbnail.status = 'UNSUPPORTED'
                print("[Sculpt+][Thumbnailer] thumbnail file format is unsupported!")
                continue
            thumbnails.append(thumbnail)

        if thumbnails == []:
            print("[Sculpt+][Thumbnailer] no thumbnails data to process!")
            return

        thumbnailer = cls.get_instance()

        thumbnail_count: int = len(thumbnails)
        needed_thread_count: int = min(MAX_THREADS, max(1, int(thumbnail_count / MAX_THUMBNAILS_PER_THREAD)))
        _thumbnails_per_thread = thumbnail_count / needed_thread_count
        thumbnails_per_thread = [floor(_thumbnails_per_thread)] * needed_thread_count
        if _thumbnails_per_thread % 1 != 0:
            thumbnails_per_thread[0] += int(_thumbnails_per_thread % 1 * needed_thread_count)

        if thumbnailer.thread_count >= MAX_THREADS:
            thread_items_count = 100000000
            thread_id_with_less_item = ''
            for (thread, thread_id) in thumbnailer.threads:
                if thread is None:
                    continue
                if not thread.is_alive():
                    if USE_DEBUG:
                        print("WARN! Thread %s is not alive!" % thread.name)
                    thread = None
                    continue
                if len(thumbnailer.thread_items[thread_id]) < thread_items_count:
                    thread_id_with_less_item = thread_id
                    break
                #if ( len(thumbnailer.thread_items[thread_id]) + len(thumbnails) ) < 10:
                #    target_thread = thread
                #    break
            thumbnailer.add_thumbnails_to_thread(thread_id_with_less_item, thumbnails)
        else:
            t_index: int = 0
            for t_count in thumbnails_per_thread:
                if USE_DEBUG:
                    print("[Sculpt+][Thumbnailer] Starting new thread that will process %i thumbnails at start" % t_count)
                thumbnailer.new_thread(
                    thumbnails[t_index:t_index+t_count]
                )
                t_index += t_count


    def new_thread(self, thumbnails: Tuple[Thumbnail]):
        thread_id: str = uuid4().hex
        thread = Thread(
            name="Thumbnailer_" + thread_id,
            target=self._thread__generate_thumbnails,
            args=(thread_id, ),
            daemon=False,
        )
        self.threads.append((thread, thread_id))
        self.thread_items[thread_id].update(set(thumbnails))

        thread.start()


    def remove_thread(self, target_thread_id: str):
        for idx, (thread, thread_id) in enumerate(list(self.threads)):
            if thread_id == target_thread_id:
                thread = None
                self.threads.pop(idx)
                break

        del self.thread_items[target_thread_id]


    def add_thumbnails_to_thread(self, thread_id, thumbnails: Tuple[Thumbnail]) -> None:
        self.thread_items[thread_id].update(set(thumbnails))


    def _thread__generate_thumbnails(thumbnailer, thread_id: str) -> None:
        if USE_DEBUG:
            print("[Sculpt+][Thumbnailer][Thread] Start", thread_id)
        def _process_thumbnails(thumbnails: List[Thumbnail]) -> None:
            # print("[Sculpt+][Thumbnailer][Thread] Process", thread_id, len(thumbnails))
            for thumbnail in thumbnails:
                if thumbnail.filepath is None:
                    if USE_DEBUG:
                        print("\t- Not valid source filepath to generate thumbnail...")
                    continue
                icon_filepath = Path(thumbnail.filepath)
                if not icon_filepath.exists() or not icon_filepath.is_file():
                    thumbnail.status = 'NONE'
                    thumbnail.filepath = ''
                    continue
                if USE_DEBUG:
                    print("\t- Processing thumbnail '%s'" % thumbnail.filepath)
                file_format: str = icon_filepath.suffix.upper()[1:]
                if file_format in {'PSD'}:
                    if USE_DEBUG:
                        print("\t- Not valid file format to generate thumbnail... (PSD)")
                    thumbnail.pixels = None
                    thumbnail.status = 'UNSUPPORTED'
                elif file_format in {'TIF', 'TIFF'}: #
                    thumbnail.pixels = None # generate_thumbnail_with_bpy(str(icon_filepath))
                    thumbnailer.add_fucked_thumbnail(thumbnail)
                else:
                    thumbnail.pixels, thumbnail.image_size, thumbnail.px_size = generate_thumbnail_with_pil(str(icon_filepath), format=file_format)
                    #print("\t- thumbnail data:")
                    #print("\t\t- pixels:", len(thumbnail.pixels))
                    #print("\t\t- image_size:", thumbnail.image_size)
                    #print("\t\t- px_size:", thumbnail.px_size)
                if thumbnail.pixels is not None:
                    thumbnail.status = 'READY'
                    if USE_DEBUG:
                        print("\t\t - READY!")
                thumbnail.file_format = file_format

        # Thread loop.
        # print(thumbnailer.thread_items[thread_id])
        while len(thumbnailer.thread_items[thread_id]) > 0:
            _process_thumbnails(list(thumbnailer.thread_items.pop(thread_id)))
            sleep(0.5)

        thumbnailer.remove_thread(thread_id)
        if USE_DEBUG:
            print("[Sculpt+][Thumbnailer][Thread] Stop", thread_id)
