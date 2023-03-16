from typing import Union, List, Dict, Set, Tuple

import bpy
from bpy.types import Context, Image as BlImage, ImageTexture as BlImageTexture, Brush as BlBrush, WorkSpace

from sculpt_plus.sculpt_hotbar.canvas import Canvas
from sculpt_plus.management.manager import Manager, TextureCategory, BrushCategory, Brush, Texture, HotbarManager
from sculpt_plus.management.types.fake_item import FakeViewItem_Brush, FakeViewItem_Texture
from sculpt_plus.path import SculptPlusPaths

#from sculpt_plus.core.data.scn import SCULPTPLUS_PG_scn
#from sculpt_plus.core.data.wm import SCULPTPLUS_PG_wm
#from sculpt_plus.brush_manager.data_brush_manager import SCULPTPLUS_PG_brush_manager
#from sculpt_plus.brush_manager.data_brush_category import SCULPTPLUS_PG_brush_category
#from sculpt_plus.brush_manager.data_brush_slot import SCULPTPLUS_PG_brush_slot


# SOME NICE SCULPT TOOL - BRUSH NAME CONSTANTS:
sculpt_tool_brush_name: Dict[str, str] = {'BLOB': 'Blob', 'BOUNDARY': 'Boundary', 'CLAY': 'Clay', 'CLAY_STRIPS': 'Clay Strips', 'CLAY_THUMB': 'Clay Thumb', 'CLOTH': 'Cloth', 'CREASE': 'Crease', 'DRAW_FACE_SETS': 'Draw Face Sets', 'DRAW_SHARP': 'Draw Sharp', 'ELASTIC_DEFORM': 'Elastic Deform', 'FILL': 'Fill/Deepen', 'FLATTEN': 'Flatten/Contrast', 'GRAB': 'Grab', 'INFLATE': 'Inflate/Deflate', 'LAYER': 'Layer', 'MASK': 'Mask', 'MULTIPLANE_SCRAPE': 'Multi-plane Scrape', 'DISPLACEMENT_ERASER': 'Multires Displacement Eraser', 'DISPLACEMENT_SMEAR': 'Multires Displacement Smear', 'NUDGE': 'Nudge', 'PAINT': 'Paint', 'PINCH': 'Pinch/Magnify', 'POSE': 'Pose', 'ROTATE': 'Rotate', 'SCRAPE': 'Scrape/Peaks', 'DRAW': 'SculptDraw', 'SIMPLIFY': 'Simplify', 'TOPOLOGY': 'Slide Relax', 'SMOOTH': 'Smooth', 'SNAKE_HOOK': 'Snake Hook', 'THUMB': 'Thumb'}
builtin_brush_names: Tuple[str] = tuple(sculpt_tool_brush_name.values())
builtin_brushes: Set[str] = set(builtin_brush_names)
builtin_images: Set[str]  = {'Render Result', 'Viewer Node'}
manager_exclude_brush_tools: Set[str] = {'MASK', 'DRAW_FACE_SETS', 'SIMPLIFY', 'DISPLACEMENT_ERASER', 'DISPLACEMENT_SMEAR'}
toolbar_hidden_brush_tools: Set[str] = {sculpt_tool for sculpt_tool in sculpt_tool_brush_name.keys() if sculpt_tool not in manager_exclude_brush_tools}
exclude_brush_names: Set[str] = {sculpt_tool_brush_name[sculpt_tool] for sculpt_tool in manager_exclude_brush_tools}
filtered_builtin_brush_names = tuple(b for b in builtin_brush_names if b not in exclude_brush_names)


