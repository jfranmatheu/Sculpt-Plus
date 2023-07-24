from typing import Union, List, Dict, Set, Tuple

import bpy
from bpy.types import Context, Image as BlImage, ImageTexture as BlImageTexture, Brush as BlBrush, WorkSpace

from sculpt_plus.sculpt_hotbar.canvas import Canvas
from sculpt_plus.path import SculptPlusPaths
from sculpt_plus.management.manager import HotbarManager

from brush_manager.api import BM, bm_types



# SOME NICE SCULPT TOOL - BRUSH NAME CONSTANTS:
sculpt_tool_brush_name: Dict[str, str] = {'BLOB': 'Blob', 'BOUNDARY': 'Boundary', 'CLAY': 'Clay', 'CLAY_STRIPS': 'Clay Strips', 'CLAY_THUMB': 'Clay Thumb', 'CLOTH': 'Cloth', 'CREASE': 'Crease', 'DRAW_FACE_SETS': 'Draw Face Sets', 'DRAW_SHARP': 'Draw Sharp', 'ELASTIC_DEFORM': 'Elastic Deform', 'FILL': 'Fill/Deepen', 'FLATTEN': 'Flatten/Contrast', 'GRAB': 'Grab', 'INFLATE': 'Inflate/Deflate', 'LAYER': 'Layer', 'MASK': 'Mask', 'MULTIPLANE_SCRAPE': 'Multi-plane Scrape', 'DISPLACEMENT_ERASER': 'Multires Displacement Eraser', 'DISPLACEMENT_SMEAR': 'Multires Displacement Smear', 'NUDGE': 'Nudge', 'PAINT': 'Paint', 'PINCH': 'Pinch/Magnify', 'POSE': 'Pose', 'ROTATE': 'Rotate', 'SCRAPE': 'Scrape/Peaks', 'DRAW': 'SculptDraw', 'SIMPLIFY': 'Simplify', 'TOPOLOGY': 'Slide Relax', 'SMOOTH': 'Smooth', 'SNAKE_HOOK': 'Snake Hook', 'THUMB': 'Thumb'}
builtin_brush_names: Tuple[str] = tuple(sculpt_tool_brush_name.values())
builtin_brushes: Set[str] = set(builtin_brush_names)
builtin_images: Set[str]  = {'Render Result', 'Viewer Node'}
manager_exclude_brush_tools: Set[str] = {'MASK', 'DRAW_FACE_SETS', 'SIMPLIFY', 'DISPLACEMENT_ERASER', 'DISPLACEMENT_SMEAR'}
toolbar_hidden_brush_tools: Set[str] = {sculpt_tool for sculpt_tool in sculpt_tool_brush_name.keys() if sculpt_tool not in manager_exclude_brush_tools}
exclude_brush_names: Set[str] = {sculpt_tool_brush_name[sculpt_tool] for sculpt_tool in manager_exclude_brush_tools}
filtered_builtin_brush_names = tuple(b for b in builtin_brush_names if b not in exclude_brush_names)



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

    @staticmethod
    def BrushManager(context: Context | None = None) -> bm_types.AddonDataByMode:
        return BM.SCULPT(context)


    ''' Categories Common. '''

    @classmethod
    def NewCat(cls, context: Context, cat_type: str, cat_name: str = None) -> None:
        if cat_type == 'BRUSH':
            return cls.BrushManager(context).new_brush_cat('Untitled Cat ' + str(cls.BrushCatsCount()) if cat_name is None else cat_name)
        elif cat_type == 'TEXTURE':
            return cls.BrushManager(context).new_texture_cat('Untitled Cat ' + str(cls.TextureCatsCount()) if cat_name is None else cat_name)

    @classmethod
    def RemoveActiveCat(cls, context: Context, cat_type: str) -> None:
        if cat_type == 'BRUSH':
            act_cat = cls.ActiveBrushCat(context)
            return cls.BrushManager(context).remove_brush_cat(act_cat)
        elif cat_type == 'TEXTURE':
            act_cat = cls.ActiveTextureCat(context)
            return cls.BrushManager(context).remove_texture_cat(act_cat)

    @classmethod
    def GetActiveCat(cls, context: Context, ctx_type: str) -> Union[bm_types.BrushCategory, bm_types.TextureCategory, None]:
        if ctx_type == 'BRUSH':
            return cls.ActiveBrushCat(context)
        elif ctx_type == 'TEXTURE':
            return cls.ActiveTextureCat(context)
        return None

    @classmethod
    def SetActiveCat(cls, context: Context, ctx_type: str, cat: Union[bm_types.BrushCategory, bm_types.TextureCategory, str, int]) -> None:
        if cat is None:
            return
        if ctx_type == 'BRUSH':
            Props.BrushManager(context).select_brush_category(cat)
        elif ctx_type == 'TEXTURE':
            Props.BrushManager(context).select_texture_category(cat)

    @classmethod
    def GetAllCats(cls, context: Context, ctx_type: str, skip_active: bool = False) -> Union[List[Union[bm_types.BrushCategory, bm_types.TextureCategory]], None]:
        if ctx_type == 'BRUSH':
            cats = Props.GetAllBrushCats(context)
        elif ctx_type == 'TEXTURE':
            cats = Props.GetAllTextureCats(context)
        if skip_active:
            act_cat = cls.GetActiveCat(context, ctx_type)
            cats = [cat for cat in cats if cat != act_cat]
        return cats


    ''' Brush Catagories. '''

    @classmethod
    def GetAllBrushCats(cls, context: Context) -> bm_types.BrushCat_Collection:
        return cls.BrushManager(context).brush_cats

    @classmethod
    def GetBrushCat(cls, context: Context, cat_id_or_index: Union[str, int]) -> bm_types.BrushCategory:
        return cls.BrushManager(context).get_brush_cat(cat_id_or_index)

    @classmethod
    def ActiveBrushCat(cls, context: Context) -> bm_types.BrushCategory:
        return cls.BrushManager(context).active_brush_cat

    @classmethod
    def ActiveBrushCatIndex(cls, context: Context) -> int:
        return cls.BrushManager(context).active_brush_cat_index

    @classmethod
    def GetActiveBrushCatItems(cls, context: Context) -> list[bm_types.Brush]:
        ''' Returns the brushes UUIDs from active brush category. '''
        if act_cat := cls.ActiveBrushCat(context):
            return act_cat.get_items(cls.BrushManager(context)) # act_cat.item_ids
        return []

    @classmethod
    def BrushCatsCount(cls, context: Context) -> int:
        return len(cls.BrushManager(context).brush_cats)


    ''' Texture Categories. '''
    @classmethod
    def TextureCatsCount(cls, context: Context) -> int:
        return len(cls.GetAllTextureCats(context))

    @classmethod
    def GetAllTextureCats(cls, context: Context) -> bm_types.TextureCat_Collection:
        return cls.BrushManager(context).texture_cats

    @classmethod
    def GetTextureCat(cls, context: Context, cat_idname: Union[str, int]) -> bm_types.TextureCategory:
        return cls.BrushManager(context).get_texture_cat(cat_idname)

    @classmethod
    def ActiveTextureCat(cls, context: Context) -> bm_types.TextureCategory:
        return cls.BrushManager(context).active_texture_cat

    @classmethod
    def ActiveTextureCatIndex(cls, context: Context) -> int:
        return cls.BrushManager(context).active_texture_cat_index

    @classmethod
    def GetActiveTextureCatItems(cls, context: Context) -> List[bm_types.Texture]:
        if act_cat := cls.ActiveTextureCat(context):
            return act_cat.get_items(cls.BrushManager(context)) # act_cat.item_ids
        return []

    @classmethod
    def GetActiveCatItems(cls, context: Context, ctx_type: str) -> Union[List[Union[bm_types.Brush, bm_types.Texture]], None]:
        act_cat = cls.GetActiveCat(context, ctx_type)
        if act_cat is not None:
            return act_cat.items
        return None

    @classmethod
    def GetActiveCatItemIds(cls, context: Context, ctx_type: str) -> List[str]:
        act_cat = cls.GetActiveCat(context, ctx_type)
        if act_cat is not None:
            return act_cat.item_ids
        return None


    ''' Get brush/texture item. '''
    @classmethod
    def GetBrush(cls, context: Context, index_or_uuid: int | str) -> bm_types.Brush:
        return cls.BrushManager(context).get_brush(index_or_uuid)

    @classmethod
    def GetTexture(cls, context: Context, index_or_uuid: int | str) -> bm_types.Texture:
        return cls.BrushManager(context).get_texture(index_or_uuid)

    @classmethod
    def GetBrushIndex(cls, context: Context, brush_id: str) -> int:
        return cls.BrushManager(context).get_brush_index(brush_id)

    @classmethod
    def GetTextureIndex(cls, context: Context, texture_id: str) -> int:
        return cls.BrushManager(context).get_texture_index(texture_id)

    @classmethod
    def GetActiveBrush(cls, context: Context) -> bm_types.Brush:
        return cls.BrushManager(context).active_brush

    @classmethod
    def GetActiveTexture(cls, context: Context) -> bm_types.Texture:
        return cls.GetTexture(context, cls.BrushManager(context).active_texture)
    
    @classmethod
    def GetActiveBrushIndex(cls, context: Context) -> int:
        return cls.GetBrushIndex(context, cls.GetActiveBrush(context).uuid)

    @classmethod
    def GetActiveTextureIndex(cls, context: Context) -> int:
        return cls.GetTextureIndex(context, cls.GetActiveTexture(context).uuid)

    @classmethod
    def SetActiveBrush(cls, context: Context, brush: Union[int, str]) -> None:
        cls.BrushManager(context).select_brush(context, brush)
        
    @classmethod
    def SetActiveTexture(cls, context: Context, brush: Union[int, str]) -> None:
        cls.BrushManager(context).select_texture(context, brush)


    ''' Hotbar. '''
    @staticmethod
    def Hotbar() -> HotbarManager:
        return HotbarManager.get()

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
    def GetHotbarSelectedBrush(cls) -> Union[bm_types.Brush, None]:
        selected_id: str = cls.GetHotbarSelectedId()
        if selected_id is None:
            return None
        return cls.GetBrush(selected_id)

    @classmethod
    def GetHotbarBrushAtIndex(cls, brush_index: int) -> bm_types.Brush:
        if brush_index < 0 or brush_index > 9:
            return None
        brushes_ids = cls.GetHotbarBrushIds()
        if not brushes_ids:
            return None
        brush_id: str = brushes_ids[brush_index]
        if brush_id is None:
            return None
        return cls.GetBrush(brush_id)

    @classmethod
    def SetHotbarBrush(cls, slot_index: int, brush: Union[str, bm_types.Brush]) -> None:
        brush_id: str = brush if isinstance(brush, str) else brush.id
        cls.Hotbar().brushes[slot_index] = brush_id

    @classmethod
    def SwitchHotbarBrushIndices(cls, index_A: int, index_B: int) -> None:
        hotbar: HotbarManager = cls.Hotbar()
        hotbar.brushes[index_A], hotbar.brushes[index_B] = hotbar.brushes[index_B], hotbar.brushes[index_A]

    @classmethod
    def SelectBrush(cls, ctx: Context, brush: Union[str, bm_types.Brush]) -> None:
        if isinstance(brush, str):
            brush = cls.GetBrush(brush)
        if brush is None:
            return
        # print("--------------------------------------------------------------------------------------")
        # print("Selecting brush..", brush.name)
        cls.SetActiveBrush(brush.id)
        SculptToolUtils.select_brush_tool(ctx, brush)
        # brush.to_brush(ctx)
        if brush.texture_id is not None:
            if texture := cls.GetTexture(brush.texture_id):
                texture.to_brush(ctx)
                print(texture.name, texture.image.filepath_raw)

        ui_props = cls.UI(ctx)
        ui_props.toolbar_brush_sections = 'BRUSH_SETTINGS'

    @classmethod
    def SetHotbarSelected(cls, ctx: Context, selected: Union[int, str, bm_types.Brush]) -> None:
        cls.Hotbar().selected = selected
        brush = cls.GetHotbarSelectedBrush()
        cls.SelectBrush(ctx, brush)

    @classmethod
    def ToggleHotbarAlt(cls):
        cls.Hotbar().toggle_alt()
