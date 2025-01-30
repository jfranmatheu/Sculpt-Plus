from bpy.types import AddonPreferences, Context
from bpy.props import StringProperty
from bpy.types import AddonPreferences, Region, UILayout
from bpy.props import FloatProperty, BoolProperty, EnumProperty, IntVectorProperty, IntProperty, FloatVectorProperty, StringProperty
from mathutils import Vector
import bpy

import os
from os.path import dirname, abspath, join

from .ackit import ACK, GLOBALS
from .path import SculptPlusPaths
# from sculpt_plus.ackit import better_prefs

app_data_path = os.getenv('APPDATA')

SLOT_SIZE = 56

enum_list = [("NONE", "None", "")]


# @better_prefs.new_panel(tab='TOOLBAR', label='Main', order=0, hide_header=True)
# def draw__toolbar__settings(panel, layout: UILayout, prefs: 'SCULPTPLUS_AddonPreferences') -> None:
#     box = layout.box()
#     box.row().prop(prefs, 'toolbar_position', expand=True)
#     box.prop(prefs, 'toolbar_panel_mask_layout')
# 
# @better_prefs.new_panel(tab='HOTBAR', label='Main', order=0, hide_header=True)
# def draw__hotbar__settings(panel, layout: UILayout, prefs: 'SCULPTPLUS_AddonPreferences') -> None:
#     box = layout.box()
#     box.prop(prefs, 'scale', slider=True)
#     box.prop(prefs, 'use_smooth_scroll')
# 
# @better_prefs.new_panel(tab='HOTBAR', label='Style', order=1)
# def draw__hotbar__style(panel, layout: UILayout, prefs: 'SCULPTPLUS_AddonPreferences') -> None:
#     layout.prop(prefs, 'margin_bottom', text="Bottom Margin", slider=True)
#     layout.prop(prefs, 'padding', text="Brush Icon Padding", slider=True)
# 
# @better_prefs.new_panel(tab='HOTBAR', label='Button Groups', order=2)
# def draw__hotbar__button_groups(panel, layout: UILayout, prefs: 'SCULPTPLUS_AddonPreferences') -> None:
#     layout.prop(prefs, 'show_hotbar_mask_group', text="Mask Group")
#     layout.prop(prefs, 'show_hotbar_transform_group', text="Transform Group")



