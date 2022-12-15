from math import floor
import functools
from time import time

from .di import DiCage, DiRct,DiBr,DiText
from mathutils import Vector
from gpu import state
from bpy.app import timers
import bpy
from bpy.app import timers
from bpy import ops as OP
from bpy.types import Brush
import functools
from sculpt_plus.utils.math import distance_between, ease_quad_in_out, lerp, lerp_smooth, map_value, point_inside_circle, smoothstep, vector
from .types import Return
from sculpt_plus.prefs import get_prefs
from .di import set_font
from sculpt_plus.lib.fonts import Fonts
from sculpt_plus.utils.gpu import OffscreenBuffer
from ..utils.gpu import LiveView


start_time = 0
counter = 0
fps_count = 0

class Canvas:
    def __init__(self, reg) -> None:
        self.size = Vector((reg.width,reg.height))
        self.pos = Vector((0, 0))
        self.scale = 1.0
        self.reg = reg
        self.mouse = Vector((0, 0))
        self.hover_ctx = None
        self.tag_redraw = False
        self.modal_override_all = False
        self.init_ui()
        set_font(Fonts.NUNITO)

    def init_ui(self):
        from .wg_base import WidgetBase
        from .wg_hotbar import Hotbar
        from .wg_shelf import Shelf, ShelfDragHandle, ShelfSearch, ShelfGrid, ShelfGridItemInfo
        # from .wg_sidebar import Sidebar, SidebarGrid
        from .wg_group_mask import MaskGroup, MaskMultiGroup
        from .wg_group_t import TransformGroup
        from .wg_shelf_sidebar import ShelfSidebar, ShelfSidebarActions
        from .wg_ctx_switcher import SidebarContextSwitcher
        from .wg_ctx_pie import ShelfGridItemCtxPie, ShelfSidebarCatCtxPie

        from ..management.wg_modal_importer import (
            AssetImporterModal, AssetImporterGrid_Inputs, AssetImporterGrid_Outputs,
            AssetImporterActions, AssetImporterCatSelector)

        self.wg_on_hover: WidgetBase = None
        self.active_wg: WidgetBase = None
        self.active_ctx_widget: WidgetBase = None

        self.hotbar: Hotbar = Hotbar(self)
        self.shelf : Shelf  = Shelf(self)
        self.shelf_drag: ShelfDragHandle = ShelfDragHandle(self)
        self.shelf_search: ShelfSearch = ShelfSearch(self)
        self.shelf_grid: ShelfGrid = ShelfGrid(self)
        self.shelf_grid_item_info: ShelfGridItemInfo = ShelfGridItemInfo(self)
        self.group_mask: MaskMultiGroup = MaskMultiGroup(self)
        self.group_t: TransformGroup = TransformGroup(self)
        #self.sidebar: Sidebar = Sidebar(self)
        #self.sidebar_grid: SidebarGrid = SidebarGrid(self)
        self.shelf_sidebar: ShelfSidebar = ShelfSidebar(self)
        self.shelf_sidebar_actions: ShelfSidebarActions = ShelfSidebarActions(self)
        self.shelf_ctx_switcher: SidebarContextSwitcher = SidebarContextSwitcher(self)
        self.ctx_shelf_item: ShelfGridItemCtxPie = ShelfGridItemCtxPie(self)
        self.ctx_shelf_sidebar_item: ShelfSidebarCatCtxPie = ShelfSidebarCatCtxPie(self)
        self.mod_asset_importer: AssetImporterModal = AssetImporterModal(self)
        self.mod_asset_importer_inputs: AssetImporterGrid_Inputs = AssetImporterGrid_Inputs(self, (0, .5, .0, .85))
        self.mod_asset_importer_outputs: AssetImporterGrid_Outputs = AssetImporterGrid_Outputs(self, (.5, 1, .0, .85))
        self.mod_asset_importer_actions: AssetImporterActions = AssetImporterActions(self, text_size=16, but_spacing=32, separator_color=None)
        # self.mod_asset_importer_catselector: AssetImporterCatSelector = AssetImporterCatSelector(self)

        self.children = (self.hotbar,#self.sidebar, self.sidebar_grid,
                         self.shelf,
                         self.shelf_drag, self.shelf_search, self.shelf_grid, self.shelf_grid_item_info,
                         self.shelf_sidebar, self.shelf_sidebar_actions, self.shelf_ctx_switcher,
                         self.group_mask, self.group_t,
                         self.ctx_shelf_item, self.ctx_shelf_sidebar_item,
                         self.mod_asset_importer, self.mod_asset_importer_inputs, self.mod_asset_importer_outputs,
                         self.mod_asset_importer_actions, # self.mod_asset_importer_catselector
                         )
        global start_time
        start_time = time()

    def update(self, off: tuple, dimensions: tuple, scale: float, prefs) -> 'Canvas': # SCULPTPLUS_AddonPreferences
        if dimensions:
            self.size = Vector(dimensions)
        if off:
            self.pos = Vector(off)
        self.scale = scale
        for child in self.children: child.update(self, prefs)
        #self.hotbar.update(self, prefs)
        #self.shelf.update(self, prefs)
        #self.shelf_drag.update(self, prefs)
        return self
    def refresh(self, ctx=None):
        if ctx:
            ctx.region.tag_redraw()
        else:
            self.reg.tag_redraw()
        self.tag_redraw = True
    def test(self, ctx, m):return 1 if not get_prefs(ctx).first_time and self._on_hover(ctx, m) else -1
    @staticmethod
    def set_cursor(_state=True):
        import bpy
        #bpy.context.window.cursor_modal_set('DEFAULT'if not state else 'PAINT_CROSS')
        bpy.context.tool_settings.sculpt.show_brush = _state
    def _on_hover(self, ctx, m):
        if self.tag_redraw:
            OffscreenBuffer.tag_redraw(ctx)
            self.tag_redraw = False
        #scale = get_prefs(ctx).get_scale(ctx)
        #if scale != self.scale:
        #    self.update(self.size, scale, get_prefs(ctx))
        # self.reg = ctx.region
        self.mouse = Vector(m)
        self.hover_ctx = ctx
        if self.active_ctx_widget:
            self.active_ctx_widget._on_hover(ctx, self.mouse)
            return True
        interactable_ok = False # HACK.
        if self.wg_on_hover and self.wg_on_hover._is_on_hover:
            if self.wg_on_hover._on_hover(ctx, self.mouse):
                #self.refresh(ctx)
                # HACK.
                if self.wg_on_hover.interactable:
                    return True
                interactable_ok = True
        for child in reversed(self.children):
            # HACK.
            if interactable_ok and child == self.wg_on_hover:
                continue
            if child._on_hover(ctx, self.mouse):
                # HACK.
                if interactable_ok:
                    self.wg_on_hover._is_on_hover = False
                    self.wg_on_hover.on_hover_exit()
                if not self.wg_on_hover:
                    timers.register(functools.partial(Canvas.set_cursor, False), first_interval=0.05)
                else:
                    self.refresh(ctx)
                self.wg_on_hover = child
                return True
        # HACK.
        if interactable_ok:
            return True
        if self.wg_on_hover:
            self.refresh(ctx)
            timers.register(functools.partial(Canvas.set_cursor, True), first_interval=0.05)
            self.wg_on_hover = None
        if self.shelf.expand:
            return True
        return False

    def invoke(self, ctx, evt):
        print("Canvas::invoke - Event:", evt.type, evt.value)
        # print(evt.alt)
        if evt.type == 'LEFT_ALT' and evt.alt and evt.value == 'PRESS':
            if not self.hotbar.use_secondary:
                self.hotbar.use_secondary = True
                self.refresh(ctx)
                return Return.FINISH()
        elif evt.type == 'LEFT_ALT' and not evt.alt and evt.value == 'RELEASE':
            if self.hotbar.use_secondary:
                self.hotbar.use_secondary = False
                self.refresh(ctx)
                return Return.FINISH()
        if not self.wg_on_hover:
            if self.shelf.expand and not self.shelf.anim_pool:
                self.shelf.expand = False
            return Return.FINISH()
        if not self.wg_on_hover.interactable:
            return Return.FINISH()
        self.refresh(ctx)
        mouse = Vector((evt.mouse_region_x, evt.mouse_region_y))
        if self.wg_on_hover.invoke(ctx, evt, self, mouse):
            self.inject_submodal(ctx, self.wg_on_hover)
            return Return.RUN()
        return Return.FINISH()
    def modal(self, ctx, evt, tweak):
        #if evt.value == 'RELEASE':
        #    return Return.FINISH()
        self.refresh(ctx)
        mouse = Vector((evt.mouse_region_x, evt.mouse_region_y))
        if self.active_wg:
            if not self.active_wg.modal(ctx, evt, self, mouse):
                self.active_wg.in_modal = False
                self.active_wg.modal_exit(ctx, self, self.mouse)
                self.active_wg = None
                if self.active_ctx_widget is None:
                    return Return.FINISH()
        if self.active_ctx_widget:
            if not self.active_ctx_widget.modal(ctx, evt, self, mouse):
                self.active_ctx_widget.in_modal = False
                self.active_ctx_widget.modal_exit(ctx, self, self.mouse)
                self.active_ctx_widget = None
                if self.active_wg:
                    self.active_wg.in_modal = False
                    self.active_wg.modal_exit(ctx, self, self.mouse, cancel=True)
                    self.active_wg = None
                return Return.FINISH()
        return Return.RUN()
    def exit(self, ctx, cancel: bool = False):
        ctx.area.header_text_set(None)
        if self.active_wg:
            self.refresh(ctx)
            #if not cancel:
            #    self.active_wg.on_leftmouse_release(ctx, self, self.mouse)
            self.active_wg.in_modal = False
            self.active_wg.modal_exit(ctx, self, self.mouse, cancel=cancel)
            self.active_wg = None
        if self.active_ctx_widget: # and not self.active_ctx_widget.closes_itself:
            self.active_ctx_widget = None

    def inject_submodal(self, ctx, widget):
        self.active_wg = widget
        self.wg_on_hover = widget
        widget.in_modal = True
        widget.modal_enter(ctx, self, self.mouse)
        self.refresh(ctx)

    def inject_ctx_widget(self, widget, override_all: bool = False) -> None:
        # self.active_wg = widget
        self.wg_on_hover = widget
        widget.in_modal = True
        self.active_ctx_widget = widget
        self.modal_override_all = override_all
        self.refresh()

    def draw(self, ctx):
        if get_prefs(ctx).first_time:
            DiText(Vector((10, 10)), "Please, restart Blender to complete Sculpt+ installation!", 32, 1.0, (1.0, 0.2, 0.1, 1.0))
            return

        # LiveView.get().draw_px(ctx)

        prefs = get_prefs(ctx)

        if self.active_ctx_widget and self.modal_override_all:
            self.active_ctx_widget._draw(ctx, self, self.mouse, self.scale, prefs)
            self.active_ctx_widget.draw_over(ctx, self, self.mouse, self.scale, prefs)
            return

        global counter
        global fps_count
        global start_time

        for child in self.children:
            child._draw(ctx, self, self.mouse, self.scale, prefs)

        for child in self.children:
            child.draw_over(ctx, self, self.mouse, self.scale, prefs)

        #print("[DEBUG] FPS: ", fps_count / (time() - start_time)) # FPS = 1 / time to process loop
        DiText(Vector((10, 10)), "FPS: " + str(fps_count), 16, 1.0, (1.0, 0.2, 0.1, 1.0))

        counter += 1
        if (time() - start_time) > 1.0:
            fps_count = int(counter / (time() - start_time))
            counter = 0
            start_time = time()
