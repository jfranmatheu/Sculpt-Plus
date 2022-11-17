import bpy
from bpy.types import Operator


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