class SCULPTPLUS_AddonPreferences(ACK.Type.PREFS):
    bl_idname: str = __package__

    # better_tabs: EnumProperty(
    #     name="Sections",
    #     items=(
    #         ('TOOLBAR', '3D-View Toolbar Settings', ""),
    #         ('HOTBAR', "Sculpt Hotbar", ""),
    #         ('THEMES', "Themes", "")
    #     )
    # )

    first_time: BoolProperty(default=False)

    brush_lib_path: StringProperty(
        name="Brush Library Directory",
        description="Folder where to save your brush sets",
        default=SculptPlusPaths.APP__DATA(),
        subtype='DIR_PATH'
    )
    num_backup_versions: IntProperty(
        name="Backup Versions",
        description="Number of Backup Versions to store",
        default=2,
        min=0, max=10
    )

    def get_cv(self, context):
        if not hasattr(bpy, 'sculpt_hotbar'):
            return None
        if bpy.sculpt_hotbar is None:
            return None
        from .sculpt_hotbar.canvas import Canvas
        cv: Canvas = bpy.sculpt_hotbar.get_cv(context.region)
        if cv is None:
            return None
        return cv

    def get_scale(self, context) -> float:
        ui_scale = context.preferences.system.ui_scale # context.preferences.view.ui_scale
        return ui_scale * self.scale

    def update_ui(self, context):
        if cv := self.get_cv(context):
            scale = self.get_scale(context)
            cv.update(None, None, scale, self)

    def update_hotbar_mask_group(self, context):
        if cv := self.get_cv(context):
            cv.group_mask.enabled = self.show_hotbar_mask_group

    def update_hotbar_transform_group(self, context):
        if cv := self.get_cv(context):
            cv.group_t.enabled = self.show_hotbar_transform_group

    data_path_local = StringProperty(
        default=join(dirname(abspath(__file__)), 'data'),
        subtype='DIR_PATH'
    )
    data_path = StringProperty(
        default=join(app_data_path, 'sculpt_hotbar') if app_data_path else join(dirname(abspath(__file__)), 'data'),
        subtype='DIR_PATH'
    )

    use_smooth_scroll : BoolProperty(default=True, name="Smooth Scroll", update=update_ui)

    show_hotbar_mask_group : BoolProperty(default=False, name="Show Hotbar Mask Buttons", update=update_hotbar_mask_group)
    show_hotbar_transform_group : BoolProperty(default=False, name="Show Hotbar Transform Buttons", update=update_hotbar_transform_group)

    padding : IntProperty(default=1, min=0, max=6, name="Hotbar Brush-Icon Padding", update=update_ui)
    margin_bottom : IntProperty(default=8, min=0, max=64, name="Hotbar Bottom Margin", update=update_ui)
    margin_left : IntProperty(default=8, min=0, max=64, name="Sidebar Left Margin", update=update_ui)
    scale : FloatProperty(default=1.0, min=0.8, max=2.0, name="Scale", update=update_ui)

    # Sidebar props.
    sidebar_position: EnumProperty(
        name="Sidebar Position",
        items=(
            ('AUTO', "Automatic", "Based on the toolbar alignment, will be positioned in the other side of the viewport"),
            ('LEFT', 'Left', ''),
            ('RIGHT', 'Right', ''),
            ('TOP', 'Top', ''),
        ),
        default='AUTO'
    )

    theme_hotbar : FloatVectorProperty(size=4, default=(.007,.007,.007,.95), min=0.0, max=1.0, name="Background Color", subtype='COLOR')
    #theme_hotbar_outline : FloatVectorProperty(size=4, default=(.09,.09,.09,.9), min=0.0, max=1.0, name="Outline Color", subtype='COLOR')
    theme_hotbar_slot : FloatVectorProperty(size=4, default=(.09,.09,.09,.85), min=0.0, max=1.0, name="Slot Background Color", subtype='COLOR')

    theme_shelf : FloatVectorProperty(size=4, default=(.1, .1, .1, .9), min=0.0, max=1.0, name="Background Color", subtype='COLOR')
    theme_shelf_slot : FloatVectorProperty(size=4, default=(.16, .16, .16, .5), min=0.0, max=1.0, name="Slot Background Color", subtype='COLOR')

    theme_sidebar : FloatVectorProperty(size=4, default=(.1,.1,.1,.9), min=0.0, max=1.0, name="Background Color", subtype='COLOR')
    theme_sidebar_slot : FloatVectorProperty(size=4, default=(.16,.16,.16,.5), min=0.0, max=1.0, name="Slot Background Color", subtype='COLOR')

    theme_selected_slot_color : FloatVectorProperty(size=4, default=(.9, .5, .4, 1.0), min=0.0, max=1.0, name="Selected Slot Color", subtype='COLOR')
    theme_active_slot_color : FloatVectorProperty(size=4, default=(.2, .5, .9, 1.0), min=0.0, max=1.0, name="Active Slot Color", subtype='COLOR')
    theme_slot_outline_color : FloatVectorProperty(size=4, default=(.1, .1, .1, .9), min=0.0, max=1.0, name="Active Slot Color", subtype='COLOR')
    theme_slot_color : FloatVectorProperty(size=4, default=(.1, .1, .1, .9), min=0.0, max=1.0, name="Active Slot Color", subtype='COLOR')

    theme_text : FloatVectorProperty(size=4, default=(.92,.92,.92,1), min=0.0, max=1.0, name="Text Color (0-9)", subtype='COLOR')

    def get_camera_list(self, context):
        enum_list.clear()
        for ob in context.scene.objects:
            if ob.type == 'CAMERA':
                enum_list.append((ob.name, ob.name, ""))
        if enum_list:
            return enum_list
        return [("NONE", "None", "")]

    set_list : EnumProperty(items=get_camera_list, name="Camera List")


    toolbar_position: EnumProperty(
        name="Toolbar Position",
        items=(
            ('LEFT', 'Left', "Left, while panels will be at its right"),
            ('RIGHT', 'Right', "Right, while panels will be at its left")
        ),
        default='LEFT'
    )

    toolbar_panel_mask_layout: EnumProperty(
        name="Mask Panel Layout",
        items=(
            ('COMPACT', "Compact", "A simple and compact display of the different mask operations, without subpanels/sections or tabs"),
            ('SECTIONS', "Sections", "A set of sections (box-like) for each kind of mask operation"),
            ('TABS', "Tabs", "Only the selected tab option is visible"),
        ),
        default='SECTIONS'
    )
    # collapse_mask_panel_sections: BoolProperty(default=False, name="Collapse Mask Panel Sections", description="Turns the box sections on the Mask Panel into a tab selector\n which collapses all except the selected one")


    def draw(self, context):
        layout: UILayout = self.layout
        layout.use_property_split = True

        if self.first_time:
            return

        def section(title: str, icon: str = 'NONE', align=True, _layout=None, props: tuple[str] = ()):
            _layout = _layout or layout
            section = _layout.column(align=True)
            section.box().row(align=True).label(text=title, icon=icon)
            content = section.box().column(align=align)
            for prop in props:
                content.prop(self, prop)
            return content

        toolbar_settings = section("3D Viewport Toolbar Settings", 'TOOL_SETTINGS', align=False)
        toolbar_settings.row().prop(self, 'toolbar_position', expand=True)
        toolbar_settings.prop(self, 'toolbar_panel_mask_layout')


        ''' SCULPT HOTBAR.... '''
        hotbar_prefs = section('Sculpt Hotbar Settings', 'STATUSBAR', align=False)
        _row_1 = hotbar_prefs.split(factor=0.4)

        general = section("General UI Settings", 'SETTINGS', align=False, _layout=_row_1)
        general.prop(self, 'scale', slider=True)
        general.prop(self, 'use_smooth_scroll')

        hotbar = section("Style", 'STATUSBAR', align=False, _layout=_row_1)
        hotbar.prop(self, 'margin_bottom', text="Bottom Margin", slider=True)
        hotbar.prop(self, 'padding', text="Brush Icon Padding", slider=True)

        hotbar_prefs.separator()
        _row_2 = hotbar_prefs.split()

        hotbar = section("Button Groups - Visibility", 'HIDE_OFF', align=False, _layout=_row_2)
        hotbar.prop(self, 'show_hotbar_mask_group', text="Mask Group")
        hotbar.prop(self, 'show_hotbar_transform_group', text="Transform Group")


        # hotbar_themes = section('Themes', 'COLOR', align=False)
        # _grid = hotbar_themes.grid_flow(row_major=True, align=False)
        # hotbar_styles = ('theme_hotbar', 'theme_hotbar_slot')
        # section("Hotbar Theme", 'STATUSBAR', align=True, _layout=_grid, props=hotbar_styles)
        # shelf_styles = ('theme_shelf', 'theme_shelf_slot')
        # section("Brush-Shelf Theme", 'DESKTOP', align=True, _layout=_grid, props=shelf_styles)

        #### sidebar_styles = ('theme_sidebar', 'theme_sidebar_slot')
        #### section("Texture-Sidebar Theme", 'MENU_PANEL', align=True, _layout=_grid, props=sidebar_styles)



        layout.separator(factor=2)

        layout.alert = True
        layout.operator('sculpt_plust.clear_data', text="Clear Sculpt+ Data")
        layout.alert = False



def get_prefs(context: Context) -> SCULPTPLUS_AddonPreferences | None:
    if addon := context.preferences.addons.get(GLOBALS.ADDON_MODULE, None):
        return addon.preferences
    return None
