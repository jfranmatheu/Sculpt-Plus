from bpy.types import PropertyGroup, Context, Scene as SCN
from bpy.props import PointerProperty
from bpy.types import Context, Image as BlImage, ImageTexture as BlImageTexture


class SCULPTPLUS_PG_scn(PropertyGroup):
    @staticmethod
    def get_data(ctx: Context) -> 'SCULPTPLUS_PG_scn':
        return ctx.scene.sculpt_plus

    texture: PointerProperty(type=BlImageTexture)


# -------------------------------------------------------------------


def register():
    SCN.sculpt_plus = PointerProperty(type=SCULPTPLUS_PG_scn)
