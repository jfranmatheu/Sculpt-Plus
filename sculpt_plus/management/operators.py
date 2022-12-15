import bpy
from bpy.types import Operator
from pathlib import Path
from bpy.path import abspath
from bpy.props import StringProperty, EnumProperty
from sculpt_plus.props import Props
from bpy_extras.io_utils import ImportHelper
from tempfile import TemporaryDirectory
import subprocess
import sys
import json
from sculpt_plus.path import ScriptPaths, SculptPlusPaths

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

class SCULPTPLUS_OT_import_create_cat(Operator, ImportHelper):
    bl_idname: str = 'sculpt_plus.import_create_cat'
    bl_label: str = "Import data from library and create a new category"

    filename_ext = ".blend"
    filter_glob: StringProperty(default=("*.blend;*" + ";*.".join(['png', 'jpg', 'jpeg'])), options={'HIDDEN'}) # bpy.path.extensions_image

    cat_type: StringProperty()

    #def invoke(self, context, event):
    #    return context.window_manager.invoke_props_popup(self, event)

    def execute(self, context):
        filepath: Path = Path(abspath(self.filepath))
        print(filepath)

        if not filepath.exists():
            return {'CANCELLED'}

        if filepath.suffix == ".blend":
            return {self.load_blendlib(context)}

        elif filepath.suffix in {'.png', '.jpg', '.jpeg'}:
            self.load_image(context)

        elif filepath.is_dir():
            self.load_imagelib(context)

        return {'FINISHED'}


    def load_blendlib(self, context):
        brushes = None
        images = None
        with bpy.data.libraries.load(self.filepath) as (data_from, data_to):
            if self.cat_type == 'BRUSH':
                brushes = list(data_from.brushes)
                # images = list(data_from.images)
            elif self.cat_type == 'TEXTURE':
                images = list(data_from.images)

        if brushes:
            from sculpt_plus.management.manager import builtin_brush_names
            brushes_set = set(brushes)
            for brush_name in builtin_brush_names:
                if brush_name in brushes_set:
                    brushes_set.remove(brush_name)
            brushes = list(brushes_set)

        elif images:
            images_set = set(images)
            builtin_images_names = ('Render Result', 'Viewer Node')
            for image_name in builtin_images_names:
                if image_name in images_set:
                    images_set.remove(image_name)
            images = list(images_set)


        # RUN ANOTHER BLENDER INSTANCE IN BACKGROUND,
        # EXECUTE AN SCRIPT THAT SAVES THE BRUSH ICONS AND TEXTURES
        # AS THUMBNAILS OF 100X100 PX IN A KNOWN TEMPORAL FOLDER.
        temporal_dir = SculptPlusPaths.APP__TEMP() # TemporaryDirectory(prefix="sculpt_plus_")
        args = (
            str(temporal_dir),
            '#$#'.join(brushes) if brushes else 'NONE',
            '#$#'.join(images) if images else 'NONE',
        )

        process = subprocess.Popen(
            [
                bpy.app.binary_path,
                abspath(self.filepath),
                '--background',
                '--python',
                ScriptPaths.GENERATE_THUMBNAILS,
                '--',
                *args
            ],
            #stdout=subprocess.PIPE,
            #stderr=subprocess.PIPE,
            shell=True
        )

        #out, err = process.communicate()
        return_code = process.wait()
        if return_code != 0:
            #print(err)
            return 'CANCELLED'

        temporal_dir: Path = Path(temporal_dir)
        assets_importer_json_file = temporal_dir / 'asset_importer_data.json'
        if not assets_importer_json_file.exists() or not assets_importer_json_file.is_file():
            return 'CANCELLED'

        data = {}
        with assets_importer_json_file.open('r') as json_file:
            data = json.load(json_file)

        print(data)

        if not data:
            return 'CANCELLED'

        bpy.sculpt_hotbar._cv_instance.mod_asset_importer.show(
            self.filepath,
            type=self.cat_type,
            data=data,
        )

        #print(out)
        return 'FINISHED'
