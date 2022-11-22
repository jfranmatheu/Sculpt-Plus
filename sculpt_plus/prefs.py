from bpy.types import AddonPreferences, Context
from bpy.props import StringProperty
from sculpt_plus.path import SculptPlusPaths
from bpy.types import AddonPreferences, Region
from bpy.props import FloatProperty, BoolProperty, EnumProperty, IntVectorProperty, IntProperty, FloatVectorProperty, StringProperty
from mathutils import Vector
import bpy

import os
from os.path import dirname, abspath, join

app_data_path = os.getenv('APPDATA')

SLOT_SIZE = 56

enum_list = [("NONE", "None", "")]


class SCULPTPLUS_AddonPreferences(AddonPreferences):
    bl_idname: str = __package__

    first_time: BoolProperty(default=False)

    brush_lib_path: StringProperty(
        name="Brush Library Directory",
        description="Folder where to save your brush sets",
        default=SculptPlusPaths.DATA_BRUSHES(),
        subtype='DIR_PATH'
    )
    num_backup_versions: IntProperty(
        name="Backup Versions",
        description="Number of Backup Versions to store",
        default=2,
        min=0, max=10
    )


    def get_scale(self, context) -> float:
        ui_scale = context.preferences.view.ui_scale
        return ui_scale * self.scale

    def update_ui(self, context):
        #from .controller import SculptHotbarGizmo
        #cv = SculptHotbarGizmo.get()
        if not hasattr(bpy, 'sculpt_hotbar'):
            return
        cv = bpy.sculpt_hotbar.get(context.region)
        if not cv:
            return
        scale = self.get_scale(context)
        #dimensions = Vector((context.region.width, context.region.height))
        cv.update(None, scale, self)

    data_path_local = StringProperty(
        default=join(dirname(abspath(__file__)), 'data'),
        subtype='DIR_PATH'
    )
    data_path = StringProperty(
        default=join(app_data_path, 'sculpt_hotbar') if app_data_path else join(dirname(abspath(__file__)), 'data'),
        subtype='DIR_PATH'
    )
    
    use_smooth_scroll : BoolProperty(default=True, name="Smooth Scroll", update=update_ui)

    padding : IntProperty(default=1, min=0, max=6, name="Hotbar Brush-Icon Padding", update=update_ui)
    margin_bottom : IntProperty(default=8, min=0, max=64, name="Hotbar Bottom Margin", update=update_ui)
    margin_left : IntProperty(default=8, min=0, max=64, name="Sidebar Left Margin", update=update_ui)
    scale : FloatProperty(default=1.0, min=0.8, max=2.0, name="Scale", update=update_ui)

    theme_hotbar : FloatVectorProperty(size=4, default=(.007,.007,.007,.95), min=0.0, max=1.0, name="Background Color", subtype='COLOR')
    #theme_hotbar_outline : FloatVectorProperty(size=4, default=(.09,.09,.09,.9), min=0.0, max=1.0, name="Outline Color", subtype='COLOR')
    theme_hotbar_slot : FloatVectorProperty(size=4, default=(.09,.09,.09,.85), min=0.0, max=1.0, name="Slot Background Color", subtype='COLOR')

    theme_shelf : FloatVectorProperty(size=4, default=(.1, .1, .1, .9), min=0.0, max=1.0, name="Background Color", subtype='COLOR')
    theme_shelf_slot : FloatVectorProperty(size=4, default=(.16, .16, .16, .5), min=0.0, max=1.0, name="Slot Background Color", subtype='COLOR')

    theme_sidebar : FloatVectorProperty(size=4, default=(.1,.1,.1,.9), min=0.0, max=1.0, name="Background Color", subtype='COLOR')
    theme_sidebar_slot : FloatVectorProperty(size=4, default=(.16,.16,.16,.5), min=0.0, max=1.0, name="Slot Background Color", subtype='COLOR')

    theme_active_slot_color : FloatVectorProperty(size=4, default=(.2, .5, .9, 1.0), min=0.0, max=1.0, name="Active/Selected Slot Color", subtype='COLOR')
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


    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        if self.first_time:

            return

        def section(title: str, icon: str = 'NONE', *props):
            section = layout.column(align=True)
            section.box().row(align=True).label(text=title, icon=icon)
            content = section.box().column(align=True)
            for prop in props:
                content.prop(self, prop)
            return content

        col = layout.column(align=True)
        col.prop(self, 'scale', slider=True)
        col.prop(self, 'use_smooth_scroll')
        col.separator()

        layout.separator()
        
        hotbar_styles = ('theme_hotbar', 'theme_hotbar_slot')
        hotbar = section("Hotbar Style", 'STATUSBAR', *hotbar_styles)
        hotbar.separator()
        hotbar.prop(self, 'margin_bottom', slider=True)
        hotbar.prop(self, 'padding', slider=True)

        shelf_styles = ('theme_shelf', 'theme_shelf_slot')
        section("Brush-Shelf Style", 'DESKTOP', *shelf_styles)
        
        sidebar_styles = ('theme_sidebar', 'theme_sidebar_slot')
        section("Texture-Sidebar Style", 'MENU_PANEL', *sidebar_styles)


        #col.label(text="Slot size: "+str(int(self.scale*SLOT_SIZE))+'px')


def get_prefs(context: Context) -> SCULPTPLUS_AddonPreferences:
    return context.preferences.addons[__package__].preferences
