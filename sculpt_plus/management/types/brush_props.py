import bpy
from bpy.types import Property, BrushCapabilitiesSculpt, BrushCapabilities, BrushCurvesSculptSettings, BrushTextureSlot
from bpy.types import Brush as BlBrush, Image as BlImage, Texture as BlTexture

from typing import Dict, Tuple, List, Set, Union

from .generated import BaseBrush



brush_properties: Dict[str, Property] = lambda : bpy.types.Brush.bl_rna.properties

exclude_properties: Set[str] = {'direction'}

# ['DRAW', 'DRAW_SHARP', 'CLAY', 'CLAY_STRIPS', 'CLAY_THUMB',
# 'LAYER', 'INFLATE', 'BLOB', 'CREASE', 'SMOOTH', 'FLATTEN',
# 'FILL', 'SCRAPE', 'MULTIPLANE_SCRAPE', 'PINCH', 'GRAB',
# 'ELASTIC_DEFORM', 'SNAKE_HOOK', 'THUMB', 'POSE', 'NUDGE',
# 'ROTATE', 'TOPOLOGY', 'BOUNDARY', 'CLOTH', 'SIMPLIFY', 'MASK',
# 'DRAW_FACE_SETS', 'DISPLACEMENT_ERASER', 'DISPLACEMENT_SMEAR',
# 'PAINT', 'SMEAR']
sculpt_tool_items: Tuple[str] = tuple(item.identifier for item in BlBrush.bl_rna.properties['sculpt_tool'].enum_items)

specific_brush_properties = {
    'DRAW': {},
    'DRAW_SHARP': {},
    'CLAY': {
        'plane_offset',
        'plane_trim',
        'use_plane_trim',
    },
    'CLAY_STRIPS': {
        'plane_offset',
        'plane_trim',
        'use_plane_trim',
        'tip_roundness',
    },
    'CLAY_THUMB': {
        'plane_offset',
        'plane_trim',
        'use_plane_trim',
    },
    'LAYER': {
        'height',
        'use_persistent',
    },
    'INFLATE': {},
    'BLOB': {
        'crease_pinch_factor',
    },
    'CREASE': {
        'crease_pinch_factor',
    },
    'SMOOTH': {
        'smooth_deform_type',
        'surface_smooth_shape_preservation',
        'surface_smooth_current_vertex',
        'surface_smooth_iterations',
    },
    'FLATTEN': {
        'plane_offset',
        'plane_trim',
        'use_plane_trim',
    },
    'FILL': {
        'plane_offset',
        'plane_trim',
        'use_plane_trim',
        'area_radius_factor',
        'invert_to_scrape_fill',
    },
    'SCRAPE': {
        'plane_offset',
        'plane_trim',
        'use_plane_trim',
        'area_radius_factor',
        'invert_to_scrape_fill',
    },
    'MULTIPLANE_SCRAPE': {
        'multiplane_scrape_angle',
        'use_multiplane_scrape_dynamic',
        'show_multiplane_scrape_planes_preview',
    },
    'PINCH': {},
    'GRAB': {
        'normal_weight',
        'use_grab_active_vertex',
        'use_grab_silhouette',
    },
    'ELASTIC_DEFORM': {
        'normal_weight',
        'elastic_deform_type',
        'elastic_deform_volume_preservation',
    },
    'SNAKE_HOOK': {
        'normal_weight',
        'crease_pinch_factor',
        'rake_factor',
        'snake_hook_deform_type',
    },
    'THUMB': {},
    'POSE': {
        'deform_target',
        'pose_deform_type',
        'pose_origin_type',
        'pose_smooth_iterations',
        'pose_ik_segments',
        'pose_offset',
        'use_pose_ik_anchored',
        'use_connected_only',
        'disconnected_distance_max',
    },
    'NUDGE': {},
    'ROTATE': {},
    'TOPOLOGY': {
        'slide_deform_type',
    },
    'BOUNDARY': {
        'deform_target',
        'boundary_deform_type',
        'boundary_falloff_type',
        'boundary_offset',
    },
    'CLOTH': {
        'use_persistent',
        'cloth_simulation_area_type',
        'cloth_sim_limit',
        'cloth_sim_falloff',
        'use_cloth_pin_simulation_boundary',
        'cloth_deform_type',
        'cloth_force_falloff_type',
        'cloth_mass',
        'cloth_damping',
        'cloth_constraint_softbody_strength',
        'use_cloth_collision',
    },
    'SIMPLIFY': {},
    'MASK': {
        'mask_tool', # only for mask tool.
    },
    'DRAW_FACE_SETS': {},
    'DISPLACEMENT': {},
    'DISPLACEMENT_ERASER': {},
    'DISPLACEMENT_SMEAR': {
        'smear_deform_type',
    },
    'PAINT': {
        'color',
        'secondary_color',
        'blend',
        'flow',
        'wet_mix',
        'wet_persistence',
        'wet_paint_radius_factor',
        'density',
        'tip_roundness',
        'tip_scale_x',
        'use_flow_pressure',
        'invert_flow_pressure',
        'use_wet_mix_pressure',
        'invert_wet_mix_pressure',
        'use_wet_persistence_pressure',
        'invert_wet_persistence_pressure',
        'use_density_pressure',
        'invert_density_pressure',
        'color_type',
        'gradient_stroke_mode',
    },
    'SMEAR': {
        'smear_deform_type',
    }
}

all_specific_brush_properties: Set[str] = set()
for group_attr in specific_brush_properties.values():
    if group_attr:
        all_specific_brush_properties.update(group_attr)


brush_properties_minus_specific: Set[str] = set(BaseBrush._attributes).difference(all_specific_brush_properties).difference(exclude_properties)


brush_properties_per_sculpt_type: Dict[str, Tuple[str]] = {
    sculpt_tool: brush_properties_minus_specific.union(specific_brush_properties[sculpt_tool]) for sculpt_tool in sculpt_tool_items
}
