from .types import Texture
from sculpt_plus.path import ScriptPaths, SculptPlusPaths

from bpy.app import binary_path

from time import time, sleep
from math import floor
from threading import Thread
from multiprocessing import cpu_count
import subprocess


MAX_PROCESSES = max(1, cpu_count() / 2)
MAX_ITEMS_PER_PROCESS = 20


class PsdConverter:
    def __init__(self, blendlib_path: str, texture_items: list[Texture]) -> None:
        self.texture_items = texture_items
        self.processes = []
        self.process_items = {}

        for tex_item in texture_items:
            tex_item.thumbnail.status = 'LOADING'

        tot_items: int = len(texture_items)
        needed_process_count: int = min(MAX_PROCESSES, max(1, int(tot_items / MAX_ITEMS_PER_PROCESS)))
        _items_per_process = tot_items / needed_process_count
        items_per_process = [floor(_items_per_process)] * needed_process_count
        if _items_per_process % 1 != 0:
            items_per_process[0] += int(_items_per_process % 1 * needed_process_count)

        off = 0
        for count in items_per_process:
            items = texture_items[off:off+count]
            process = subprocess.Popen(
                [
                    binary_path,
                    blendlib_path,
                    '--background',
                    '--python',
                    ScriptPaths.CONVERT_TEXTURES_TO_PNG_FROM_BLENDLIB,
                    '--',
                    *[(item.id + item.name) for item in items]
                ],
                stdin=None,
                stdout=None,
                stderr=subprocess.DEVNULL,
                shell=False
            )
            self.processes.append(process)
            self.process_items[process.pid] = items

            off += count

        self.process_controller = Thread(target=self.controller_loop, name="PsdConverterController")
        self.process_controller.start()

    def controller_loop(self):
        print("Starting PsdConverter...")
        while 1:
            if all([process.poll() is not None for process in self.processes]):
                break
            sleep(.1)
        self.finish()
        del self.texture_items
        del self.processes
        del self.process_items
        print("Stopping PsdConverter...")

    def finish(self):
        for tex_item in self.texture_items:
            print("\t- PSD Texture converted to PNG: ", tex_item.name)
            tex_item.image_user = None
            tex_item.image.filepath_raw = SculptPlusPaths.DATA_TEXTURE_IMAGES(tex_item.id + '.png')
            tex_item.image.source = 'FILE'
            tex_item.image.extension = '.png'
            tex_item.image.file_format = 'PNG'
            tex_item.thumbnail.file_format = 'PNG'
            tex_item.image_user = None
            tex_item.thumbnail.set_filepath(tex_item.image.filepath_raw, lazy_generate=True)