class SculptToolUtils:
    @staticmethod
    def select_brush_tool(ctx: Context, brush: Brush):
        ori_brush_name = sculpt_tool_brush_name[brush.sculpt_tool]
        tmp_brush_name: str = 'S+ | ' + ori_brush_name
        tmp_brush = bpy.data.brushes.get(tmp_brush_name, None)
        if tmp_brush is None:
            tmp_brush = bpy.data.brushes.new(tmp_brush_name, mode='SCULPT')
            tmp_brush.sculpt_tool = brush.sculpt_tool
        brush.to_brush(tmp_brush)
        ctx.tool_settings.sculpt.brush = tmp_brush


''' Helper to get properties paths (with typing). '''
class Props:
    @staticmethod
    def get_temp_thumbnail_image() -> BlImage:
        if image := bpy.data.images.get('.sculpt_plus_thumbnail', None):
            return image
        return bpy.data.image.new('.sculpt_plus_thumbnail', 100, 100)

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

    @classmethod
    def TextureSingleton(cls, context: Context) -> BlImageTexture:
        texture: BlImageTexture =  cls.Scene(context).texture
        if texture is None:
            texture = bpy.data.textures.new('...sculpt_plus_brush_tex', 'IMAGE')
            cls.Scene(context).texture = texture
        return texture

    @classmethod
    def TextureImageSingleton(cls, context: Context, use_sequence: bool = False) -> BlImage:
        texture: BlImageTexture = cls.TextureSingleton(context)
        image: BlImage = cls.Scene(context).image
        if image is None:
            image: BlImage = bpy.data.images.new('...sculpt_plus_brush_tex_image', 1024, 1024)
        if texture.image != image:
            texture.image = image
        return image
        if use_sequence:
            image: BlImage = cls.Scene(context).image_seq
        else:
            image: BlImage = cls.Scene(context).image
        if image is None:
            name = '...sculpt_plus_brush_tex_image'
            if use_sequence:
                name += '_seq'
            image = bpy.data.images.new(name, 1024, 1024)
        if use_sequence:
            image.source = 'SEQUENCE'
        if texture.image != image:
            texture.image = image
        return image

    @staticmethod
    def BrushManager() -> 'Manager': # -> SCULPTPLUS_PG_brush_manager:
        # return cls.Temporal(context).brush_manager
        return Manager.get()

    @staticmethod
    def BrushManagerExists() -> bool:
        return Manager._instance is not None

    @classmethod
    def BrushManagerDestroy(cls) -> None:
        if cls.BrushManagerExists():
            del Manager._instance
            Manager._instance = None

    @classmethod
    def UpdateBrushProp(cls, brush_id: str, attr: str, value) -> None:
        if brush_id is None:
            brush = cls.GetHotbarSelectedBrush()
        else:
            brush = cls.GetBrush(brush_id)
        print(f"Update brush {brush.name} attr {attr} value {value}")
        brush.update_attr(attr, value)

    @classmethod
    def GetAllBrushCats(cls) -> List[BrushCategory]:
        return cls.BrushManager().brush_cats.values()

    @classmethod
    def GetBrushCat(cls, cat_idname: Union[str, int]) -> BrushCategory:# -> SCULPTPLUS_PG_brush_category:
        # return cls.BrushManager(context).get_cat(cat_idname)
        return cls.BrushManager().get_brush_cat(cat_idname)

    @classmethod
    def ActiveBrushCat(cls) -> BrushCategory:# -> SCULPTPLUS_PG_brush_category:
        # return cls.BrushManager(context).active
        return cls.BrushManager().active_brush_cat

    @classmethod
    def ActiveBrushCatIndex(cls) -> int:
        act_cat = cls.ActiveBrushCat()
        if act_cat is None:
            return -1
        return act_cat.index

    @classmethod
    def GetActiveBrushCatBrushes(cls) -> List[Brush]:
        act_cat = cls.ActiveBrushCat()
        if act_cat is None:
            return []
        return act_cat.items

    @classmethod
    def BrushCatsCount(cls) -> int:
        return cls.BrushManager().brush_cats_count

    @classmethod
    def TextureCatsCount(cls) -> int:
        return cls.BrushManager().texture_cats_count

    @classmethod
    def NewCat(cls, cat_type: str, cat_name: str = None) -> None:
        if cat_type == 'BRUSH':
            return cls.BrushManager().new_brush_cat('Untitled Cat ' + str(cls.BrushCatsCount()) if cat_name is None else cat_name)
        elif cat_type == 'TEXTURE':
            return cls.BrushManager().new_texture_cat('Untitled Cat ' + str(cls.TextureCatsCount()) if cat_name is None else cat_name)

    @classmethod
    def RemoveActiveCat(cls, cat_type: str) -> None:
        if cat_type == 'BRUSH':
            act_cat = cls.ActiveBrushCat()
            return cls.BrushManager().remove_brush_cat(act_cat)
        elif cat_type == 'TEXTURE':
            act_cat = cls.ActiveTextureCat()
            return cls.BrushManager().remove_texture_cat(act_cat)

    ''' Textures. '''
    @classmethod
    def GetAllTextureCats(cls) -> List[TextureCategory]:
        return cls.BrushManager().texture_cats.values()

    @classmethod
    def GetTextureCat(cls, cat_idname: Union[str, int], ensure_create: bool = False) -> TextureCategory:# -> SCULPTPLUS_PG_brush_category:
        # return cls.BrushManager(context).get_cat(cat_idname)
        cat = cls.BrushManager().get_texture_cat(cat_idname)
        if cat is None and ensure_create:
            return cls.BrushManager().new_texture_cat(cat_id=cat_idname)
        return cat

    @classmethod
    def ActiveTextureCat(cls) -> TextureCategory:# -> SCULPTPLUS_PG_brush_category:
        # return cls.BrushManager(context).active
        return cls.BrushManager().active_texture_cat

    @classmethod
    def ActiveTextureCatIndex(cls) -> int:
        act_cat = cls.ActiveTextureCat()
        if act_cat is None:
            return -1
        return act_cat.index

    @classmethod
    def GetActiveTextureCatBrushes(cls) -> List[Texture]:
        act_cat = cls.ActiveTextureCat()
        if act_cat is None:
            return []
        return act_cat.items

    @classmethod
    def GetActiveCat(cls, ctx_type: str) -> Union[BrushCategory, TextureCategory, None]:
        if ctx_type == 'BRUSH':
            return cls.ActiveBrushCat()
        elif ctx_type == 'TEXTURE':
            return cls.ActiveTextureCat()
        return None

    @classmethod
    def SetActiveCat(cls, ctx_type: str, cat: Union[BrushCategory, TextureCategory, None]) -> None:
        if cat is None:
            return
        if ctx_type == 'BRUSH':
            Props.BrushManager().active_brush_cat = cat
        elif ctx_type == 'TEXTURE':
            Props.BrushManager().active_texture_cat = cat

    @classmethod
    def GetAllCats(cls, ctx_type: str, skip_active: bool = False) -> Union[List[Union[BrushCategory, TextureCategory]], None]:
        if ctx_type == 'BRUSH':
            cats = Props.GetAllBrushCats()
        elif ctx_type == 'TEXTURE':
            cats = Props.GetAllTextureCats()
        if skip_active:
            act_cat = cls.GetActiveCat(ctx_type)
            cats = [cat for cat in cats if cat != act_cat]
        return cats

    @classmethod
    def GetActiveCatItems(cls, ctx_type: str) -> Union[List[Union[Brush, Texture]], None]:
        act_cat = cls.GetActiveCat(ctx_type)
        if act_cat is not None:
            return act_cat.items
        return None

    @classmethod
    def GetActiveCatItemIds(cls, ctx_type: str) -> List[str]:
        act_cat = cls.GetActiveCat(ctx_type)
        if act_cat is not None:
            return act_cat.item_ids
        return None


    ''' Get brush/texture item. '''
    @classmethod
    def GetBrush(cls, brush_id: str) -> Brush:
        return cls.BrushManager().get_brush(brush_id)

    @classmethod
    def GetTexture(cls, texture_id: str) -> Texture:
        return cls.BrushManager().get_texture(texture_id)

    @classmethod
    def GetActiveBrush(cls) -> Brush:
        return cls.GetBrush(cls.BrushManager().active_brush)

    @classmethod
    def GetActiveTexture(cls) -> Texture:
        return cls.GetTexture(cls.BrushManager().active_texture)

    @classmethod
    def SetActiveBrush(cls, brush: Union[Brush, str]) -> Brush:
        cls.BrushManager().active_brush = brush


    ''' Hotbar. '''
    @classmethod
    def Hotbar(cls) -> HotbarManager:
        return cls.BrushManager().hotbar

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
    def GetHotbarSelectedBrush(cls) -> Union[Brush, None]:
        selected_id: str = cls.GetHotbarSelectedId()
        if selected_id is None:
            return None
        return cls.GetBrush(selected_id)

    @classmethod
    def GetHotbarBrushAtIndex(cls, brush_index: int) -> Brush:
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
    def SetHotbarBrush(cls, slot_index: int, brush: Union[str, Brush]) -> None:
        brush_id: str = brush if isinstance(brush, str) else brush.id
        cls.Hotbar().brushes[slot_index] = brush_id

    @classmethod
    def SwitchHotbarBrushIndices(cls, index_A: int, index_B: int) -> None:
        hotbar: HotbarManager = cls.Hotbar()
        hotbar.brushes[index_A], hotbar.brushes[index_B] = hotbar.brushes[index_B], hotbar.brushes[index_A]

    @classmethod
    def SelectBrush(cls, ctx: Context, brush: Union[str, Brush]) -> None:
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
    def SetHotbarSelected(cls, ctx: Context, selected: Union[int, str, Brush]) -> None:
        cls.Hotbar().selected = selected
        brush = cls.GetHotbarSelectedBrush()
        cls.SelectBrush(ctx, brush)

    @classmethod
    def ToggleHotbarAlt(cls):
        cls.Hotbar().toggle_alt()



