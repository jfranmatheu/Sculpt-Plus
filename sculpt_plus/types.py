""" File generated automatically by ackit (Addon Creator Kit). """
import numpy
import typing
from typing import List, Set, Tuple, Dict, Any

import bpy
import bpy_types
import bl_ext
from bpy.types import Context, Scene, WindowManager


""" Addon-Defined PropertyGroup: """
class SCULPTPLUS_AddonPreferences:
	bl_idname: str
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


class SCULPTPLUS_PG_scn:
	# Root PG, attached to bpy.types.Scene
	name: str

	@classmethod
	def get_data(cls, context: Context) -> 'SCULPTPLUS_PG_scn':
		bpy_type_data: ExtendedScene = context.scene
		if hasattr(bpy_type_data, "sculpt_plus"): 
				return bpy_type_data.sculpt_plus


class _SCULPTPLUS_PG_ui_toggles:
	name: str

class SCULPTPLUS_PG_wm:
	# Root PG, attached to bpy.types.WindowManager
	name: str

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

class ExtendedTypes:
	Scene = ExtendedScene
	WindowManager = ExtendedWindowManager

# ++++++++++++++++++++++++++++++++++++++++++++++++++
""" Root PropertyGroups (linked directly to any bpy.types): """
class RootPG:
	@staticmethod
	def Preferences(context: bpy.types.Context) -> SCULPTPLUS_AddonPreferences:
		return context.preferences.addons['bl_ext.user_default.sculpt_plus'].preferences

	SCN = SCULPTPLUS_PG_scn.get_data
	WM = SCULPTPLUS_PG_wm.get_data

# Alias:
splus_types = RootPG

# ++++++++++++++++++++++++++++++++++++++++++++++++++
