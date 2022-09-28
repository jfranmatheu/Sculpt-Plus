from typing import List, Set
from uuid import uuid4

import bpy
from bpy.types import Scene as scn, PropertyGroup, Brush
from bpy.props import CollectionProperty, PointerProperty, BoolProperty, StringProperty, IntProperty, EnumProperty


def with_target_set_index(f):
    def wrapper(self, target_set, *args, **kwargs):
        if isinstance(target_set, SculptHotbarBrushSet):
            for i, brush_set in enumerate(self.sets):
                if brush_set == target_set:
                    target_set = i
                    break
        if not isinstance(target_set, int):
            return None
        if target_set == -1:
            if self.active_set_index == -1:
                return None
            target_set = self.active_set_index
        return f(self, target_set, *args, **kwargs)
    return wrapper

def with_active_set(f):
    def wrapper(self, *args, **kwargs):
        if bpy.sculpt_hotbar._cv_instance:
            cv = bpy.sculpt_hotbar._cv_instance
            idx = self.alt_set_index if cv.hotbar.use_secondary and self.alt_set_index != -1 else self.active_set_index
        else:
            idx = self.active_set_index
        if idx == -1:
            return None
        # print(idx)
        return f(self, self.sets[idx], *args, **kwargs)
    return wrapper


class SculptHotbarBrush(PropertyGroup):
    def update_brush(self, context):
        if self.slot is None:
            return
        if not self.slot.use_paint_sculpt:
            self.slot = None

    slot : PointerProperty(type=Brush, update=update_brush, name="Brush Slot")


set_icon_items = tuple(('COLLECTION_COLOR_0%i' % i, "", "", 'COLLECTION_COLOR_0%i' % i, i) for i in range(1, 9))
class SculptHotbarBrushSet(PropertyGroup):
    def update_set_name(self, context):
        set_names: Set[str] = {set.name for set in context.scene.sculpt_hotbar.sets if set != self}
        new_name = self.name
        i: int = 1
        while new_name in set_names:
            new_name = self.name + '.' + str(i).zfill(3)
            i += 1
        if new_name != self.name:
            self.name = new_name

    name : StringProperty(default="Brush Set", update=update_set_name)
    uid : StringProperty(default='')
    version : IntProperty(default=0)
    brushes : CollectionProperty(type=SculptHotbarBrush)
    icon : EnumProperty(
        name="Brush Set Icon",
        items=set_icon_items,
    )

