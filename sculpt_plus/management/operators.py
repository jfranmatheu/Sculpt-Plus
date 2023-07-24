import bpy
from bpy.types import Operator
from pathlib import Path
from bpy.path import abspath
from bpy.props import StringProperty, EnumProperty, BoolProperty
from sculpt_plus.props import Props
from bpy_extras.io_utils import ImportHelper
from tempfile import TemporaryDirectory
import subprocess
import sys
import json
from collections import deque
import numpy as np
from sculpt_plus.path import ScriptPaths, SculptPlusPaths, DBShelf, DBShelfManager
from sculpt_plus.props import Texture



'''
class SCULPTPLUS_OT_debug_fill_brush_categories(Operator):
    bl_idname: str = 'debug.fill_brush_categories'
    bl_label: str = "Debug: Fill Brush Categories"

    cat_names = (
        'Best of JF',
        'Rocks', 'Scratches', 'Skin', 'Monsters', 'Fabric',
        'Random but nice', 'Stamps', 'Wood', 'Metal'
    )

    def execute(self, context):
        br_manager = context.window_manager.sculpt_plus.brush_manager

        with bpy.data.libraries.load("D:\\RESOURCES\\3D RSS\\Blender_Assets\\_Brushes\\OrbBrushes\\OrbBrushes.blend") as (data_from, data_to):
            data_to.brushes = data_from.brushes

        cat = br_manager.new_cat('Orb Brushes')
        for brush in data_to.brushes:
            cat.add_brush(brush)

        for cat_name in self.cat_names:
            br_manager.new_cat(cat_name)

        br_manager.set_active(cat)
        return {'FINISHED'}
'''

# TODO: Operator to handle the import of brush library and texture library and textures from path.

class SCULPTPLUS_OT_toggle_hotbar_alt(Operator):
    bl_idname: str = 'sculpt_plus.toggle_hotbar_plus'
    bl_label: str = "Toggle Hotbar Alt Brush-Set"

    def execute(self, context):
        Props.ToggleHotbarAlt()
        return {'FINISHED'}


class SCULPTPLUS_OT_set_hotbar_alt(Operator):
    bl_idname: str = 'sculpt_plus.set_hotbar_plus'
    bl_label: str = "Enable/Disable Hotbar Alt Brush-Set"

    enabled: BoolProperty()

    def execute(self, context):
        Props.Hotbar().use_alt = self.enabled
        return {'FINISHED'}


class SCULPTPLUS_OT_new_cat(Operator):
    bl_idname: str = 'sculpt_plus.new_cat'
    bl_label: str = "Create a new category"

    cat_type: StringProperty(default='BRUSH', options={'HIDDEN'})
    cat_name: StringProperty(name="Category Name", default="Untitled Category")
    # cat_iconpath: StringProperty(name="Category Icon", default="", subtype='FILE_PATH')

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=250)

    def execute(self, context):
        Props.NewCat(self.cat_type, self.cat_name if self.cat_name != "Untitled Category" else None)
        return {'FINISHED'}


class SCULPTPLUS_OT_rename_item(Operator):
    bl_idname: str = 'sculpt_plus.rename_item'
    bl_label: str = "Rename Item"

    item_type: EnumProperty(
        name="Item Type",
        items=(
            ('BRUSH', "Brush", ""),
            ('TEXTURE', "Texture", ""),
            ('CAT_BRUSH', "Brush Category", ""),
            ('CAT_TEXTURE', "Texture Category", ""),
        ),
        options={'HIDDEN'}
    )
    item_id: StringProperty(name="Item ID", options={'HIDDEN'})

    item_name: StringProperty(name="Name")

    def draw(self, context):
        from bpy.types import UILayout
        name = UILayout.enum_item_name(self, 'item_type', self.item_type)
        self.layout.prop(self, 'item_name', text=name + ' Name')

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=250)

    def execute(self, context):
        if self.item_type == 'BRUSH':
            item = Props.GetBrush(self.item_id)
        elif self.item_type == 'TEXTURE':
            item = Props.GetTexture(self.item_id)
        elif self.item_type == 'CAT_BRUSH':
            item = Props.GetBrushCat(self.item_id)
        elif self.item_type == 'CAT_TEXTURE':
            item = Props.GetTextureCat(self.item_id)
        if item is None:
            return {'CANCELLED'}
        if item.name == self.item_name:
            return {'CANCELLED'}
        if self.item_name == '' or self.item_name.replace(' ', '') == '':
            self.item_name = "idk how to write"

        item.name = self.item_name
        return {'FINISHED'}
