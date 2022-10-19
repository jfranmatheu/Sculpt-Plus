from bpy.types import AddonPreferences, Context
from bpy.props import StringProperty
from sculpt_plus.path import SculptPlusPaths


class SCULPTPLUS_AddonPreferences(AddonPreferences):
    bl_idname: str = __package__

    brush_lib_directory: StringProperty(
        name="Brush Library Directory",
        description="Folder where to save your brush sets",
        default=SculptPlusPaths.BRUSH_LIB,
        subtype='DIRECTORY'
    )


def get_prefs(context: Context) -> SCULPTPLUS_AddonPreferences:
    return context.preferences.addons[__package__].preferences
