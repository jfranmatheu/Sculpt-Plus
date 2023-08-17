from typing import Union, List, Dict, Set, Tuple
from enum import Enum, auto

import bpy
from bpy.types import Context, Image as BlImage, ImageTexture as BlImageTexture, Brush as BlBrush, WorkSpace

from sculpt_plus.sculpt_hotbar.canvas import Canvas
from sculpt_plus.path import SculptPlusPaths
from sculpt_plus.management.manager import HotbarManager as HM

from bl_ui.space_toolsystem_common import ToolSelectPanelHelper

from brush_manager.api import BM_DATA, bm_types, BM_UI, get_bm_data
from brush_manager.globals import GLOBALS, CM_UIContext



# SOME NICE SCULPT TOOL - BRUSH NAME CONSTANTS:
sculpt_tool_brush_name: Dict[str, str] = {'BLOB': 'Blob', 'BOUNDARY': 'Boundary', 'CLAY': 'Clay', 'CLAY_STRIPS': 'Clay Strips', 'CLAY_THUMB': 'Clay Thumb', 'CLOTH': 'Cloth', 'CREASE': 'Crease', 'DRAW_FACE_SETS': 'Draw Face Sets', 'DRAW_SHARP': 'Draw Sharp', 'ELASTIC_DEFORM': 'Elastic Deform', 'FILL': 'Fill/Deepen', 'FLATTEN': 'Flatten/Contrast', 'GRAB': 'Grab', 'INFLATE': 'Inflate/Deflate', 'LAYER': 'Layer', 'MASK': 'Mask', 'MULTIPLANE_SCRAPE': 'Multi-plane Scrape', 'DISPLACEMENT_ERASER': 'Multires Displacement Eraser', 'DISPLACEMENT_SMEAR': 'Multires Displacement Smear', 'NUDGE': 'Nudge', 'PAINT': 'Paint', 'PINCH': 'Pinch/Magnify', 'POSE': 'Pose', 'ROTATE': 'Rotate', 'SCRAPE': 'Scrape/Peaks', 'DRAW': 'SculptDraw', 'SIMPLIFY': 'Simplify', 'TOPOLOGY': 'Slide Relax', 'SMOOTH': 'Smooth', 'SNAKE_HOOK': 'Snake Hook', 'THUMB': 'Thumb'}
builtin_brush_names: Tuple[str] = tuple(sculpt_tool_brush_name.values())
builtin_brushes: Set[str] = set(builtin_brush_names)
builtin_images: Set[str]  = {'Render Result', 'Viewer Node'}
manager_exclude_brush_tools: Set[str] = {'MASK', 'DRAW_FACE_SETS', 'SIMPLIFY', 'DISPLACEMENT_ERASER', 'DISPLACEMENT_SMEAR'}
toolbar_hidden_brush_tools: Set[str] = {sculpt_tool for sculpt_tool in sculpt_tool_brush_name.keys() if sculpt_tool not in manager_exclude_brush_tools}
exclude_brush_names: Set[str] = {sculpt_tool_brush_name[sculpt_tool] for sculpt_tool in manager_exclude_brush_tools}
filtered_builtin_brush_names = tuple(b for b in builtin_brush_names if b not in exclude_brush_names)


stored_sculpt_tool: str = 'NULL'


IN_BRUSH_CTX = lambda _type: _type == 'BRUSH'
IN_TEXTURE_CTX = lambda _type: _type == 'TEXTURE'


bm_data = BM_DATA.SCULPT



