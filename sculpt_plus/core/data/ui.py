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


def get_toolbar_sculpt_sections_items(self, context):
    if context.sculpt_object.use_dynamic_topology_sculpting:
        return (
            ('DYNTOPO', "Dyntopo", "Dyntopo Options", 'MESH_ICOSPHERE', 2),
        )
    ob = context.sculpt_object
    md = None
    for mod in ob.modifiers:
        if mod.type == 'MULTIRES':
            md = mod
            break
    if md is not None and md.total_levels > 0:
        return (
            ('MULTIRES', "Multires", "Multires Options", 'MOD_MULTIRES', 3),
        )

    return (
        ('VOXEL_REMESH', "Voxel Remesh", "Voxel Remesh Options", 'FILE_VOLUME', 0),
        ('QUAD_REMESH', "Quad Remesh", "Quad Remesh Options", 'MOD_REMESH', 1),
        ('DYNTOPO', "Dyntopo", "Dyntopo Options", 'MESH_ICOSPHERE', 2),
        ('MULTIRES', "Multires", "Multires Options", 'MOD_MULTIRES', 3)
    )

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
    
    toolbar_sculpt_sections: EnumProperty(
        name="Sculpt Sections",
        items=get_toolbar_sculpt_sections_items,
        #default='VOXEL_REMESH'
    )
