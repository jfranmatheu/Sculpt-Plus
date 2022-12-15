import bpy

class BaseBrush:
	name: str
	blend: str
	sculpt_tool: str
	image_tool: str
	direction: str
	stroke_method: str
	sculpt_plane: str
	mask_tool: str
	curve_preset: str
	deform_target: str
	elastic_deform_type: str
	snake_hook_deform_type: str
	cloth_deform_type: str
	cloth_force_falloff_type: str
	cloth_simulation_area_type: str
	boundary_falloff_type: str
	smooth_deform_type: str
	smear_deform_type: str
	slide_deform_type: str
	boundary_deform_type: str
	pose_deform_type: str
	pose_origin_type: str
	jitter_unit: str
	falloff_shape: str
	size: int
	unprojected_radius: float
	jitter: float
	jitter_absolute: int
	spacing: int
	grad_spacing: int
	smooth_stroke_radius: int
	smooth_stroke_factor: float
	rate: float
	color: list
	secondary_color: list
	strength: float
	flow: float
	wet_mix: float
	wet_persistence: float
	density: float
	tip_scale_x: float
	use_hardness_pressure: bool
	invert_hardness_pressure: bool
	use_flow_pressure: bool
	invert_flow_pressure: bool
	use_wet_mix_pressure: bool
	invert_wet_mix_pressure: bool
	use_wet_persistence_pressure: bool
	invert_wet_persistence_pressure: bool
	use_density_pressure: bool
	invert_density_pressure: bool
	dash_ratio: float
	dash_samples: int
	plane_offset: float
	plane_trim: float
	height: float
	texture_sample_bias: float
	normal_weight: float
	elastic_deform_volume_preservation: float
	rake_factor: float
	crease_pinch_factor: float
	pose_offset: float
	disconnected_distance_max: float
	boundary_offset: float
	surface_smooth_shape_preservation: float
	surface_smooth_current_vertex: float
	surface_smooth_iterations: int
	multiplane_scrape_angle: float
	pose_smooth_iterations: int
	pose_ik_segments: int
	tip_roundness: float
	cloth_mass: float
	cloth_damping: float
	cloth_sim_limit: float
	cloth_sim_falloff: float
	cloth_constraint_softbody_strength: float
	hardness: float
	automasking_boundary_edges_propagation_steps: int
	auto_smooth_factor: float
	topology_rake_factor: float
	tilt_strength_factor: float
	normal_radius_factor: float
	area_radius_factor: float
	wet_paint_radius_factor: float
	stencil_pos: list
	stencil_dimension: list
	mask_stencil_pos: list
	mask_stencil_dimension: list
	sharp_threshold: float
	fill_threshold: float
	blur_kernel_radius: int
	blur_mode: str
	falloff_angle: float
	use_airbrush: bool
	use_original_normal: bool
	use_original_plane: bool
	use_automasking_topology: bool
	use_automasking_face_sets: bool
	use_automasking_boundary_edges: bool
	use_automasking_boundary_face_sets: bool
	use_scene_spacing: str
	use_grab_active_vertex: bool
	use_grab_silhouette: bool
	use_multiplane_scrape_dynamic: bool
	show_multiplane_scrape_planes_preview: bool
	use_pose_ik_anchored: bool
	use_pose_lock_rotation: bool
	use_connected_only: bool
	use_cloth_pin_simulation_boundary: bool
	use_cloth_collision: bool
	invert_to_scrape_fill: bool
	use_pressure_strength: bool
	use_offset_pressure: bool
	use_pressure_area_radius: bool
	use_pressure_size: bool
	use_pressure_jitter: bool
	use_pressure_spacing: bool
	use_pressure_masking: str
	use_inverse_smooth_pressure: bool
	use_plane_trim: bool
	use_frontface: bool
	use_frontface_falloff: bool
	use_anchor: bool
	use_space: bool
	use_line: bool
	use_curve: bool
	use_smooth_stroke: bool
	use_persistent: bool
	use_accumulate: bool
	use_space_attenuation: bool
	use_adaptive_space: bool
	use_locked_size: str
	color_type: str
	use_edge_to_edge: bool
	use_restore_mesh: bool
	use_alpha: bool
	gradient_stroke_mode: str
	gradient_fill_mode: str
	cursor_color_add: list
	cursor_color_subtract: list
	use_custom_icon: bool
	icon_filepath: str
	clone_alpha: float
	clone_offset: list

	_attributes = ("name", "blend", "sculpt_tool", "image_tool", "direction", "stroke_method", "sculpt_plane", "mask_tool", "curve_preset", "deform_target", "elastic_deform_type", "snake_hook_deform_type", "cloth_deform_type", "cloth_force_falloff_type", "cloth_simulation_area_type", "boundary_falloff_type", "smooth_deform_type", "smear_deform_type", "slide_deform_type", "boundary_deform_type", "pose_deform_type", "pose_origin_type", "jitter_unit", "falloff_shape", "size", "unprojected_radius", "jitter", "jitter_absolute", "spacing", "grad_spacing", "smooth_stroke_radius", "smooth_stroke_factor", "rate", "color", "secondary_color", "strength", "flow", "wet_mix", "wet_persistence", "density", "tip_scale_x", "use_hardness_pressure", "invert_hardness_pressure", "use_flow_pressure", "invert_flow_pressure", "use_wet_mix_pressure", "invert_wet_mix_pressure", "use_wet_persistence_pressure", "invert_wet_persistence_pressure", "use_density_pressure", "invert_density_pressure", "dash_ratio", "dash_samples", "plane_offset", "plane_trim", "height", "texture_sample_bias", "normal_weight", "elastic_deform_volume_preservation", "rake_factor", "crease_pinch_factor", "pose_offset", "disconnected_distance_max", "boundary_offset", "surface_smooth_shape_preservation", "surface_smooth_current_vertex", "surface_smooth_iterations", "multiplane_scrape_angle", "pose_smooth_iterations", "pose_ik_segments", "tip_roundness", "cloth_mass", "cloth_damping", "cloth_sim_limit", "cloth_sim_falloff", "cloth_constraint_softbody_strength", "hardness", "automasking_boundary_edges_propagation_steps", "auto_smooth_factor", "topology_rake_factor", "tilt_strength_factor", "normal_radius_factor", "area_radius_factor", "wet_paint_radius_factor", "stencil_pos", "stencil_dimension", "mask_stencil_pos", "mask_stencil_dimension", "sharp_threshold", "fill_threshold", "blur_kernel_radius", "blur_mode", "falloff_angle", "use_airbrush", "use_original_normal", "use_original_plane", "use_automasking_topology", "use_automasking_face_sets", "use_automasking_boundary_edges", "use_automasking_boundary_face_sets", "use_scene_spacing", "use_grab_active_vertex", "use_grab_silhouette", "use_multiplane_scrape_dynamic", "show_multiplane_scrape_planes_preview", "use_pose_ik_anchored", "use_pose_lock_rotation", "use_connected_only", "use_cloth_pin_simulation_boundary", "use_cloth_collision", "invert_to_scrape_fill", "use_pressure_strength", "use_offset_pressure", "use_pressure_area_radius", "use_pressure_size", "use_pressure_jitter", "use_pressure_spacing", "use_pressure_masking", "use_inverse_smooth_pressure", "use_plane_trim", "use_frontface", "use_frontface_falloff", "use_anchor", "use_space", "use_line", "use_curve", "use_smooth_stroke", "use_persistent", "use_accumulate", "use_space_attenuation", "use_adaptive_space", "use_locked_size", "color_type", "use_edge_to_edge", "use_restore_mesh", "use_alpha", "gradient_stroke_mode", "gradient_fill_mode", "cursor_color_add", "cursor_color_subtract", "use_custom_icon", "icon_filepath", "clone_alpha", "clone_offset")
	def __init__(self):
		self._name: str = "NONE"
		self._blend: str = "MIX"
		self._sculpt_tool: str = "DRAW"
		self._image_tool: str = "DRAW"
		self._direction: str = "ADD"
		self._stroke_method: str = "DOTS"
		self._sculpt_plane: str = "AREA"
		self._mask_tool: str = "DRAW"
		self._curve_preset: str = "CUSTOM"
		self._deform_target: str = "GEOMETRY"
		self._elastic_deform_type: str = "GRAB"
		self._snake_hook_deform_type: str = "FALLOFF"
		self._cloth_deform_type: str = "DRAG"
		self._cloth_force_falloff_type: str = "RADIAL"
		self._cloth_simulation_area_type: str = "LOCAL"
		self._boundary_falloff_type: str = "CONSTANT"
		self._smooth_deform_type: str = "LAPLACIAN"
		self._smear_deform_type: str = "DRAG"
		self._slide_deform_type: str = "DRAG"
		self._boundary_deform_type: str = "BEND"
		self._pose_deform_type: str = "ROTATE_TWIST"
		self._pose_origin_type: str = "TOPOLOGY"
		self._jitter_unit: str = "BRUSH"
		self._falloff_shape: str = "SPHERE"
		self._size: int = 35
		self._unprojected_radius: float = 0.0
		self._jitter: float = 0.0
		self._jitter_absolute: int = 0
		self._spacing: int = 10
		self._grad_spacing: int = 0
		self._smooth_stroke_radius: int = 75
		self._smooth_stroke_factor: float = 0.8999999761581421
		self._rate: float = 0.10000000149011612
		self._color: list = list((1.0, 1.0, 1.0))
		self._secondary_color: list = list((0.0, 0.0, 0.0))
		self._strength: float = 1.0
		self._flow: float = 0.0
		self._wet_mix: float = 0.0
		self._wet_persistence: float = 0.0
		self._density: float = 0.0
		self._tip_scale_x: float = 0.0
		self._use_hardness_pressure: bool = False
		self._invert_hardness_pressure: bool = False
		self._use_flow_pressure: bool = False
		self._invert_flow_pressure: bool = False
		self._use_wet_mix_pressure: bool = False
		self._invert_wet_mix_pressure: bool = False
		self._use_wet_persistence_pressure: bool = False
		self._invert_wet_persistence_pressure: bool = False
		self._use_density_pressure: bool = False
		self._invert_density_pressure: bool = False
		self._dash_ratio: float = 1.0
		self._dash_samples: int = 20
		self._plane_offset: float = 0.0
		self._plane_trim: float = 0.5
		self._height: float = 0.5
		self._texture_sample_bias: float = 0.0
		self._normal_weight: float = 0.0
		self._elastic_deform_volume_preservation: float = 0.0
		self._rake_factor: float = 0.0
		self._crease_pinch_factor: float = 0.5
		self._pose_offset: float = 0.0
		self._disconnected_distance_max: float = 0.10000000149011612
		self._boundary_offset: float = 0.0
		self._surface_smooth_shape_preservation: float = 0.0
		self._surface_smooth_current_vertex: float = 0.0
		self._surface_smooth_iterations: int = 0
		self._multiplane_scrape_angle: float = 0.0
		self._pose_smooth_iterations: int = 4
		self._pose_ik_segments: int = 1
		self._tip_roundness: float = 0.0
		self._cloth_mass: float = 1.0
		self._cloth_damping: float = 0.009999999776482582
		self._cloth_sim_limit: float = 2.5
		self._cloth_sim_falloff: float = 0.75
		self._cloth_constraint_softbody_strength: float = 0.0
		self._hardness: float = 0.0
		self._automasking_boundary_edges_propagation_steps: int = 1
		self._auto_smooth_factor: float = 0.0
		self._topology_rake_factor: float = 0.0
		self._tilt_strength_factor: float = 0.0
		self._normal_radius_factor: float = 0.5
		self._area_radius_factor: float = 0.5
		self._wet_paint_radius_factor: float = 0.5
		self._stencil_pos: list = list((256.0, 256.0))
		self._stencil_dimension: list = list((256.0, 256.0))
		self._mask_stencil_pos: list = list((0.0, 0.0))
		self._mask_stencil_dimension: list = list((0.0, 0.0))
		self._sharp_threshold: float = 0.0
		self._fill_threshold: float = 0.20000000298023224
		self._blur_kernel_radius: int = 2
		self._blur_mode: str = "GAUSSIAN"
		self._falloff_angle: float = 0.0
		self._use_airbrush: bool = False
		self._use_original_normal: bool = False
		self._use_original_plane: bool = False
		self._use_automasking_topology: bool = False
		self._use_automasking_face_sets: bool = False
		self._use_automasking_boundary_edges: bool = False
		self._use_automasking_boundary_face_sets: bool = False
		self._use_scene_spacing: str = "VIEW"
		self._use_grab_active_vertex: bool = False
		self._use_grab_silhouette: bool = False
		self._use_multiplane_scrape_dynamic: bool = False
		self._show_multiplane_scrape_planes_preview: bool = False
		self._use_pose_ik_anchored: bool = False
		self._use_pose_lock_rotation: bool = False
		self._use_connected_only: bool = False
		self._use_cloth_pin_simulation_boundary: bool = False
		self._use_cloth_collision: bool = False
		self._invert_to_scrape_fill: bool = False
		self._use_pressure_strength: bool = True
		self._use_offset_pressure: bool = False
		self._use_pressure_area_radius: bool = False
		self._use_pressure_size: bool = False
		self._use_pressure_jitter: bool = False
		self._use_pressure_spacing: bool = False
		self._use_pressure_masking: str = "NONE"
		self._use_inverse_smooth_pressure: bool = False
		self._use_plane_trim: bool = False
		self._use_frontface: bool = False
		self._use_frontface_falloff: bool = False
		self._use_anchor: bool = False
		self._use_space: bool = True
		self._use_line: bool = False
		self._use_curve: bool = False
		self._use_smooth_stroke: bool = False
		self._use_persistent: bool = False
		self._use_accumulate: bool = False
		self._use_space_attenuation: bool = True
		self._use_adaptive_space: bool = False
		self._use_locked_size: str = "VIEW"
		self._color_type: str = "COLOR"
		self._use_edge_to_edge: bool = False
		self._use_restore_mesh: bool = False
		self._use_alpha: bool = False
		self._gradient_stroke_mode: str = "PRESSURE"
		self._gradient_fill_mode: str = "LINEAR"
		self._cursor_color_add: list = list((1.0, 0.38999998569488525, 0.38999998569488525, 0.8999999761581421))
		self._cursor_color_subtract: list = list((0.38999998569488525, 0.38999998569488525, 1.0, 0.8999999761581421))
		self._use_custom_icon: bool = False
		self._icon_filepath: str = "NONE"
		self._clone_alpha: float = 0.5
		self._clone_offset: list = list((0.0, 0.0))


	@property
	def name(self) -> str:
		return self._name
	@name.setter
	def name(self, value: str) -> None:
		self._name: str = value
	@property
	def blend(self) -> str:
		return self._blend
	@blend.setter
	def blend(self, value: str) -> None:
		self._blend: str = value
	@property
	def sculpt_tool(self) -> str:
		return self._sculpt_tool
	@sculpt_tool.setter
	def sculpt_tool(self, value: str) -> None:
		self._sculpt_tool: str = value
	@property
	def image_tool(self) -> str:
		return self._image_tool
	@image_tool.setter
	def image_tool(self, value: str) -> None:
		self._image_tool: str = value
	@property
	def direction(self) -> str:
		return self._direction
	@direction.setter
	def direction(self, value: str) -> None:
		self._direction: str = value
	@property
	def stroke_method(self) -> str:
		return self._stroke_method
	@stroke_method.setter
	def stroke_method(self, value: str) -> None:
		self._stroke_method: str = value
	@property
	def sculpt_plane(self) -> str:
		return self._sculpt_plane
	@sculpt_plane.setter
	def sculpt_plane(self, value: str) -> None:
		self._sculpt_plane: str = value
	@property
	def mask_tool(self) -> str:
		return self._mask_tool
	@mask_tool.setter
	def mask_tool(self, value: str) -> None:
		self._mask_tool: str = value
	@property
	def curve_preset(self) -> str:
		return self._curve_preset
	@curve_preset.setter
	def curve_preset(self, value: str) -> None:
		self._curve_preset: str = value
	@property
	def deform_target(self) -> str:
		return self._deform_target
	@deform_target.setter
	def deform_target(self, value: str) -> None:
		self._deform_target: str = value
	@property
	def elastic_deform_type(self) -> str:
		return self._elastic_deform_type
	@elastic_deform_type.setter
	def elastic_deform_type(self, value: str) -> None:
		self._elastic_deform_type: str = value
	@property
	def snake_hook_deform_type(self) -> str:
		return self._snake_hook_deform_type
	@snake_hook_deform_type.setter
	def snake_hook_deform_type(self, value: str) -> None:
		self._snake_hook_deform_type: str = value
	@property
	def cloth_deform_type(self) -> str:
		return self._cloth_deform_type
	@cloth_deform_type.setter
	def cloth_deform_type(self, value: str) -> None:
		self._cloth_deform_type: str = value
	@property
	def cloth_force_falloff_type(self) -> str:
		return self._cloth_force_falloff_type
	@cloth_force_falloff_type.setter
	def cloth_force_falloff_type(self, value: str) -> None:
		self._cloth_force_falloff_type: str = value
	@property
	def cloth_simulation_area_type(self) -> str:
		return self._cloth_simulation_area_type
	@cloth_simulation_area_type.setter
	def cloth_simulation_area_type(self, value: str) -> None:
		self._cloth_simulation_area_type: str = value
	@property
	def boundary_falloff_type(self) -> str:
		return self._boundary_falloff_type
	@boundary_falloff_type.setter
	def boundary_falloff_type(self, value: str) -> None:
		self._boundary_falloff_type: str = value
	@property
	def smooth_deform_type(self) -> str:
		return self._smooth_deform_type
	@smooth_deform_type.setter
	def smooth_deform_type(self, value: str) -> None:
		self._smooth_deform_type: str = value
	@property
	def smear_deform_type(self) -> str:
		return self._smear_deform_type
	@smear_deform_type.setter
	def smear_deform_type(self, value: str) -> None:
		self._smear_deform_type: str = value
	@property
	def slide_deform_type(self) -> str:
		return self._slide_deform_type
	@slide_deform_type.setter
	def slide_deform_type(self, value: str) -> None:
		self._slide_deform_type: str = value
	@property
	def boundary_deform_type(self) -> str:
		return self._boundary_deform_type
	@boundary_deform_type.setter
	def boundary_deform_type(self, value: str) -> None:
		self._boundary_deform_type: str = value
	@property
	def pose_deform_type(self) -> str:
		return self._pose_deform_type
	@pose_deform_type.setter
	def pose_deform_type(self, value: str) -> None:
		self._pose_deform_type: str = value
	@property
	def pose_origin_type(self) -> str:
		return self._pose_origin_type
	@pose_origin_type.setter
	def pose_origin_type(self, value: str) -> None:
		self._pose_origin_type: str = value
	@property
	def jitter_unit(self) -> str:
		return self._jitter_unit
	@jitter_unit.setter
	def jitter_unit(self, value: str) -> None:
		self._jitter_unit: str = value
	@property
	def falloff_shape(self) -> str:
		return self._falloff_shape
	@falloff_shape.setter
	def falloff_shape(self, value: str) -> None:
		self._falloff_shape: str = value
	@property
	def size(self) -> int:
		return self._size
	@size.setter
	def size(self, value: int) -> None:
		self._size: int = value
	@property
	def unprojected_radius(self) -> float:
		return self._unprojected_radius
	@unprojected_radius.setter
	def unprojected_radius(self, value: float) -> None:
		self._unprojected_radius: float = value
	@property
	def jitter(self) -> float:
		return self._jitter
	@jitter.setter
	def jitter(self, value: float) -> None:
		self._jitter: float = value
	@property
	def jitter_absolute(self) -> int:
		return self._jitter_absolute
	@jitter_absolute.setter
	def jitter_absolute(self, value: int) -> None:
		self._jitter_absolute: int = value
	@property
	def spacing(self) -> int:
		return self._spacing
	@spacing.setter
	def spacing(self, value: int) -> None:
		self._spacing: int = value
	@property
	def grad_spacing(self) -> int:
		return self._grad_spacing
	@grad_spacing.setter
	def grad_spacing(self, value: int) -> None:
		self._grad_spacing: int = value
	@property
	def smooth_stroke_radius(self) -> int:
		return self._smooth_stroke_radius
	@smooth_stroke_radius.setter
	def smooth_stroke_radius(self, value: int) -> None:
		self._smooth_stroke_radius: int = value
	@property
	def smooth_stroke_factor(self) -> float:
		return self._smooth_stroke_factor
	@smooth_stroke_factor.setter
	def smooth_stroke_factor(self, value: float) -> None:
		self._smooth_stroke_factor: float = value
	@property
	def rate(self) -> float:
		return self._rate
	@rate.setter
	def rate(self, value: float) -> None:
		self._rate: float = value
	@property
	def color(self) -> list:
		return self._color
	@color.setter
	def color(self, value: list) -> None:
		self._color: list = value
	@property
	def secondary_color(self) -> list:
		return self._secondary_color
	@secondary_color.setter
	def secondary_color(self, value: list) -> None:
		self._secondary_color: list = value
	@property
	def strength(self) -> float:
		return self._strength
	@strength.setter
	def strength(self, value: float) -> None:
		self._strength: float = value
	@property
	def flow(self) -> float:
		return self._flow
	@flow.setter
	def flow(self, value: float) -> None:
		self._flow: float = value
	@property
	def wet_mix(self) -> float:
		return self._wet_mix
	@wet_mix.setter
	def wet_mix(self, value: float) -> None:
		self._wet_mix: float = value
	@property
	def wet_persistence(self) -> float:
		return self._wet_persistence
	@wet_persistence.setter
	def wet_persistence(self, value: float) -> None:
		self._wet_persistence: float = value
	@property
	def density(self) -> float:
		return self._density
	@density.setter
	def density(self, value: float) -> None:
		self._density: float = value
	@property
	def tip_scale_x(self) -> float:
		return self._tip_scale_x
	@tip_scale_x.setter
	def tip_scale_x(self, value: float) -> None:
		self._tip_scale_x: float = value
	@property
	def use_hardness_pressure(self) -> bool:
		return self._use_hardness_pressure
	@use_hardness_pressure.setter
	def use_hardness_pressure(self, value: bool) -> None:
		self._use_hardness_pressure: bool = value
	@property
	def invert_hardness_pressure(self) -> bool:
		return self._invert_hardness_pressure
	@invert_hardness_pressure.setter
	def invert_hardness_pressure(self, value: bool) -> None:
		self._invert_hardness_pressure: bool = value
	@property
	def use_flow_pressure(self) -> bool:
		return self._use_flow_pressure
	@use_flow_pressure.setter
	def use_flow_pressure(self, value: bool) -> None:
		self._use_flow_pressure: bool = value
	@property
	def invert_flow_pressure(self) -> bool:
		return self._invert_flow_pressure
	@invert_flow_pressure.setter
	def invert_flow_pressure(self, value: bool) -> None:
		self._invert_flow_pressure: bool = value
	@property
	def use_wet_mix_pressure(self) -> bool:
		return self._use_wet_mix_pressure
	@use_wet_mix_pressure.setter
	def use_wet_mix_pressure(self, value: bool) -> None:
		self._use_wet_mix_pressure: bool = value
	@property
	def invert_wet_mix_pressure(self) -> bool:
		return self._invert_wet_mix_pressure
	@invert_wet_mix_pressure.setter
	def invert_wet_mix_pressure(self, value: bool) -> None:
		self._invert_wet_mix_pressure: bool = value
	@property
	def use_wet_persistence_pressure(self) -> bool:
		return self._use_wet_persistence_pressure
	@use_wet_persistence_pressure.setter
	def use_wet_persistence_pressure(self, value: bool) -> None:
		self._use_wet_persistence_pressure: bool = value
	@property
	def invert_wet_persistence_pressure(self) -> bool:
		return self._invert_wet_persistence_pressure
	@invert_wet_persistence_pressure.setter
	def invert_wet_persistence_pressure(self, value: bool) -> None:
		self._invert_wet_persistence_pressure: bool = value
	@property
	def use_density_pressure(self) -> bool:
		return self._use_density_pressure
	@use_density_pressure.setter
	def use_density_pressure(self, value: bool) -> None:
		self._use_density_pressure: bool = value
	@property
	def invert_density_pressure(self) -> bool:
		return self._invert_density_pressure
	@invert_density_pressure.setter
	def invert_density_pressure(self, value: bool) -> None:
		self._invert_density_pressure: bool = value
	@property
	def dash_ratio(self) -> float:
		return self._dash_ratio
	@dash_ratio.setter
	def dash_ratio(self, value: float) -> None:
		self._dash_ratio: float = value
	@property
	def dash_samples(self) -> int:
		return self._dash_samples
	@dash_samples.setter
	def dash_samples(self, value: int) -> None:
		self._dash_samples: int = value
	@property
	def plane_offset(self) -> float:
		return self._plane_offset
	@plane_offset.setter
	def plane_offset(self, value: float) -> None:
		self._plane_offset: float = value
	@property
	def plane_trim(self) -> float:
		return self._plane_trim
	@plane_trim.setter
	def plane_trim(self, value: float) -> None:
		self._plane_trim: float = value
	@property
	def height(self) -> float:
		return self._height
	@height.setter
	def height(self, value: float) -> None:
		self._height: float = value
	@property
	def texture_sample_bias(self) -> float:
		return self._texture_sample_bias
	@texture_sample_bias.setter
	def texture_sample_bias(self, value: float) -> None:
		self._texture_sample_bias: float = value
	@property
	def normal_weight(self) -> float:
		return self._normal_weight
	@normal_weight.setter
	def normal_weight(self, value: float) -> None:
		self._normal_weight: float = value
	@property
	def elastic_deform_volume_preservation(self) -> float:
		return self._elastic_deform_volume_preservation
	@elastic_deform_volume_preservation.setter
	def elastic_deform_volume_preservation(self, value: float) -> None:
		self._elastic_deform_volume_preservation: float = value
	@property
	def rake_factor(self) -> float:
		return self._rake_factor
	@rake_factor.setter
	def rake_factor(self, value: float) -> None:
		self._rake_factor: float = value
	@property
	def crease_pinch_factor(self) -> float:
		return self._crease_pinch_factor
	@crease_pinch_factor.setter
	def crease_pinch_factor(self, value: float) -> None:
		self._crease_pinch_factor: float = value
	@property
	def pose_offset(self) -> float:
		return self._pose_offset
	@pose_offset.setter
	def pose_offset(self, value: float) -> None:
		self._pose_offset: float = value
	@property
	def disconnected_distance_max(self) -> float:
		return self._disconnected_distance_max
	@disconnected_distance_max.setter
	def disconnected_distance_max(self, value: float) -> None:
		self._disconnected_distance_max: float = value
	@property
	def boundary_offset(self) -> float:
		return self._boundary_offset
	@boundary_offset.setter
	def boundary_offset(self, value: float) -> None:
		self._boundary_offset: float = value
	@property
	def surface_smooth_shape_preservation(self) -> float:
		return self._surface_smooth_shape_preservation
	@surface_smooth_shape_preservation.setter
	def surface_smooth_shape_preservation(self, value: float) -> None:
		self._surface_smooth_shape_preservation: float = value
	@property
	def surface_smooth_current_vertex(self) -> float:
		return self._surface_smooth_current_vertex
	@surface_smooth_current_vertex.setter
	def surface_smooth_current_vertex(self, value: float) -> None:
		self._surface_smooth_current_vertex: float = value
	@property
	def surface_smooth_iterations(self) -> int:
		return self._surface_smooth_iterations
	@surface_smooth_iterations.setter
	def surface_smooth_iterations(self, value: int) -> None:
		self._surface_smooth_iterations: int = value
	@property
	def multiplane_scrape_angle(self) -> float:
		return self._multiplane_scrape_angle
	@multiplane_scrape_angle.setter
	def multiplane_scrape_angle(self, value: float) -> None:
		self._multiplane_scrape_angle: float = value
	@property
	def pose_smooth_iterations(self) -> int:
		return self._pose_smooth_iterations
	@pose_smooth_iterations.setter
	def pose_smooth_iterations(self, value: int) -> None:
		self._pose_smooth_iterations: int = value
	@property
	def pose_ik_segments(self) -> int:
		return self._pose_ik_segments
	@pose_ik_segments.setter
	def pose_ik_segments(self, value: int) -> None:
		self._pose_ik_segments: int = value
	@property
	def tip_roundness(self) -> float:
		return self._tip_roundness
	@tip_roundness.setter
	def tip_roundness(self, value: float) -> None:
		self._tip_roundness: float = value
	@property
	def cloth_mass(self) -> float:
		return self._cloth_mass
	@cloth_mass.setter
	def cloth_mass(self, value: float) -> None:
		self._cloth_mass: float = value
	@property
	def cloth_damping(self) -> float:
		return self._cloth_damping
	@cloth_damping.setter
	def cloth_damping(self, value: float) -> None:
		self._cloth_damping: float = value
	@property
	def cloth_sim_limit(self) -> float:
		return self._cloth_sim_limit
	@cloth_sim_limit.setter
	def cloth_sim_limit(self, value: float) -> None:
		self._cloth_sim_limit: float = value
	@property
	def cloth_sim_falloff(self) -> float:
		return self._cloth_sim_falloff
	@cloth_sim_falloff.setter
	def cloth_sim_falloff(self, value: float) -> None:
		self._cloth_sim_falloff: float = value
	@property
	def cloth_constraint_softbody_strength(self) -> float:
		return self._cloth_constraint_softbody_strength
	@cloth_constraint_softbody_strength.setter
	def cloth_constraint_softbody_strength(self, value: float) -> None:
		self._cloth_constraint_softbody_strength: float = value
	@property
	def hardness(self) -> float:
		return self._hardness
	@hardness.setter
	def hardness(self, value: float) -> None:
		self._hardness: float = value
	@property
	def automasking_boundary_edges_propagation_steps(self) -> int:
		return self._automasking_boundary_edges_propagation_steps
	@automasking_boundary_edges_propagation_steps.setter
	def automasking_boundary_edges_propagation_steps(self, value: int) -> None:
		self._automasking_boundary_edges_propagation_steps: int = value
	@property
	def auto_smooth_factor(self) -> float:
		return self._auto_smooth_factor
	@auto_smooth_factor.setter
	def auto_smooth_factor(self, value: float) -> None:
		self._auto_smooth_factor: float = value
	@property
	def topology_rake_factor(self) -> float:
		return self._topology_rake_factor
	@topology_rake_factor.setter
	def topology_rake_factor(self, value: float) -> None:
		self._topology_rake_factor: float = value
	@property
	def tilt_strength_factor(self) -> float:
		return self._tilt_strength_factor
	@tilt_strength_factor.setter
	def tilt_strength_factor(self, value: float) -> None:
		self._tilt_strength_factor: float = value
	@property
	def normal_radius_factor(self) -> float:
		return self._normal_radius_factor
	@normal_radius_factor.setter
	def normal_radius_factor(self, value: float) -> None:
		self._normal_radius_factor: float = value
	@property
	def area_radius_factor(self) -> float:
		return self._area_radius_factor
	@area_radius_factor.setter
	def area_radius_factor(self, value: float) -> None:
		self._area_radius_factor: float = value
	@property
	def wet_paint_radius_factor(self) -> float:
		return self._wet_paint_radius_factor
	@wet_paint_radius_factor.setter
	def wet_paint_radius_factor(self, value: float) -> None:
		self._wet_paint_radius_factor: float = value
	@property
	def stencil_pos(self) -> list:
		return self._stencil_pos
	@stencil_pos.setter
	def stencil_pos(self, value: list) -> None:
		self._stencil_pos: list = value
	@property
	def stencil_dimension(self) -> list:
		return self._stencil_dimension
	@stencil_dimension.setter
	def stencil_dimension(self, value: list) -> None:
		self._stencil_dimension: list = value
	@property
	def mask_stencil_pos(self) -> list:
		return self._mask_stencil_pos
	@mask_stencil_pos.setter
	def mask_stencil_pos(self, value: list) -> None:
		self._mask_stencil_pos: list = value
	@property
	def mask_stencil_dimension(self) -> list:
		return self._mask_stencil_dimension
	@mask_stencil_dimension.setter
	def mask_stencil_dimension(self, value: list) -> None:
		self._mask_stencil_dimension: list = value
	@property
	def sharp_threshold(self) -> float:
		return self._sharp_threshold
	@sharp_threshold.setter
	def sharp_threshold(self, value: float) -> None:
		self._sharp_threshold: float = value
	@property
	def fill_threshold(self) -> float:
		return self._fill_threshold
	@fill_threshold.setter
	def fill_threshold(self, value: float) -> None:
		self._fill_threshold: float = value
	@property
	def blur_kernel_radius(self) -> int:
		return self._blur_kernel_radius
	@blur_kernel_radius.setter
	def blur_kernel_radius(self, value: int) -> None:
		self._blur_kernel_radius: int = value
	@property
	def blur_mode(self) -> str:
		return self._blur_mode
	@blur_mode.setter
	def blur_mode(self, value: str) -> None:
		self._blur_mode: str = value
	@property
	def falloff_angle(self) -> float:
		return self._falloff_angle
	@falloff_angle.setter
	def falloff_angle(self, value: float) -> None:
		self._falloff_angle: float = value
	@property
	def use_airbrush(self) -> bool:
		return self._use_airbrush
	@use_airbrush.setter
	def use_airbrush(self, value: bool) -> None:
		self._use_airbrush: bool = value
	@property
	def use_original_normal(self) -> bool:
		return self._use_original_normal
	@use_original_normal.setter
	def use_original_normal(self, value: bool) -> None:
		self._use_original_normal: bool = value
	@property
	def use_original_plane(self) -> bool:
		return self._use_original_plane
	@use_original_plane.setter
	def use_original_plane(self, value: bool) -> None:
		self._use_original_plane: bool = value
	@property
	def use_automasking_topology(self) -> bool:
		return self._use_automasking_topology
	@use_automasking_topology.setter
	def use_automasking_topology(self, value: bool) -> None:
		self._use_automasking_topology: bool = value
	@property
	def use_automasking_face_sets(self) -> bool:
		return self._use_automasking_face_sets
	@use_automasking_face_sets.setter
	def use_automasking_face_sets(self, value: bool) -> None:
		self._use_automasking_face_sets: bool = value
	@property
	def use_automasking_boundary_edges(self) -> bool:
		return self._use_automasking_boundary_edges
	@use_automasking_boundary_edges.setter
	def use_automasking_boundary_edges(self, value: bool) -> None:
		self._use_automasking_boundary_edges: bool = value
	@property
	def use_automasking_boundary_face_sets(self) -> bool:
		return self._use_automasking_boundary_face_sets
	@use_automasking_boundary_face_sets.setter
	def use_automasking_boundary_face_sets(self, value: bool) -> None:
		self._use_automasking_boundary_face_sets: bool = value
	@property
	def use_scene_spacing(self) -> str:
		return self._use_scene_spacing
	@use_scene_spacing.setter
	def use_scene_spacing(self, value: str) -> None:
		self._use_scene_spacing: str = value
	@property
	def use_grab_active_vertex(self) -> bool:
		return self._use_grab_active_vertex
	@use_grab_active_vertex.setter
	def use_grab_active_vertex(self, value: bool) -> None:
		self._use_grab_active_vertex: bool = value
	@property
	def use_grab_silhouette(self) -> bool:
		return self._use_grab_silhouette
	@use_grab_silhouette.setter
	def use_grab_silhouette(self, value: bool) -> None:
		self._use_grab_silhouette: bool = value
	@property
	def use_multiplane_scrape_dynamic(self) -> bool:
		return self._use_multiplane_scrape_dynamic
	@use_multiplane_scrape_dynamic.setter
	def use_multiplane_scrape_dynamic(self, value: bool) -> None:
		self._use_multiplane_scrape_dynamic: bool = value
	@property
	def show_multiplane_scrape_planes_preview(self) -> bool:
		return self._show_multiplane_scrape_planes_preview
	@show_multiplane_scrape_planes_preview.setter
	def show_multiplane_scrape_planes_preview(self, value: bool) -> None:
		self._show_multiplane_scrape_planes_preview: bool = value
	@property
	def use_pose_ik_anchored(self) -> bool:
		return self._use_pose_ik_anchored
	@use_pose_ik_anchored.setter
	def use_pose_ik_anchored(self, value: bool) -> None:
		self._use_pose_ik_anchored: bool = value
	@property
	def use_pose_lock_rotation(self) -> bool:
		return self._use_pose_lock_rotation
	@use_pose_lock_rotation.setter
	def use_pose_lock_rotation(self, value: bool) -> None:
		self._use_pose_lock_rotation: bool = value
	@property
	def use_connected_only(self) -> bool:
		return self._use_connected_only
	@use_connected_only.setter
	def use_connected_only(self, value: bool) -> None:
		self._use_connected_only: bool = value
	@property
	def use_cloth_pin_simulation_boundary(self) -> bool:
		return self._use_cloth_pin_simulation_boundary
	@use_cloth_pin_simulation_boundary.setter
	def use_cloth_pin_simulation_boundary(self, value: bool) -> None:
		self._use_cloth_pin_simulation_boundary: bool = value
	@property
	def use_cloth_collision(self) -> bool:
		return self._use_cloth_collision
	@use_cloth_collision.setter
	def use_cloth_collision(self, value: bool) -> None:
		self._use_cloth_collision: bool = value
	@property
	def invert_to_scrape_fill(self) -> bool:
		return self._invert_to_scrape_fill
	@invert_to_scrape_fill.setter
	def invert_to_scrape_fill(self, value: bool) -> None:
		self._invert_to_scrape_fill: bool = value
	@property
	def use_pressure_strength(self) -> bool:
		return self._use_pressure_strength
	@use_pressure_strength.setter
	def use_pressure_strength(self, value: bool) -> None:
		self._use_pressure_strength: bool = value
	@property
	def use_offset_pressure(self) -> bool:
		return self._use_offset_pressure
	@use_offset_pressure.setter
	def use_offset_pressure(self, value: bool) -> None:
		self._use_offset_pressure: bool = value
	@property
	def use_pressure_area_radius(self) -> bool:
		return self._use_pressure_area_radius
	@use_pressure_area_radius.setter
	def use_pressure_area_radius(self, value: bool) -> None:
		self._use_pressure_area_radius: bool = value
	@property
	def use_pressure_size(self) -> bool:
		return self._use_pressure_size
	@use_pressure_size.setter
	def use_pressure_size(self, value: bool) -> None:
		self._use_pressure_size: bool = value
	@property
	def use_pressure_jitter(self) -> bool:
		return self._use_pressure_jitter
	@use_pressure_jitter.setter
	def use_pressure_jitter(self, value: bool) -> None:
		self._use_pressure_jitter: bool = value
	@property
	def use_pressure_spacing(self) -> bool:
		return self._use_pressure_spacing
	@use_pressure_spacing.setter
	def use_pressure_spacing(self, value: bool) -> None:
		self._use_pressure_spacing: bool = value
	@property
	def use_pressure_masking(self) -> str:
		return self._use_pressure_masking
	@use_pressure_masking.setter
	def use_pressure_masking(self, value: str) -> None:
		self._use_pressure_masking: str = value
	@property
	def use_inverse_smooth_pressure(self) -> bool:
		return self._use_inverse_smooth_pressure
	@use_inverse_smooth_pressure.setter
	def use_inverse_smooth_pressure(self, value: bool) -> None:
		self._use_inverse_smooth_pressure: bool = value
	@property
	def use_plane_trim(self) -> bool:
		return self._use_plane_trim
	@use_plane_trim.setter
	def use_plane_trim(self, value: bool) -> None:
		self._use_plane_trim: bool = value
	@property
	def use_frontface(self) -> bool:
		return self._use_frontface
	@use_frontface.setter
	def use_frontface(self, value: bool) -> None:
		self._use_frontface: bool = value
	@property
	def use_frontface_falloff(self) -> bool:
		return self._use_frontface_falloff
	@use_frontface_falloff.setter
	def use_frontface_falloff(self, value: bool) -> None:
		self._use_frontface_falloff: bool = value
	@property
	def use_anchor(self) -> bool:
		return self._use_anchor
	@use_anchor.setter
	def use_anchor(self, value: bool) -> None:
		self._use_anchor: bool = value
	@property
	def use_space(self) -> bool:
		return self._use_space
	@use_space.setter
	def use_space(self, value: bool) -> None:
		self._use_space: bool = value
	@property
	def use_line(self) -> bool:
		return self._use_line
	@use_line.setter
	def use_line(self, value: bool) -> None:
		self._use_line: bool = value
	@property
	def use_curve(self) -> bool:
		return self._use_curve
	@use_curve.setter
	def use_curve(self, value: bool) -> None:
		self._use_curve: bool = value
	@property
	def use_smooth_stroke(self) -> bool:
		return self._use_smooth_stroke
	@use_smooth_stroke.setter
	def use_smooth_stroke(self, value: bool) -> None:
		self._use_smooth_stroke: bool = value
	@property
	def use_persistent(self) -> bool:
		return self._use_persistent
	@use_persistent.setter
	def use_persistent(self, value: bool) -> None:
		self._use_persistent: bool = value
	@property
	def use_accumulate(self) -> bool:
		return self._use_accumulate
	@use_accumulate.setter
	def use_accumulate(self, value: bool) -> None:
		self._use_accumulate: bool = value
	@property
	def use_space_attenuation(self) -> bool:
		return self._use_space_attenuation
	@use_space_attenuation.setter
	def use_space_attenuation(self, value: bool) -> None:
		self._use_space_attenuation: bool = value
	@property
	def use_adaptive_space(self) -> bool:
		return self._use_adaptive_space
	@use_adaptive_space.setter
	def use_adaptive_space(self, value: bool) -> None:
		self._use_adaptive_space: bool = value
	@property
	def use_locked_size(self) -> str:
		return self._use_locked_size
	@use_locked_size.setter
	def use_locked_size(self, value: str) -> None:
		self._use_locked_size: str = value
	@property
	def color_type(self) -> str:
		return self._color_type
	@color_type.setter
	def color_type(self, value: str) -> None:
		self._color_type: str = value
	@property
	def use_edge_to_edge(self) -> bool:
		return self._use_edge_to_edge
	@use_edge_to_edge.setter
	def use_edge_to_edge(self, value: bool) -> None:
		self._use_edge_to_edge: bool = value
	@property
	def use_restore_mesh(self) -> bool:
		return self._use_restore_mesh
	@use_restore_mesh.setter
	def use_restore_mesh(self, value: bool) -> None:
		self._use_restore_mesh: bool = value
	@property
	def use_alpha(self) -> bool:
		return self._use_alpha
	@use_alpha.setter
	def use_alpha(self, value: bool) -> None:
		self._use_alpha: bool = value
	@property
	def gradient_stroke_mode(self) -> str:
		return self._gradient_stroke_mode
	@gradient_stroke_mode.setter
	def gradient_stroke_mode(self, value: str) -> None:
		self._gradient_stroke_mode: str = value
	@property
	def gradient_fill_mode(self) -> str:
		return self._gradient_fill_mode
	@gradient_fill_mode.setter
	def gradient_fill_mode(self, value: str) -> None:
		self._gradient_fill_mode: str = value
	@property
	def cursor_color_add(self) -> list:
		return self._cursor_color_add
	@cursor_color_add.setter
	def cursor_color_add(self, value: list) -> None:
		self._cursor_color_add: list = value
	@property
	def cursor_color_subtract(self) -> list:
		return self._cursor_color_subtract
	@cursor_color_subtract.setter
	def cursor_color_subtract(self, value: list) -> None:
		self._cursor_color_subtract: list = value
	@property
	def use_custom_icon(self) -> bool:
		return self._use_custom_icon
	@use_custom_icon.setter
	def use_custom_icon(self, value: bool) -> None:
		self._use_custom_icon: bool = value
	@property
	def icon_filepath(self) -> str:
		return self._icon_filepath
	@icon_filepath.setter
	def icon_filepath(self, value: str) -> None:
		self._icon_filepath: str = value
	@property
	def clone_alpha(self) -> float:
		return self._clone_alpha
	@clone_alpha.setter
	def clone_alpha(self, value: float) -> None:
		self._clone_alpha: float = value
	@property
	def clone_offset(self) -> list:
		return self._clone_offset
	@clone_offset.setter
	def clone_offset(self, value: list) -> None:
		self._clone_offset: list = value

'''
brush = BaseBrush()
print(brush.name)
brush.name = "Test"
print(brush.name)
'''