class SculptHotbarPG(PropertyGroup):
    def update_active_set_index(self, ctx=None) -> None:
        if self.active_set_index == -1:
            return
        self.active_set = self.sets[self.active_set_index]
        print("Update active set")

    show_gizmo_sculpt_hotbar : BoolProperty(default=True, description='Enable Sculpt Hotbar')
    #brushes : CollectionProperty(type=SculptHotbarBrush)
    #active_set : PointerProperty(type=SculptHotbarBrushSet)
    active_set_index : IntProperty(default=-1, name="Select Brush Set")#, update=update_active_set_index)
    alt_set_index : IntProperty(default=-1, name="Secondary Selected Brush Set")#, update=update_active_set_index)
    sets : CollectionProperty(type=SculptHotbarBrushSet)

    @property
    def active_set(self) -> SculptHotbarBrushSet:
        if bpy.sculpt_hotbar._cv_instance:
            cv = bpy.sculpt_hotbar._cv_instance
            idx = self.alt_set_index if cv.hotbar.use_secondary else self.active_set_index
        else:
            idx = self.active_set_index
        if idx == -1 or not self.sets:
            return None
        return self.sets[idx]

    @property
    def active_brushes(self) -> List[SculptHotbarBrush]:
        if not self.active_set:
            return None
        return self.active_set.brushes

    ####################################

    def new_set(self) -> SculptHotbarBrushSet:
        new_brush_set: SculptHotbarBrushSet = self.sets.add()
        new_brush_set.uid = uuid4().hex
        new_brush_set.name = "New Brush-Set"
        self.active_set_index = len(self.sets) - 1
        for i in range(10):
            self.add_brush()
        return new_brush_set

    @with_target_set_index
    def remove_set(self, target_brush_set: int = -1) -> None:
        self.sets.remove(target_brush_set)
        if target_brush_set >= len(self.sets):
            self.active_set_index -= 1
        if self.alt_set_index >= len(self.sets):
            self.alt_set_index -= 1
        if self.alt_set_index == self.active_set_index:
            if len(self.sets) < 2:
                return
            if self.alt_set_index != 0:
                self.alt_set_index -= 1
            else:
                self.alt_set_index += 1

    @with_target_set_index
    def move_set(self, target_brush_set: int = -1, direction: int = 0) -> None:
        if direction == 0:
            return
        src_index = target_brush_set
        dst_index = src_index + direction
        if dst_index >= len(self.sets):
            return
        self.sets.move(src_index, dst_index)
        self.active_set_index = dst_index

    @with_target_set_index
    def select_set(self, target_brush_set: int = -1, secondary: bool = False) -> None:
        if secondary:
            self.alt_set_index = target_brush_set
        else:
            self.active_set_index = target_brush_set

    ####################################

    def init_brushes(self):
        # print("INIT BRUSHES!!!")
        if not self.sets or len(self.sets) == 0:
            #  or (len(self.sets) == 1 and len(self.sets[0].brushes)==0)
            import bpy
            def_brushes = (
                'Clay Strips',
                'Blob', 'Inflate/Deflate',
                'Draw Sharp', 'Crease', 'Pinch/Magnify',
                
                'Grab',
                'Elastic Deform',
                'Snake Hook',

                'Scrape/Peaks',
                #'Pose', 'Cloth',
                #'Mask', 'Draw Face Sets'
            )
            new_brush_set = self.new_set()
            new_brush_set.name = "Default"
            for set_brush, br_name in zip(new_brush_set.brushes, def_brushes):
                #b = self.add_brush()
                #if b:
                #    b.slot = bpy.data.brushes.get(name, None)
                set_brush.slot = bpy.data.brushes.get(br_name, None)

    ####################################

    @with_active_set
    def add_brush(self, act_set: SculptHotbarBrushSet):
        if len(act_set.brushes) >= 10:
            return
        return act_set.brushes.add()

    @with_active_set
    def set_brush(self, act_set: SculptHotbarBrushSet, i, br):
        act_set.brushes[i].slot = br

    @with_active_set
    def get_brush(self, act_set: SculptHotbarBrushSet, i):
        if i >= len(act_set.brushes):
            return None
        return act_set.brushes[i].slot

    @with_active_set
    def get_brushes(self, act_set: SculptHotbarBrushSet):
        return [br.slot for br in act_set.brushes]

    @with_active_set
    def get_brush_and_icon(self, act_set: SculptHotbarBrushSet, i):
        if i >= len(act_set.brushes):
            return (None, None)
        b = act_set.brushes[i].slot
        if not b:
            return (None, None)
        return (b, b.preview.icon_id)

    @with_active_set
    def get_brush_icon(self, act_set: SculptHotbarBrushSet, i):
        return act_set.brushes[i].slot.preview.icon_id

    @with_active_set
    def draw_brush(self, act_set: SculptHotbarBrushSet, layout, i):
        layout.prop(act_set.brushes[i], 'slot', text='', icon=self.get_brush_icon(i))

'''
def draw_ui(self, context):
    layout = self.layout.box().column(align=True)
    layout.label(text="Sculpt Hotbar :")
    brushes = context.scene.sculpt_hotbar.brushes
    for brush in brushes:
        layout.prop(brush, 'slot', text='', icon_value=-1 if not brush.slot else brush.slot.preview.icon_id)
'''

def register():
    scn.sculpt_hotbar = PointerProperty(type=SculptHotbarPG)

    #from bpy.types import VIEW3D_PT_tools_brush_select as Panel
    #Panel.append(draw_ui)

#def unregister():
#    from bpy.types import VIEW3D_PT_tools_brush_select as Panel
#    Panel.remove(draw_ui)
