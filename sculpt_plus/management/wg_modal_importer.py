from sculpt_plus.sculpt_hotbar.wg_container import Canvas, Vector, SCULPTPLUS_AddonPreferences, WidgetContainer, WidgetBase
from sculpt_plus.sculpt_hotbar.wg_view import ViewWidget, FakeViewItem_Brush, FakeViewItem_Texture, FakeViewItem
from sculpt_plus.sculpt_hotbar.wg_but import Button, ButtonGroup
from sculpt_plus.sculpt_hotbar.wg_selector import WidgetSelector
from sculpt_plus.management.types.image import Thumbnail
from sculpt_plus.sculpt_hotbar.di import DiRct, DiCage, DiIma, DiIcoCol, DiIco, DiText, DiIcoOpGamHl, DiImaOpGamHl
from sculpt_plus.utils.gpu import gputex_from_image_file
from sculpt_plus.lib.icons import Icon
from sculpt_plus.props import Props
from sculpt_plus.path import DBShelfManager, DBShelfPaths, ScriptPaths, SculptPlusPaths

import bpy
from typing import Union
import subprocess
from time import time


class AssetImporterModal(WidgetBase): # WidgetContainer
    interactable: bool = False

    def init(self) -> None:
        self.enabled = False
        self.lib_path: str = None
        self.input_brushes = []
        self.input_textures = []
        self.output_brushes = []
        self.output_textures = []
        self.ctx_type = 'BRUSH'

        #self.add_child(AssetImporterGrid_Inputs(self.cv, (.05, .45, .05, .9)))
        #self.add_child(AssetImporterGrid_Outputs(self.cv, (.55, .95, .05, .9)))

    def on_hover(self, m: Vector, p: Vector = None, s: Vector = None) -> bool:
        return True

    def pass_item(self, item: Union[FakeViewItem_Brush, FakeViewItem_Texture], move_to: str) -> None:
        if self.ctx_type == 'BRUSH':
            if move_to == 'INPUT':
                self.input_brushes.append(self.output_brushes.pop(self.output_brushes.index(item)))
            elif move_to == 'OUTPUT':
                self.output_brushes.append(self.input_brushes.pop(self.input_brushes.index(item)))
        elif self.ctx_type == 'TEXTURE':
            if move_to == 'INPUT':
                self.input_textures.append(self.output_textures.pop(self.output_textures.index(item)))
            elif move_to == 'OUTPUT':
                self.output_textures.append(self.input_textures.pop(self.input_textures.index(item)))
    
    def pass_all_items(self, move_to: str) -> None:
        if self.ctx_type == 'BRUSH':
            if move_to == 'INPUT':
                self.input_brushes, self.output_brushes = self.output_brushes, self.input_brushes
            elif move_to == 'OUTPUT':
                self.output_brushes, self.input_brushes = self.input_brushes, self.output_brushes
        elif self.ctx_type == 'TEXTURE':
            if move_to == 'INPUT':
                self.input_textures, self.output_textures = self.output_textures, self.input_textures
            elif move_to == 'OUTPUT':
                self.output_textures, self.input_brushes = self.input_brushes, self.output_textures

    def show(self, lib_path: str, type: str, data: Union[list[FakeViewItem_Brush], list[FakeViewItem_Texture]]) -> None:
        if not data:
            return

        self.lib_path = lib_path
        self.ctx_type = type

        if type == 'BRUSH':
            self.input_brushes = data
            self.output_brushes = []
        elif type == 'TEXTURE':
            self.input_textures = data
            self.output_textures = []

        self.enabled = True
        self.cv.shelf.expand = False

        self.update(self.cv, None)
        self.cv.refresh()

    def confirm(self):
        manager = Props.BrushManager()
        # manager.load_brushes_from_lib("Blend-lib Cat", lib_path=self.lib_path)
        '''
        datablocks = {
            'brushes': [brush.name for brush in self.output_brushes],
            'images': [texture.name for texture in self.output_textures],
        }
        '''
        items = self.output_brushes if self.ctx_type == 'BRUSH' else self.output_textures if self.ctx_type == 'TEXTURE' else None
        if not items:
            return

        start_time = time()
        # with DBShelfManager.TEMPORAL() as temp_db:
        #     {temp_db.write(item) for item in items}
        output_file: str = SculptPlusPaths.APP__TEMP('fake_items_texture_ids.txt')
        with open(output_file, 'w', encoding='ascii') as f:
            if self.ctx_type == 'BRUSH':
                f.write('\n'.join([b.texture.id + b.texture.name for b in items if b.texture is not None]))
            elif self.ctx_type == 'TEXTURE':
                f.write('\n'.join([t.id + t.name for t in items]))
        print("*[TIME] Save fake items to temporal database: %.2f seconds" % (time() - start_time))

        start_time = time()
        process = subprocess.Popen(
            [
                bpy.app.binary_path,
                self.lib_path,
                '--background',
                '--python',
                ScriptPaths.GENERATE_NPZ_FROM_BLENDLIB,
                '--',
                output_file,
                # self.ctx_type
            ],
        )
        process.wait()
        print("*[TIME] Save selected textures to .npy: %.2f seconds" % (time() - start_time))

        #manager.load_viewitems_from_lib(lib_path=self.lib_path, type=self.ctx_type, items=items)
        del items
        self.close()

    def cancel(self):
        self.close()

    def close(self) -> None:
        self.cv.refresh()
        self.cv.shelf.expand = True
        self.enabled = False
        self.lib_path = None

        if self.ctx_type == 'BRUSH':
            del self.input_brushes
            del self.output_brushes
        elif self.ctx_type == 'TEXTURE':
            del self.input_textures
            del self.output_textures

    def update(self, cv: Canvas, prefs: SCULPTPLUS_AddonPreferences) -> None:
        # print(self.enabled)
        self.pos = Vector((
            cv.reg.width * .25, # cv.shelf_sidebar.pos.x,
            cv.reg.height * .25
        ))
        self.size = Vector((
            cv.reg.width * .75 - self.pos.x, # cv.hotbar.get_pos_by_relative_point(Vector((1, 0))).x - self.pos.x,
            cv.reg.height * .75 - self.pos.y
        ))

        super().update(cv, prefs)

    def draw_pre(self, ctx, cv: Canvas, mouse: Vector, scale: float, prefs: SCULPTPLUS_AddonPreferences):
        DiRct(Vector((0, 0)), Vector((ctx.region.width, ctx.region.height)), (.05, .05, .05, .95))

    def draw(self, ctx, cv: Canvas, m, scale: float, prefs: SCULPTPLUS_AddonPreferences):
        DiRct(self.pos, self.size, prefs.theme_shelf)
        DiCage(self.pos, self.size, 6, Vector(prefs.theme_shelf) * 1.25)
        DiText(self.pos, "Press 'A' to swap all items.", 12, scale, pivot=(0, 1))


