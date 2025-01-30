import bpy
from bpy.types import Operator, ImageTexture
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper

from os.path import isfile, basename

from ...ackit import ACK


@ACK.Deco.OPS.IMPORT('jpg', 'jpeg', 'png', 'bmp', 'psd', '.tiff', 'tif')
class ImportTexture:
    label = "Import Texture"
    tooltip = "Import texture from an image file and asign it to the active brush"

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

        # BM.add_bl_texture(context, new_tex, set_active=True)

        return {'FINISHED'}


class UnasignTexture(ACK.Type.OPS.ACTION):
    label = "Unasign Texture"
    tooltip = "Un-asign the texture from the Brush"

    @classmethod
    def poll(cls, context):
        return context.mode == "SCULPT" and context.sculpt_object is not None and context.tool_settings.sculpt.brush is not None

    def action(self, context):
        if context.tool_settings.sculpt.brush.texture is None:
            return -1

        act_brush = context.tool_settings.sculpt.brush
        act_brush.texture = None
        
        '''
        act_brush_item = BM.active_brush

        if act_brush['uuid'] == act_brush_item.uuid:
            act_brush_item.texture = None
        '''
