""" File generated automatically by ackit (Addon Creator Kit). """
import numpy
import typing
from typing import List, Set, Tuple, Dict, Any

import bpy
import bpy_types
import bl_ext
from bpy.types import WindowManager, Context


""" Addon-Defined PropertyGroup: """
class sculpt_plus_ui_panel_toggles:
	# Root PG, attached to bpy.types.WindowManager
	name: str

	@classmethod
	def get_data(cls, context: Context) -> 'sculpt_plus_ui_panel_toggles':
		bpy_type_data: ExtendedWindowManager = context.window_manager
		if hasattr(bpy_type_data, "sculpt_plus_ui_panels"): 
				return bpy_type_data.sculpt_plus_ui_panels



# ++++++++++++++++++++++++++++++++++++++++++++++++++
""" Extended bpy.types classes by the addon: """

class ExtendedWindowManager(WindowManager):
	sculpt_plus_ui_panels: sculpt_plus_ui_panel_toggles

class ExtendedTypes:
	WindowManager = ExtendedWindowManager

# ++++++++++++++++++++++++++++++++++++++++++++++++++
""" Root PropertyGroups (linked directly to any bpy.types): """
class RootPG:
	@staticmethod
	def Preferences(context: bpy.types.Context) -> SCULPTPLUS_AddonPreferences:
		return context.preferences.addons['bl_ext.user_default.sculpt_plus'].preferences

	WM = sculpt_plus_ui_panel_toggles.get_data

# Alias:
splus_types = RootPG

# ++++++++++++++++++++++++++++++++++++++++++++++++++