class AssetImporterWidget:
    parent: AssetImporterModal
    enabled: bool

    @property
    def enabled(self):
        return self.cv.mod_asset_importer.enabled
    
    @enabled.setter
    def enabled(self, value):
        self._enabled = value
        if value:
            self.on_enable()

    def on_enable(self):
        pass

    def __init__(self) -> None:
        self._enabled = False


class AssetImporterCatSelector(WidgetSelector, AssetImporterWidget):
    label = "Select a Category"

    def update(self, cv: Canvas, prefs: SCULPTPLUS_AddonPreferences) -> None:
        parent = cv.mod_asset_importer
        self.size = Vector((150, 30)) * cv.scale
        self.pos = parent.get_pos_by_relative_point(Vector((.5, .85)))
        self.pos.x -= (self.size.x * .5)
        self.pos.y += self.size.y

        super().update(cv, prefs)

    def on_enable(self):
        self.items = self.load_items()
        # print(self.items)

    def load_items(self):
        # print(self.cv.mod_asset_importer.ctx_type, "Holaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        parent = self.cv.mod_asset_importer
        if parent.ctx_type == 'BRUSH':
            cats = Props.GetAllBrushCats()
        elif parent.ctx_type == 'TEXTURE':
            cats = Props.GetAllTextureCats()
        else:
            return ()
        return [
            (cat.id, cat.name) for cat in cats
        ]


class AssetImporterActions(ButtonGroup, AssetImporterWidget):
    def init(self) -> None:
        super().init()

        self.button_style['color'] = (.16, .16, .16, .9)

        self.new_button(
            "Confirm",
            on_click_callback=lambda ctx, cv: cv.mod_asset_importer.confirm(),
        )
        self.new_button(
            "Cancel",
            on_click_callback=lambda ctx, cv: cv.mod_asset_importer.cancel(),
        )

    def update(self, cv: Canvas, prefs: SCULPTPLUS_AddonPreferences) -> None:
        parent = cv.mod_asset_importer
        self.size = Vector((
            180 * cv.scale,
            32 * cv.scale
        ))
        self.pos = parent.get_pos_by_relative_point(Vector((.5, 0)))
        self.pos.x -= (self.size.x / 2)
        self.pos.y -= (self.size.y * 2)

        super().update(cv, prefs)

    def draw_pre(self, context, cv: Canvas, mouse: Vector, scale: float, prefs: SCULPTPLUS_AddonPreferences):
        pass


