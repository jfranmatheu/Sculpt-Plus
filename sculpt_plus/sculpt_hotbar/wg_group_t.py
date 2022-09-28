from typing import Any, Dict, Tuple

from bpy import ops as OPS

from .icons import Icon
from .wg_group_but import ButtonGroup, MultiButtonGroup



class TransformGroup(ButtonGroup):
    fill_by: str = 'COLS'
    rows: int = 2 # 2 # 1
    align: str = 'LEFT'
    align_dir: str = 'RIGHT' # 'RIGHT' # 'LEFT'
    relative_to_bar_pos = (1, 0) # (1, 0) # (1, 1)
    items: Tuple[Dict[str, Any]] = (
        { # MOVE.
            'label': "Transform Move",
            'func': OPS.wm.tool_set_by_id,
            'args': (),
            'kwargs': {
                'name': "builtin.move",
            },
            'icon': Icon.TRANSFORM_TRANSLATE,
            'icon_scale': 1.1,
            'toggle': lambda ctx: ctx.workspace.tools.from_space_view3d_mode(ctx.mode, create=False).idname == "builtin.move"
        },
        { # SCALE.
            'label': "Transform Scale",
            'func': OPS.wm.tool_set_by_id,
            'args': (),
            'kwargs': {
                'name': "builtin.scale",
            },
            'icon': Icon.TRANSFORM_SCALE,
            #'icon_color': (.9, .9, .9, .9)
            'icon_scale': 1.1,
            'toggle': lambda ctx: ctx.workspace.tools.from_space_view3d_mode(ctx.mode, create=False).idname == "builtin.scale"
        },
        { # ROTATE.
            'label': "Transform Rotate",
            'func': OPS.wm.tool_set_by_id,
            'args': (),
            'kwargs': {
                'name': "builtin.rotate",
            },
            'icon': Icon.TRANSFORM_ROTATE,
            'icon_scale': 1.1,
            'toggle': lambda ctx: ctx.workspace.tools.from_space_view3d_mode(ctx.mode, create=False).idname == "builtin.rotate"
        },
        { # TRANSFORM.
            'label': "Transform Move/Rotate/Scale",
            'func': OPS.wm.tool_set_by_id,
            'args': (),
            'kwargs': {
                'name': "builtin.transform",
            },
            'icon': Icon.TRANSFORM_MULTI,
            #'icon_color': (.9, .9, .9, .9)
            'icon_scale': 1.1,
            'toggle': lambda ctx: ctx.workspace.tools.from_space_view3d_mode(ctx.mode, create=False).idname == "builtin.transform"
        },
    )
