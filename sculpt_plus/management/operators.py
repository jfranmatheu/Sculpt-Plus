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

class SCULPTPLUS_OT_import_create_cat(Operator, ImportHelper):
    bl_idname: str = 'sculpt_plus.import_create_cat'
    bl_label: str = "Import data from library and create a new category"

    filename_ext = ".blend"
    filter_glob: StringProperty(default=("*.blend;*" + ";*.".join(['png', 'jpg', 'jpeg'])), options={'HIDDEN'}) # bpy.path.extensions_image

    cat_type: StringProperty(options={'HIDDEN'})
    source_type: StringProperty(options={'HIDDEN'})
    cat_name: StringProperty(default="Blend-Lib Category")

    #def invoke(self, context, event):
    #    return context.window_manager.invoke_props_popup(self, event)

    def execute(self, context):
        filepath: Path = Path(abspath(self.filepath))
        print(filepath)

        if not filepath.exists():
            return {'CANCELLED'}

        if filepath.suffix == ".blend":
            self.source_type = 'LIBRARY'
            return {self.load_blendlib(context)}

        elif filepath.suffix in {'.png', '.jpg', '.jpeg'}:
            self.source_type = 'SINGLE IMAGE'
            self.load_image(context)

        elif filepath.is_dir():
            self.source_type = 'FOLDER'
            self.load_imagelib(context)

        return {'FINISHED'}


    def load_blendlib(self, context):
        self.cv = Props.Canvas()
        self.mod_asset_importer = self.cv.mod_asset_importer

        from sculpt_plus.core.sockets.pbar_server import PBarServer
        pbar = PBarServer()
        pbar.set_update_callback(self.on_progress_update)
        pbar.start()
        self.pbar = pbar

        self.region = context.region

        # RUN ANOTHER BLENDER INSTANCE IN BACKGROUND,
        # EXECUTE AN SCRIPT THAT SAVES THE BRUSH ICONS AND TEXTURES
        # AS THUMBNAILS OF 100X100 PX IN A KNOWN TEMPORAL FOLDER.
        temporal_dir = SculptPlusPaths.APP__TEMP() # TemporaryDirectory(prefix="sculpt_plus_")
        args = (
            str(temporal_dir),
            self.cat_type,
            str(pbar.port)
            #'#$#'.join(brushes) if brushes else 'NONE',
            #'#$#'.join(images) if images else 'NONE',
        )

        self.process = subprocess.Popen(
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

        #print(out)
        self.cv.progress_start(label=f"Loading {self.cat_type.capitalize()} data from {self.source_type.capitalize()}")

        context.window_manager.modal_handler_add(self)
        self._timer = context.window_manager.event_timer_add(0.1, window=context.window)
        return 'RUNNING_MODAL' # 'FINISHED'

    def modal(self, context, event):
        res = self.pbar.run_in_modal()
        if res == 'FINISHED':
            self.done(context)
        elif res == 'CANCELLED': # in {'FINISHED', 'CANCELLED'}:
            self.error(context)
        print(res)
        return {res}

    def on_progress_update(self, progress: float) -> None:
        print("[MODAL] Progress:", progress)
        self.region.tag_redraw()
        self.cv.progress_update(progress, None)

    def cleanup(self, context):
        context.window_manager.event_timer_remove(self._timer)
        del self._timer
        self.cv.progress_stop()
        self.pbar.stop()
        del self.pbar

    def error(self, context) -> None:
        self.cleanup(context)

    def done(self, context) -> str:
        self.cleanup(context)

        #out, err = process.communicate()
        return_code = self.process.wait()
        if return_code != 0:
            #print(err)
            return 'CANCELLED'
        
        temporal_dir = SculptPlusPaths.APP__TEMP()
        temporal_dir: Path = Path(temporal_dir)
        assets_importer_json_file = temporal_dir / 'asset_importer_data.json'
        if not assets_importer_json_file.exists() or not assets_importer_json_file.is_file():
            return 'CANCELLED'

        data = {}
        with assets_importer_json_file.open('r') as json_file:
            data = json.load(json_file)

        # print(data)

        if not data:
            return 'CANCELLED'

        self.mod_asset_importer.show(
            self.filepath,
            type=self.cat_type,
            data=data,
        )
        return 'FINISHED'
