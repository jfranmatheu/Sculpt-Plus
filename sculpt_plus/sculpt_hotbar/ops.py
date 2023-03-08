from typing import Tuple, Set, List
from pathlib import Path

import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
from bpy.props import IntProperty, EnumProperty, BoolProperty, StringProperty

from sculpt_plus.prefs import get_prefs
from sculpt_plus.props import Props


enum_items = [('NONE', 'NONE', '')]
op_pointer = None
class SCULPTPLUS_OT_move_item_to_another_cat(Operator):
    """Move an item to another category"""
    bl_idname = "sculpt_plus.move_item_to_another_cat"
    bl_label = "Move Item To Another Category"
    bl_description = "Move an item to another category"
    bl_options = {'REGISTER', 'UNDO'}

    item_id: StringProperty(options={'SKIP_SAVE', 'HIDDEN'})
    cat_type: StringProperty(options={'SKIP_SAVE', 'HIDDEN'})

    def get_enum_items(self, context) -> List[Tuple[str, str, str]]:
        global op_pointer
        if op_pointer is not None and op_pointer == self.as_pointer():
            return enum_items
        enum_items.clear()
        if self.cat_type == 'BRUSH':
            cats = Props.GetAllBrushCats()
            act_cat = Props.ActiveBrushCat()
        elif self.cat_type == 'TEXTURE':
            cats = Props.GetAllTextureCats()
            act_cat = Props.ActiveTextureCat()
        else:
            return [('NONE', 'NONE', '')]

        for cat in cats:
            if act_cat == cat:
                continue
            enum_items.append((cat.id, cat.name, ""))
        op_pointer = self.as_pointer()
        return enum_items

    bl_property = 'enum'
    enum: EnumProperty(
        name="Category List",
        items=get_enum_items,
        options={'SKIP_SAVE'}
    )

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.mode == 'SCULPT'

    #def draw(self, context):
    #    layout = self.layout
    #    layout.prop()

    def invoke(self, context, event) -> Set[str]:
        global op_pointer
        op_pointer = None
        if not self.item_id or not self.cat_type:
            return {'CANCELLED'}
        if self.cat_type == 'BRUSH':
            if Props.BrushCatsCount() <= 1:
                return {'CANCELLED'}
            act_cat = Props.ActiveBrushCat()
        elif self.cat_type == 'TEXTURE':
            if Props.TextureCatsCount() <= 1:
                return {'CANCELLED'}
            act_cat = Props.ActiveTextureCat()
        else:
            return {'CANCELLED'}
        if self.item_id not in act_cat.item_ids:
            return {'CANCELLED'}
        context.window_manager.invoke_search_popup(self)
        return {'INTERFACE'}

    def execute(self, context) -> Set[str]:
        global op_pointer
        op_pointer = None
        if self.cat_type == 'BRUSH':
            Props.BrushManager().move_brush(self.item_id, from_cat=None, to_cat=self.enum)
        elif self.cat_type == 'TEXTURE':
            Props.BrushManager().move_texture(self.item_id, from_cat=None, to_cat=self.enum)
        return {'FINISHED'}


class SCULPTPLUST_OT_assign_icon_to_brush(Operator, ImportHelper):
    """Assign an icon to a brush"""
    bl_idname = "sculpt_plus.assign_icon_to_brush"
    bl_label = "Assign Icon To Brush"
    bl_description = "Assign an icon to a brush"

    brush_id: StringProperty(options={'SKIP_SAVE', 'HIDDEN'})
    # item_id: StringProperty(options={'SKIP_SAVE', 'HIDDEN'})
    # item_type: StringProperty(options={'SKIP_SAVE', 'HIDDEN'})

    def execute(self, context):
        # print(self.filepath, " ######## ", self.properties.filepath)
        if not self.filepath:
            return {'CANCELLED'}
        image_path: Path = Path(self.filepath)
        if not image_path.exists() or not image_path.is_file():
            return {'CANCELLED'}
        if image_path.suffix not in {'.png', '.jpg', 'jpeg'}:
            return {'CANCELLED'}
        # OK is an image file...
        #if self.item_type == 'BRUSH':
        #    item = Props.GetBrush(self.item_id)
        #elif self.item_type == 'TEXTURE':
        #    item = Props.GetTexture(self.item_id)
        item = Props.GetBrush(self.brush_id)
        if item is not None:
            item.use_custom_icon = True
            item.icon_filepath = str(image_path)
            # item.load_icon(str(image_path))
        return{'FINISHED'}


