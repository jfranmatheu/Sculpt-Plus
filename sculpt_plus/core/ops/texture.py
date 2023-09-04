import bpy
from bpy.types import Operator, ImageTexture
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper

from os.path import isfile, basename



class SCULPTPLUS_OT_import_texture(Operator, ImportHelper):
    bl_idname = "sculpt_plus.import_texture"
    bl_label = "Import Texture"
    bl_description = "Import texture from an image file and asign it to the active brush"
    
    filter_glob: StringProperty(options={'HIDDEN'}, default='*.jpg;*.jpeg;*.png;*.bmp;*.psd;*.tiff;*.tif')

    @classmethod
    def poll(cls, context):
        return context.mode == "SCULPT" and context.sculpt_object is not None and context.tool_settings.sculpt.brush is not None

    def execute(self, context):
        if not isfile(self.filepath):
            return {'CANCELLED'}

        loaded_image = bpy.data.images.load(self.filepath)

        if loaded_image is None:
            return {'CANCELLED'}
        
        is_sequence = self.filepath.endswith(('.psd', '.tiff', '.tif'))
        new_tex: ImageTexture = bpy.data.textures.new(basename(self.filepath), 'IMAGE')
        new_tex.image = loaded_image
        
        from sculpt_plus.globals import G
        G.bm_data.add_bl_texture(context, new_tex, set_active=True)

        return {'FINISHED'}
