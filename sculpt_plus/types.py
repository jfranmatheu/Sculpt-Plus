""" File generated automatically by ackit (Addon Creator Kit). """
import numpy
import typing
from typing import List, Set, Tuple, Dict, Any

import bpy
import bpy_types
import bl_ext
from bpy.types import WindowManager, Scene, Context


""" Addon-Defined PropertyGroup: """
class sculpt_plus_ui_panel_toggles:
	# Root PG, attached to bpy.types.WindowManager
	name: str

	@classmethod
	def get_data(cls, context: Context) -> 'sculpt_plus_ui_panel_toggles':
		bpy_type_data: ExtendedWindowManager = context.window_manager
		if hasattr(bpy_type_data, "sculpt_plus_ui_panels"): 
				return bpy_type_data.sculpt_plus_ui_panels


class SCULPTPLUS_PG_scn:
	# Root PG, attached to bpy.types.Scene
	name: str
	texture: bpy.types.ImageTexture
	image: bpy.types.Image
	image_seq: bpy.types.Image
	mask_op_use_front_faces_only: bool
	mask_op_clear_previous_mask: bool
	mask_op_invert: bool
	mask_op_use_reposition_pivot: bool
	facesets_op_use_front_faces_only: bool

	@classmethod
	def get_data(cls, context: Context) -> 'SCULPTPLUS_PG_scn':
		bpy_type_data: ExtendedScene = context.scene
		if hasattr(bpy_type_data, "sculpt_plus"): 
				return bpy_type_data.sculpt_plus


class SCULPTPLUS_AddonPreferences:
	bl_idname: str
	first_time: bool
	brush_lib_path: str
	num_backup_versions: int
	use_smooth_scroll: bool
	show_hotbar_mask_group: bool
	show_hotbar_transform_group: bool
	padding: int
	margin_bottom: int
	margin_left: int
	scale: float
	sidebar_position: str
	theme_hotbar: tuple[float]
	theme_hotbar_slot: tuple[float]
	theme_shelf: tuple[float]
	theme_shelf_slot: tuple[float]
	theme_sidebar: tuple[float]
	theme_sidebar_slot: tuple[float]
	theme_selected_slot_color: tuple[float]
	theme_active_slot_color: tuple[float]
	theme_slot_outline_color: tuple[float]
	theme_slot_color: tuple[float]
	theme_text: tuple[float]
	set_list: str
	toolbar_position: str
	toolbar_panel_mask_layout: str
	def get_cv(self, context):
		pass

	def get_scale(self, context) -> float:
		pass

	def update_ui(self, context):
		pass

	def update_hotbar_mask_group(self, context):
		pass

	def update_hotbar_transform_group(self, context):
		pass

	def get_camera_list(self, context):
		pass

	def draw(self, context):
		pass


class _SCULPTPLUS_PG_ui_toggles:
	name: str
	show_brush_settings: bool
	show_brush_settings_advanced: bool
	show_brush_settings_stroke: bool
	show_brush_settings_falloff: bool
	show_brush_settings_texture: bool
	show_brush_settings_panel: bool
	show_mask_facesets_panel: bool
	show_sculpt_mesh_panel: bool
	show_facesets_panel_initialize_section: bool
	show_facesets_panel_createfrom_section: bool
	toolbar_brush_sections: str
	toolbar_maskfacesets_sections: str
	toolbar_sculpt_sections: str
	mask_panel_tabs: str
	color_toolbar_panel_tool: tuple[float]
	color_toolbar_panel_maskfacesets: tuple[float]
	color_toolbar_panel_sculptmesh: tuple[float]
	color_toolbar_panel_emboss_bottom: tuple[float]

class SCULPTPLUS_PG_wm:
	# Root PG, attached to bpy.types.WindowManager
	name: str
	ui: _SCULPTPLUS_PG_ui_toggles
	test_context: bool

	@classmethod
	def get_data(cls, context: Context) -> 'SCULPTPLUS_PG_wm':
		bpy_type_data: ExtendedWindowManager = context.window_manager
		if hasattr(bpy_type_data, "sculpt_plus"): 
				return bpy_type_data.sculpt_plus



# ++++++++++++++++++++++++++++++++++++++++++++++++++
""" Extended bpy.types classes by the addon: """

class ExtendedScene(Scene):
	sculpt_plus: SCULPTPLUS_PG_scn

class ExtendedWindowManager(WindowManager):
	sculpt_plus: SCULPTPLUS_PG_wm
	sculpt_plus_ui_panels: sculpt_plus_ui_panel_toggles

class ExtendedTypes:
	Scene = ExtendedScene
	WindowManager = ExtendedWindowManager

# ++++++++++++++++++++++++++++++++++++++++++++++++++
""" Root PropertyGroups (linked directly to any bpy.types): """
class RootPG:
	@staticmethod
	def Preferences(context: bpy.types.Context) -> SCULPTPLUS_AddonPreferences:
		return context.preferences.addons['bl_ext.user_default.sculpt_plus'].preferences

	WM = sculpt_plus_ui_panel_toggles.get_data
	SCN = SCULPTPLUS_PG_scn.get_data
	WM = SCULPTPLUS_PG_wm.get_data

# Alias:
splus_types = RootPG

# ++++++++++++++++++++++++++++++++++++++++++++++++++



# EXAMPLE ++++++++++++++++++++++++++++++++++++++++++++++++++
'''
from bl_ext.user_default.sculpt_plus.types import splus_types

# Your property_group variable will have the correct typing. :-)
splus_wm = splus_types.WM(context)
ui = property_group.ui
print(ui)
'''