''' Helper to get properties paths (with typing). '''
class Props:
    @staticmethod
    def Workspace(context=None) -> WorkSpace or None:
        context = context if context else bpy.context
        for workspace in bpy.data.workspaces:
            if 'sculpt_plus' in workspace:
                return workspace
        return None

    @staticmethod
    def WorkspaceSetup(context) -> WorkSpace or None:
        old_workspace = context.window.workspace

        try:
            # Workaround to ensure context is OK before workspace.append_active.
            Props.Temporal(context).test_context = True
        except RuntimeError as e:
            print(e)
            return None

        bpy.ops.workspace.append_activate(False, idname='Sculpt+', filepath=SculptPlusPaths.BLEND_WORKSPACE())
        workspace: WorkSpace = bpy.data.workspaces.get('Sculpt+', None)
        context.window.workspace = workspace

        # Set-up the workspace.
        if 'sculpt_plus' not in workspace:
            workspace['sculpt_plus'] = 1

        #workspace.use_filter_by_owner = True

        #for screen in workspace.screens:
        #    for area in screen.areas:
        #        print(screen.name, area.type)

        # Only addon enabled in this workspace should be Sculpt+ addon.
        #with context.temp_override(window=context.window, area=workspace.screens[0].areas[1], screen=workspace.screens[0], workspace=workspace):
        # bpy.ops.wm.owner_enable('INVOKE_DEFAULT', False, owner_id="sculpt_plus")

        context.window.workspace = old_workspace
        return workspace

    @staticmethod
    def Canvas() -> Union[Canvas, None]:
        if not hasattr(bpy, 'sculpt_hotbar'):
            return None
        return bpy.sculpt_hotbar._cv_instance

    @staticmethod
    def Scene(context: Context):# -> SCULPTPLUS_PG_scn:
        return context.scene.sculpt_plus

    @staticmethod
    def Temporal(context: Context):# -> SCULPTPLUS_PG_wm:
        return context.window_manager.sculpt_plus

    @classmethod
    def UI(cls, context: Context):# -> SCULPTPLUS_PG_wm:
        return cls.Temporal(context).ui


    class SculptTool:
        @staticmethod
        def get_stored() -> str:
            global stored_sculpt_tool
            return stored_sculpt_tool

        @staticmethod
        def clear_stored() -> None:
            global stored_sculpt_tool
            stored_sculpt_tool = 'NULL'

        @staticmethod
        def get_from_context(context: Context) -> tuple[str, str]:
            try:
                curr_active_tool = ToolSelectPanelHelper._tool_active_from_context(context, 'VIEW_3D', mode='SCULPT', create=False)
            except AttributeError as e:
                print("[SCULPT+] WARN!", e)
                return None
            if curr_active_tool is None:
                print("[SCULPT+] WARN! Current active tool is NULL")
                return None
            type, curr_active_tool = curr_active_tool.idname.split('.')
            curr_active_tool = curr_active_tool.replace(' ', '_').upper()
            return curr_active_tool, type

        @classmethod
        def update_stored(cls, context : Context) -> str:
            global stored_sculpt_tool
            stored_sculpt_tool = cls.get_from_context(context)

        @classmethod
        def has_changed(cls, context: Context) -> bool:
            global stored_sculpt_tool
            return stored_sculpt_tool != cls.get_from_context(context)



class HotbarManager:
    ''' Hotbar. '''
    @staticmethod
    def Hotbar() -> HM:
        return HM.get()

    @classmethod
    def GetHotbarSelectedId(cls) -> Union[str, None]:
        return cls.Hotbar().selected

    @classmethod
    def GetHotbarSelectedIndex(cls) -> int:
        selected_id: str = cls.GetHotbarSelectedId()
        if selected_id is None:
            return -1
        return cls.GetHotbarBrushIds().index(selected_id)

    @classmethod
    def GetHotbarBrushIds(cls) -> List[str]:
        return cls.Hotbar().brushes

    @classmethod
    def GetHotbarSelectedBrush(cls, context: Context) -> Union[bm_types.Brush, None]:
        selected_id: str = cls.GetHotbarSelectedId()
        if selected_id is None:
            return None
        return bm.get_brush(selected_id)

    @classmethod
    def GetHotbarBrushAtIndex(cls, context: Context, brush_index: int) -> bm_types.Brush:
        if brush_index < 0 or brush_index > 9:
            return None
        brushes_ids = cls.GetHotbarBrushIds()
        if not brushes_ids:
            return None
        brush_id: str = brushes_ids[brush_index]
        if brush_id is None:
            return None
        bm, item_type = BrushManager.get(context)
        return bm.get_brush(brush_id)

    @classmethod
    def SetHotbarBrush(cls, slot_index: int, brush: Union[str, bm_types.Brush]) -> None:
        brush_id: str = brush if isinstance(brush, str) else brush.id
        cls.Hotbar().brushes[slot_index] = brush_id

    @classmethod
    def SwitchHotbarBrushIndices(cls, index_A: int, index_B: int) -> None:
        hotbar: HotbarManager = cls.Hotbar()
        hotbar.brushes[index_A], hotbar.brushes[index_B] = hotbar.brushes[index_B], hotbar.brushes[index_A]

    @classmethod
    def SelectBrush(cls, context: Context, brush: Union[str, bm_types.Brush]) -> None:
        bm, item_type = BrushManager.get(context)
        if isinstance(brush, (int, str)):
            brush = bm.get_brush(brush)
        if brush is None:
            return

        brush.select(context)

        ui_props = Props.UI(context)
        ui_props.toolbar_brush_sections = 'BRUSH_SETTINGS'

    @classmethod
    def SetHotbarSelected(cls, context: Context, selected: Union[int, str, bm_types.Brush]) -> None:
        cls.Hotbar().selected = selected
        brush = cls.GetHotbarSelectedBrush()
        cls.SelectBrush(context, brush)

    @classmethod
    def ToggleHotbarAlt(cls):
        cls.Hotbar().toggle_alt()