class FakeItemContextManager:
    items: List[Union[FakeViewItem_Brush, FakeViewItem_Texture]]

    def __init__(self, mode: str = 'w'):
        from .path import SculptPlusPaths
        self.items: List[Union[FakeViewItem_Brush, FakeViewItem_Texture]] = []
        self.mode: str = mode
        self.json_filepath = SculptPlusPaths.APP__TEMP('fake_items.json')

    def __enter__(self):
        if self.mode == 'r':
            import json
            with open(self.json_filepath, 'r') as f:
                items_data: dict = json.load(f)
                self.deserialize_data(items_data)
        return self

    def deserialize_data(self, items_data: dict) -> None:
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.mode == 'w':
            with open(self.json_filepath, mode='w') as f:
                pass

    def add_item(self, item: Union[FakeViewItem_Brush, FakeViewItem_Texture]) -> None:
        self.items.append(item)


class CM_FakeItem_Brush(FakeItemContextManager):
    items: List[FakeViewItem_Brush]

    def deserialize_data(self, items_data: dict) -> None:
        for item_id, item_data in items_data.items():
            self.brush(item_id, item_data)

    def brush(self, name: str, id: str = '') -> FakeViewItem_Brush:
        brush_item = FakeViewItem_Brush(name)
        self.add_item(brush_item)
        if id:
            brush_item.id = id
        return brush_item

    def brush_from_datablock(self, bl_brush: BlBrush, generate_thumbnail: bool = True) -> FakeViewItem_Brush:
        brush_item = FakeViewItem_Brush.from_bl_brush(bl_brush, generate_thumbnail=generate_thumbnail)
        self.add_item(brush_item)
        return brush_item

class CM_FakeViewItem_Texture(FakeItemContextManager):
    items: List[FakeViewItem_Texture]
