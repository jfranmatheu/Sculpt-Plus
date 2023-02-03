from bpy.types import PropertyGroup, Context, Scene as SCN
from bpy.props import PointerProperty, BoolProperty
from bpy.types import Context, Image as BlImage, ImageTexture as BlImageTexture


class SCULPTPLUS_PG_scn(PropertyGroup):
    @staticmethod
    def get_data(ctx: Context) -> 'SCULPTPLUS_PG_scn':
        return ctx.scene.sculpt_plus

    texture: PointerProperty(type=BlImageTexture)
    image: PointerProperty(type=BlImage, name="Image base")
    image_seq: PointerProperty(type=BlImage, name="Image Base used for sequence source images (PSD)")

    mask_op_use_front_faces_only : BoolProperty(default=False, name="Front Faces Only", description="Affect only faces facing towards the view")
    mask_op_clear_previous_mask : BoolProperty(default=False, name="Clear Previous Masks", description="Does not keep previous masks. Clear everything before the expand operation")
    mask_op_invert : BoolProperty(default=False, name="Invert Mask", description="Invert mask effect")

    facesets_op_use_front_faces_only : BoolProperty(default=False, name="Front Faces Only", description="Affect only faces facing towards the view")

# -------------------------------------------------------------------


def register():
    SCN.sculpt_plus = PointerProperty(type=SCULPTPLUS_PG_scn)
