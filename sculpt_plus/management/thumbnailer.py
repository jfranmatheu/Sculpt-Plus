from threading import Thread, Timer
from multiprocessing import cpu_count
from typing import Tuple, Union, List, Dict, Set
from uuid import uuid4
from pathlib import Path
from math import floor
from collections import defaultdict
import numpy as np
import bpy
from time import sleep
from PIL import Image

from sculpt_plus.management.types.image import Thumbnail


MAX_THREADS = int(cpu_count() / 2.0)
MAX_THUMBNAILS_PER_THREAD = 32

THUMBNAIL_SIZE = 100, 100
THUMBNAIL_PIXEL_SIZE = 100 * 100 * 4

USE_DEBUG = False


def generate_thumbnail_with_bpy(image_path: str) -> np.ndarray:
    data_images = bpy.data.images
    image = data_images.load(image_path)
    image.scale(*THUMBNAIL_SIZE)
    pixels = np.empty(THUMBNAIL_PIXEL_SIZE, dtype=np.float32)
    image.pixels.foreach_get(pixels)
    data_images.remove(image)
    del image
    return pixels


def generate_thumbnail_with_pil(image_path: str) -> np.ndarray:
    image = Image.open(image_path)
    image.thumbnail(THUMBNAIL_SIZE, Image.Resampling.NEAREST)
    image = image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    pixels = np.array(image, dtype=np.float32).reshape(THUMBNAIL_PIXEL_SIZE) / 255
    image.close()
    del image
    return pixels


class Thumbnailer(object):
    _instance = None

    def __init__(self):
        self.threads: List[Tuple[Thread, str]] = []
        self.thread_items: Dict[str, Set[Thumbnail]] = defaultdict(set)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = Thumbnailer()
        return cls._instance


    @property
    def thread_count(self):
        return len(self.threads)


    @classmethod
    def push(cls, *thumbnails: Thumbnail):
        if USE_DEBUG:
            print("[Sculpt+][Thumbnailer] Pushing %i thumbnails..." % len(thumbnails))
        for thumbnail in thumbnails:
            thumbnail.status = 'LOADING'

        thumbnailer = cls.get_instance()

        thumbnail_count: int = len(thumbnails)
        needed_thread_count: int = min(MAX_THREADS, max(1, int(thumbnail_count / MAX_THUMBNAILS_PER_THREAD)))
        _thumbnails_per_thread = thumbnail_count / needed_thread_count
        thumbnails_per_thread = [floor(_thumbnails_per_thread)] * needed_thread_count
        if _thumbnails_per_thread % 1 != 0:
            thumbnails_per_thread[0] += int(thumbnails_per_thread % 1 * needed_thread_count)

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
            daemon=False
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
                icon_filepath = Path(thumbnail.filepath)
                if not icon_filepath.exists() or not icon_filepath.is_file():
                    thumbnail.status = 'NONE'
                    thumbnail.filepath = ''
                    continue
                if USE_DEBUG:
                    print("\t- Processing thumbnail '%s'" % thumbnail.filepath)
                file_format: str = icon_filepath.suffix.upper()[1:]
                if file_format in {'TIF', 'TIFF', 'PSD'}:
                    thumbnail.pixels = generate_thumbnail_with_bpy(str(icon_filepath))
                else:
                    thumbnail.pixels = generate_thumbnail_with_pil(str(icon_filepath))
                thumbnail.status = 'READY'

        # Thread loop.
        # print(thumbnailer.thread_items[thread_id])
        while len(thumbnailer.thread_items[thread_id]) > 0:
            _process_thumbnails(list(thumbnailer.thread_items.pop(thread_id)))
            sleep(0.5)

        thumbnailer.remove_thread(thread_id)
        if USE_DEBUG:
            print("[Sculpt+][Thumbnailer][Thread] Stop", thread_id)