class SCULPTPLUS_OT_assign_icon_to_cat(Operator, ImportHelper):
    """Assign an icon to a brush"""
    bl_idname = "sculpt_plus.assign_icon_to_cat"
    bl_label = "Assign Icon To Category"
    bl_description = "Assign an icon to a category"

    cat_id: StringProperty(options={'SKIP_SAVE', 'HIDDEN'})
    cat_type: StringProperty(options={'SKIP_SAVE', 'HIDDEN'})

    def execute(self, context):
        if not self.filepath:
            return {'CANCELLED'}
        image_path: Path = Path(self.filepath)
        if not image_path.exists() or not image_path.is_file():
            return {'CANCELLED'}
        if image_path.suffix not in {'.png', '.jpg', 'jpeg'}:
            return {'CANCELLED'}
        if self.cat_type == 'BRUSH':
            cat = Props.GetBrushCat(self.cat_id)
        elif self.cat_type == 'TEXTURE':
            cat = Props.GetTextureCat(self.cat_id)
        if cat is not None:
            # cat.load_icon(str(image_path))
            cat.icon.set_filepath(str(image_path), lazy_generate=True)
        return{'FINISHED'}


class SCULPTHOTBAR_OT_set_brush(Operator):
    bl_idname = 'sculpt_hotbar.set_brush'
    bl_label = "Set Active Brush"
    bl_description = "Sets the current active brush into this hotbar slot"

    index : IntProperty(default=-1)

    @classmethod
    def poll(cls, context):
        return context.mode == 'SCULPT' and context.tool_settings.sculpt.brush # and context.scene.sculpt_hotbar.active_set

    def execute(self, context):
        if self.index == -1:
            return {'CANCELLED'}
        # act_set = context.scene.sculpt_hotbar.active_set
        # if self.index >= len(act_set.brushes):
        #     return {'CANCELLED'}
        # act_set.brushes[self.index].slot = context.tool_settings.sculpt.brush
        ## br_index: int = 9 if self.index==0 else self.index - 1
        Props.SetHotbarSelected(context, self.index)
        return {'FINISHED'}


class SCULPTHOTBAR_OT_select_brush(Operator):
    bl_idname = 'sculpt_hotbar.select_brush'
    bl_label = "Select Sculpt Hotbar Brush"
    bl_description = "Selects a brush from hotbar slot"

    index : IntProperty(default=-1)

    @classmethod
    def poll(cls, context):
        return context.mode == 'SCULPT' and context.scene.sculpt_hotbar.show_gizmo_sculpt_hotbar and context.scene.sculpt_hotbar.active_set

    def execute(self, context):
        if self.index == -1:
            return {'CANCELLED'}
        act_set = context.scene.sculpt_hotbar.active_set
        if self.index >= len(act_set.brushes):
            return {'CANCELLED'}
        br = act_set.brushes[self.index].slot
        if not br:
            return {'CANCELLED'}
        context.tool_settings.sculpt.brush = br
        return {'FINISHED'}


