from typing import Tuple
import bpy
from bpy.types import Operator
from bpy.props import IntProperty, EnumProperty, BoolProperty
from sculpt_hotbar.prefs import get_prefs


class SCULPTHOTBAR_OT_set_brush(Operator):
    bl_idname = 'sculpt_hotbar.set_brush'
    bl_label = "Set Active Brush"
    bl_description = "Sets the current active brush into this hotbar slot"

    index : IntProperty(default=-1)

    @classmethod
    def poll(cls, context):
        return context.mode == 'SCULPT' and context.tool_settings.sculpt.brush and context.scene.sculpt_hotbar.active_set

    def execute(self, context):
        if self.index == -1:
            return {'CANCELLED'}
        act_set = context.scene.sculpt_hotbar.active_set
        if self.index >= len(act_set.brushes):
            return {'CANCELLED'}
        act_set.brushes[self.index].slot = context.tool_settings.sculpt.brush
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
