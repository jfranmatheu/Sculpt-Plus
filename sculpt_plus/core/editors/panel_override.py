import bpy
from bpy.utils import register_class, unregister_class
from bpy.types import (
    VIEW3D_PT_tools_brush_select,
    VIEW3D_PT_tools_active,
    VIEW3D_PT_tools_brush_settings, VIEW3D_PT_tools_brush_settings_advanced,
    VIEW3D_PT_tools_brush_falloff, VIEW3D_PT_tools_brush_stroke,
    VIEW3D_PT_tools_brush_texture,
)
from bl_ui.properties_paint_common import UnifiedPaintPanel, BrushSelectPanel, BrushPanel
# To change category.
from bpy.types import (
    VIEW3D_PT_sculpt_dyntopo,
    VIEW3D_PT_sculpt_voxel_remesh,
    VIEW3D_PT_sculpt_symmetry,
    VIEW3D_PT_sculpt_options_gravity,
    VIEW3D_PT_sculpt_options
)

from .backup_cache import get_attr_from_cache

classes_to_override__poll = (
    #BrushPanel,
    #BrushSelectPanel,
    #VIEW3D_PT_tools_active,
    VIEW3D_PT_tools_brush_select,
    VIEW3D_PT_tools_brush_settings, #VIEW3D_PT_tools_brush_settings_advanced,
    #VIEW3D_PT_tools_brush_falloff, VIEW3D_PT_tools_brush_stroke,
    #VIEW3D_PT_tools_brush_texture
)

classes_to_override__draw = ()

panels_to_override__category = (
    #VIEW3D_PT_sculpt_dyntopo,
    #VIEW3D_PT_sculpt_voxel_remesh,
    #VIEW3D_PT_sculpt_symmetry,
    #VIEW3D_PT_sculpt_options_gravity,
    #VIEW3D_PT_sculpt_options
)

# register_original_classes, unregister_original_classes = bpy.utils.register_classes_factory(classes_to_override)

@classmethod
def poll(cls, context):
    if context.mode == 'SCULPT':
        return False
    return cls._ori_poll(context)

@classmethod
def poll_default(cls, context):
    return True


def draw(self, context):
    if context.mode == 'SCULPT':
        return False
    return self.__class__._ori_draw(context)

def draw_default(self, context):
    pass


def register():
    for cls in classes_to_override__poll:
        cls._ori_poll = get_attr_from_cache(cls, 'poll', poll_default)
        cls.poll = poll
    
    for cls in classes_to_override__draw:
        cls._ori_draw = get_attr_from_cache(cls, 'draw', draw_default)
        cls.draw = draw

    for cls in panels_to_override__category:
        unregister_class(cls)
        cls.bl_category = 'Sculpt'
        register_class(cls)

def unregister():
    pass