class SCULPTHOTBAR_OT_show_sets(Operator):
    bl_idname = 'sculpt_hotbar.show_sets'
    bl_label = "Show Sculpt Hotbar's Sets"
    bl_description = "Switch Brush-Set"

    @classmethod
    def poll(cls, context):
        return context.mode == 'SCULPT' and context.scene.sculpt_hotbar.show_gizmo_sculpt_hotbar and context.scene.sculpt_hotbar.active_set

    @staticmethod
    def draw(self, context):
        #prop_search
        self.layout.prop(get_prefs(context), 'set_list')

        col = self.layout.column(align=True)
        col.operator('render.render', text='Save and Create Set')
        col.alert=True
        col.operator('render.render', text='Clear Current Set')
        col.operator('render.render', text='Remove Current Set')

    def invoke(self, context, event):
        #context.window.cursor_warp(context.area.x + context.area.width/2, context.area.y + context.area.height/2)
        #context.window_manager.invoke_search_popup(self)#, event)
        context.window.cursor_warp(event.mouse_region_x, event.mouse_region_y + 100)
        context.window_manager.popover(self.__class__.draw, ui_units_x=12) # title="Brush-Set Context Menu", icon='PROPERTIES')
        return {'INTERFACE'}

    def execute(self, context):
        #if not self.set_list or self.set_list == 'NONE':
        #    return {'FINISHED'}

        return {'FINISHED'}


class BrushSetAction:
    bl_description = ""

    index : IntProperty(default=-1)

    @classmethod
    def poll(cls, context):
        return context.mode == 'SCULPT' and context.scene.sculpt_hotbar.sets

    def execute(self, context):
        self.__class__.action(context.scene.sculpt_hotbar, self.index, *self.get_action_args())
        return {'FINISHED'}

    def get_action_args(self) -> Tuple:
        return ()

    @staticmethod
    def action(hotbar, set_index: int, *args):
        pass


class SCULPTHOTBAR_OT_remove_set(Operator, BrushSetAction):
    bl_idname = 'sculpt_hotbar.remove_set'
    bl_label = "Remove Set"
    bl_description = "Removes Active Brush Set"

    @staticmethod
    def action(hotbar, set_index: int):
        hotbar.remove_set(set_index)


class SCULPTHOTBAR_OT_select_set(Operator, BrushSetAction):
    bl_idname = 'sculpt_hotbar.select_set'
    bl_label = "Select Set"
    bl_description = "Selects Brush Set"

    @staticmethod
    def action(hotbar, set_index: int):
        hotbar.select_set(set_index)


class SCULPTHOTBAR_OT_new_set(Operator, BrushSetAction):
    bl_idname = 'sculpt_hotbar.new_set'
    bl_label = "New Set"
    bl_description = "Creates a new Brush Set"

    @staticmethod
    def action(hotbar, *_):
        print("New Set")
        hotbar.new_set()


class SCULPTHOTBAR_OT_move_set(Operator, BrushSetAction):
    bl_idname = 'sculpt_hotbar.move_set'
    bl_label = "Move Set"
    bl_description = "Moves Up/Down Active Brush Set"

    direction: IntProperty(default=0)

    def get_action_args(self) -> Tuple:
        return (self.direction,)

    @staticmethod
    def action(hotbar, set_index: int, move_direction: int):
        hotbar.move_set(set_index, move_direction)


class SCULPTHOTBAR_OT_set_secondary_set(Operator, BrushSetAction):
    bl_idname = 'sculpt_hotbar.set_secondary_set'
    bl_label = "Set Secondary Brush-Set"
    bl_description = "Set Secondary/Alternative Brush-Set to switch on air with [Alt] key"

    @staticmethod
    def action(hotbar, set_index: int):
        hotbar.select_set(set_index, secondary=True)


class SCULPTHOTBAR_OT_swap_set(Operator, BrushSetAction):
    bl_idname = 'sculpt_hotbar.swap_set'
    bl_label = "Swap Secondary Brush-Set"
    bl_description = "Swap to Secondary/Alternative Brush-Set"

    enabled: BoolProperty(default=False)

    def get_action_args(self) -> Tuple:
        return (self.enabled,)

    @staticmethod
    def action(hotbar, set_index: int, enabled: bool):
        if bpy.sculpt_hotbar._cv_instance:
            bpy.sculpt_hotbar._cv_instance.hotbar.use_secondary = enabled
            bpy.context.area.tag_redraw()
