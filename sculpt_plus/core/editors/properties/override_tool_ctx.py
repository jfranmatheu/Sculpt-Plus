from bl_ui.properties_paint_common import BrushSelectPanel, BrushPanel, UnifiedPaintPanel

'''
from ..backup_cache import get_attr_from_cache

@classmethod
def poll__BrushPanel(cls, context) -> bool:
    # Override in Sculpt Mode.
    print("holeaa")
    if context.mode == 'SCULPT':
        # if context.space_data.type not in {'TOOLS'}:
        return False
    return get_attr_from_cache(BrushPanel, 'poll')(context)


def register():
    BrushPanel.poll = poll__BrushPanel
    print(BrushPanel.poll)

    from bpy.types import VIEW3D_PT_tools_active
    VIEW3D_PT_tools_active.poll = lambda cls, context: context.mode != 'SCULPT'

def unregister():
    pass
'''