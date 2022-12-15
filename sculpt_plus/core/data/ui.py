from bpy.types import PropertyGroup
from bpy.props import PointerProperty, BoolProperty, EnumProperty


toolbar_brush_sections_items = []
def get_toolbar_brush_sections_items(self, context):
    brush = context.tool_settings.sculpt.brush
    items = [
        ('BRUSH_SETTINGS', "", "", 'BRUSH_DATA', 0),
        ('BRUSH_SETTINGS_ADVANCED', "", "", 'GHOST_ENABLED', 1),
        ('BRUSH_SETTINGS_STROKE', "", "", 'GP_SELECT_STROKES', 2),
        ('BRUSH_SETTINGS_FALLOFF', "", "", 'SMOOTHCURVE', 3),
    ]
    if brush.texture is not None:
        items.append(
            ('BRUSH_SETTINGS_TEXTURE', "", "", 'TEXTURE_DATA', 4)
        )
    return items


class SCULPTPLUS_PG_ui_toggles(PropertyGroup):
    show_brush_settings: BoolProperty(default=True)
    show_brush_settings_advanced: BoolProperty(default=False)
    show_brush_settings_stroke: BoolProperty(default=False)
    show_brush_settings_falloff: BoolProperty(default=False)
    show_brush_settings_texture: BoolProperty(default=False)

    toolbar_brush_sections: EnumProperty(
        name="Brush Settings Sections",
        description="Brush Settings Sections",
        items=get_toolbar_brush_sections_items
    )