class AssetImporterGrid(ViewWidget, AssetImporterWidget):
    use_scissor: bool = True

    header_label: str = 'Hello World'
    item_hover_icon: Icon

    def __init__(self, canvas: Canvas, anchor: tuple[float, float, float, float] = (0, 1, 0, 1)) -> None:
        self.anchor = anchor

        super().__init__(canvas)

    def update(self, cv: Canvas, prefs: SCULPTPLUS_AddonPreferences) -> None:
        parent = cv.mod_asset_importer
        pos, size = parent.get_pos_size_by_anchor(Vector(self.anchor))
        padding = Vector((10, 10)) * cv.scale
        self.pos = pos + padding
        self.size = size - padding * 2

    def event(self, ctx, evt, cv: Canvas, m: Vector) -> bool:
        if evt.type == 'A' and evt.value == 'CLICK':
            self.pass_all_items(cv)
        return False

    def on_left_click(self, ctx, cv: Canvas, m: Vector) -> None:
        if self.hovered_item:
            self.pass_item(cv)
            cv.refresh(ctx)

    def pass_item(self, cv: Canvas) -> None:
        pass

    def pass_all_items(self, cv: Canvas) -> None:
        pass

    def get_draw_item_args(self, context, cv: Canvas, scale: float, prefs: SCULPTPLUS_AddonPreferences) -> tuple:
        return (
            prefs.theme_shelf_slot,
            cv.mouse
        )

    def draw_pre(self, context, cv: Canvas, mouse: Vector, scale: float, prefs: SCULPTPLUS_AddonPreferences):
        DiText(self.get_pos_by_relative_point(Vector((0, 1))) + Vector((0, 8 * scale)), self.header_label, 16, scale)
        DiRct(self.pos, self.size, Vector(prefs.theme_sidebar) * .7)

    def draw_item(self, slot_p, slot_s, item: Union[FakeViewItem_Brush, FakeViewItem_Texture], is_hovered: bool, slot_color, mouse: Vector, scale: float, prefs: SCULPTPLUS_AddonPreferences):
        pad = 4 * scale
        padding = Vector((pad, pad))
        DiRct(slot_p, slot_s, slot_color)
        DiImaOpGamHl(slot_p + padding, slot_s - padding * 2, item.icon)

        if isinstance(item, FakeViewItem_Brush) and item.texture:
            texsize = slot_s.x * .4
            texsize = Vector((texsize, texsize))
            texpos = slot_p + Vector((slot_s.x - texsize.x, 0))
            DiImaOpGamHl(texpos, texsize, item.texture.icon)
            DiCage(texpos, texsize, 1, (.1, .1, .1, .92))

        if is_hovered:
            DiRct(slot_p, slot_s, (.05, .05, .05, .82))
            DiCage(slot_p, slot_s, pad*.5, prefs.theme_active_slot_color)

            mid = slot_p + slot_s * .5
            r = slot_s.x * .2
            radius = Vector((r, r))
            DiIcoOpGamHl(mid - radius, radius * 2, self.item_hover_icon, 1.5)
            # DiIcoOpGamHl(mouse - radius, radius * 2, self.item_hover_icon, 1.0) 


class AssetImporterGrid_Inputs(AssetImporterGrid):
    header_label: str = 'Blend Library Assets'
    item_hover_icon = Icon.ADD_PLUS_2

    def get_data(self, cv: Canvas) -> list:
        parent = cv.mod_asset_importer
        if parent.ctx_type == 'BRUSH':
            return parent.input_brushes
        elif parent.ctx_type == 'TEXTURE':
            return parent.input_textures
        return []

    def pass_item(self, cv: Canvas):
        parent = cv.mod_asset_importer
        parent.pass_item(self.hovered_item, move_to='OUTPUT')

    def pass_all_items(self, cv: Canvas) -> None:
        parent = cv.mod_asset_importer
        parent.pass_all_items(move_to='OUTPUT')


class AssetImporterGrid_Outputs(AssetImporterGrid):
    header_label: str = 'To Import Assets'
    item_hover_icon = Icon.CLOSE

    def get_data(self, cv: Canvas) -> list:
        parent = cv.mod_asset_importer
        if parent.ctx_type == 'BRUSH':
            return parent.output_brushes
        elif parent.ctx_type == 'TEXTURE':
            return parent.output_textures
        return []

    def pass_item(self, cv: Canvas):
        parent = cv.mod_asset_importer
        parent.pass_item(self.hovered_item, move_to='INPUT')

    def pass_all_items(self, cv: Canvas) -> None:
        parent = cv.mod_asset_importer
        parent.pass_all_items(move_to='INPUT')
