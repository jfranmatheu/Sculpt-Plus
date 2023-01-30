from bpy.types import PropertyGroup
from bpy.props import PointerProperty, BoolProperty, EnumProperty

from sculpt_plus.previews import Previews


toolbar_brush_sections_items = []
def get_toolbar_brush_sections_items(self, context):
    brush = context.tool_settings.sculpt.brush
    items = [
        ('BRUSH_SETTINGS', "Brush", "Brush Settings", 'BRUSH_DATA', 0),
        ('BRUSH_SETTINGS_ADVANCED', "Advanced", "Advanced Brush Settings", 'GHOST_ENABLED', 1),
        ('BRUSH_SETTINGS_STROKE', "Stroke", "Brush Stroke Settings", 'GP_SELECT_STROKES', 2),
        ('BRUSH_SETTINGS_FALLOFF', "Falloff", "Brush Falloff Settings", 'SMOOTHCURVE', 3),
    ]
    if brush.texture is not None:
        items.append(
            ('BRUSH_SETTINGS_TEXTURE', "Texture", "Brush Texture Settings", 'TEXTURE_DATA', 4)
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

    show_brush_settings_panel: BoolProperty(default=False, name="Show Brush Settings")
    show_mask_facesets_panel: BoolProperty(default=True, name="Show Mask/Face Sets Panel")
    show_sculpt_mesh_panel: BoolProperty(default=True, name="Show Sculpt Mesh Panel")

    toolbar_brush_sections: EnumProperty(
        name="Section",
        #description="Brush Settings Sections",
        items=get_toolbar_brush_sections_items
    )

    toolbar_maskfacesets_sections: EnumProperty(
        name="Section",
        #description="Brush Settings Sections",
        items=(
            ('MASK', 'Mask', "Mask Settings", 'MOD_MASK', 0),
            ('FACESETS', 'Face Sets', "Face Sets", Previews.FaceSets.FACE_SETS(), 1) # 'FACE_MAPS'
        ),
        default='MASK'
    )

    toolbar_sculpt_sections: EnumProperty(
        name="Section",
        items=get_toolbar_sculpt_sections_items,
        #default='VOXEL_REMESH'
    )

    mask_panel_tabs: EnumProperty(
        name="Mask Tabs",
        items=(
            ('MASK_EXPAND', "Expand", "Mask Expand Operators"),
            ('MASK_EFFECTS', "Effects", "Mask Effect Operators"),
            ('MASK_FILTERS', "Filters", "Mask Filter Operators"),
            ('MASK_TO_MESH', "To Mesh", "Mask To Mesh Operators"),
        ),
        default='MASK_FILTERS'
    )
