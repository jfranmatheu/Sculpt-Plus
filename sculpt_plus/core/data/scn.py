from bpy.props import PointerProperty, BoolProperty
from bpy.types import Context, Image as BlImage, ImageTexture as BlImageTexture

from ...ackit import ACK


@ACK.Deco.PROP_GROUP.ROOT.SCENE('sculpt_plus')
class SCULPTPLUS_PG_scn:
    @staticmethod
    def get_data(ctx: Context) -> 'SCULPTPLUS_PG_scn':
        return ctx.scene.sculpt_plus

    texture: PointerProperty(type=BlImageTexture)
    image: PointerProperty(type=BlImage, name="Image base")
    image_seq: PointerProperty(type=BlImage, name="Image Base used for sequence source images (PSD)")

    mask_op_use_front_faces_only : BoolProperty(default=False, name="Front Faces Only", description="Affect only faces facing towards the view")
    mask_op_clear_previous_mask : BoolProperty(default=False, name="Clear Previous Masks", description="Does not keep previous masks. Clear everything before the expand operation")
    mask_op_invert : BoolProperty(default=False, name="Invert Mask", description="Invert mask effect")
    mask_op_use_reposition_pivot: BoolProperty(default=False, name="Reposition Pivot", description="Reposition the sculpt transform pivot to the boundary of the expand active area")

    facesets_op_use_front_faces_only : BoolProperty(default=False, name="Front Faces Only", description="Affect only faces facing towards the view")
