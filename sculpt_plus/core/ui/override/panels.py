from bpy.types import (
    VIEW3D_PT_tools_brush_select,
    VIEW3D_PT_tools_brush_settings
)

from .backup_cache import set_cls_attribute


classes_to_override__poll = (
    VIEW3D_PT_tools_brush_select,
    VIEW3D_PT_tools_brush_settings
)


@classmethod
def poll(cls, context):
    if context.mode == 'SCULPT' and ('sculpt_plus' in context.workspace):
        return False
    return context.object and context.mode == 'SCULPT' # cls._ori_poll(cls, context)


@classmethod
def poll_default(cls, context):
    return True


def register():
    for cls in classes_to_override__poll:
        set_cls_attribute(cls, 'poll', poll)
