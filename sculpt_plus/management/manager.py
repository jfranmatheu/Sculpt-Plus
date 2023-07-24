import json
from os.path import exists, isfile

from sculpt_plus.path import SculptPlusPaths
from brush_manager.data import Brush_Collection


builtin_brush_names = ('Blob', 'Boundary', 'Clay', 'Clay Strips', 'Clay Thumb', 'Cloth', 'Crease', 'Draw Face Sets', 'Draw Sharp', 'Elastic Deform', 'Fill/Deepen', 'Flatten/Contrast', 'Grab', 'Inflate/Deflate', 'Layer', 'Mask', 'Multi-plane Scrape', 'Multires Displacement Eraser', 'Multires Displacement Smear', 'Nudge', 'Paint', 'Pinch/Magnify', 'Pose', 'Rotate', 'Scrape/Peaks', 'SculptDraw', 'Simplify', 'Slide Relax', 'Smooth', 'Snake Hook', 'Thumb')
exclude_brush_names = {'Mask', 'Draw Face Sets', 'Simplify', 'Multires Displacement Eraser', 'Multires Displacement Smear'}
filtered_builtin_brush_names = tuple(b for b in builtin_brush_names if b not in exclude_brush_names)


class HotbarManager:
    _instance = None

    @classmethod
    def get(cls) -> 'HotbarManager':
        if cls._instance is None:
            cls._instance = HotbarManager()
        return cls._instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(HotbarManager, cls).__new__(cls)
        return cls._instance

    brushes: list[str]
    selected: str

    alt_brushes: list[str]
    alt_selected: str

    use_alt: bool

    is_data_loaded: bool

    def __init__(self):
        self._brushes: list[str] = [None] * 10
        self._selected: str = None
        self.alt_selected: str = None
        self.alt_brushes: list[str] = [None] * 10
        self.use_alt: bool = False

        self.is_data_loaded = False

    def __del__(self):
        self._selected = None
        self.alt_selected = None
        self._brushes.clear()
        self.alt_brushes.clear()

    @property
    def brushes(self) -> list[str]:
        if self.use_alt:
            return self.alt_brushes
        return self._brushes

    @brushes.setter
    def brushes(self, brushes: list[str]):
        self._brushes = brushes

    @property
    def selected(self) -> str:
        if self.use_alt:
            return self.alt_selected
        return self._selected

    def toggle_alt(self) -> None:
        self.use_alt = not self.use_alt

    @selected.setter
    def selected(self, item):
        if isinstance(item, str):
            pass
        elif isinstance(item, int):
            item = self.brushes[item]
        elif isinstance(item, Brush_Collection):
            item = item.uuid
        else:
            item = None
            print(f'WARN! Invalid selected hotbar item: {item}')
            # raise ValueError(f'Invalid selected item: {item}')
        if self.use_alt:
            self.alt_selected = item
        else:
            self._selected = item

    def serialize(self) -> dict:
        ''' Serialize hotbar data to a dictionary. '''
        return {
            '_brushes': self._brushes,
            '_selected': self._selected,
            'alt_brushes': self.alt_brushes,
            'alt_selected': self.alt_selected
        }

    def deserialize(self, data: dict) -> None:
        ''' Load data from dictionary. '''
        for attr, value in data.items():
            setattr(self, attr, value)


    # ----------------------------------------------------------------


    def load(self) -> None:
        print("[SCULPT+] Loading config file...")
        self.is_data_loaded = True
        hotbar_config: dict = {}
        config_filepath: str = SculptPlusPaths.HOTBAR_CONFIG()
        if exists(config_filepath) and isfile(config_filepath):
            with open(config_filepath, 'r') as f:
                hotbar_config = json.load(f)
                self.deserialize(hotbar_config)

    def save(self) -> None:
        print("[SCULPT+] Saving hotbar config...")
        with open(SculptPlusPaths.HOTBAR_CONFIG(), 'w') as f:
            json.dump(self.serialize(), f, indent=4, ensure_ascii=True)
