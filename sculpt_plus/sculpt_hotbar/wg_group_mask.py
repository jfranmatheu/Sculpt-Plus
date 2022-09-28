from typing import Any, Dict, Tuple

from bpy import ops as OPS

from .icons import BrushIcon, Icon
from .wg_group_but import ButtonGroup, MultiButtonGroup

'''
{ # MASK FILL.
            'func': OPS.paint.mask_flood_fill,
            'args': (),
            'kwargs': {
                'mode':   'VALUE',
                'value':  1
            },
            'icon': 'F'
        },
'''


def set_face_set_edit_mode(ctx, mode: str) -> None:
    tool = ctx.workspace.tools.from_space_view3d_mode("SCULPT", create=False)
    if tool:
        tool.operator_properties("sculpt.face_set_edit").mode = mode

def get_face_set_edit_mode(ctx) -> None:
    if ctx.workspace.tools.from_space_view3d_mode(ctx.mode, create=False).idname != "builtin.face_set_edit":
        return None
    tool = ctx.workspace.tools.from_space_view3d_mode("SCULPT", create=False)
    if tool:
        return tool.operator_properties("sculpt.face_set_edit").mode
    return None


class MaskGroup(ButtonGroup):
    fill_by: str = 'COLS'
    relative_to_bar_pos = (0, 1)
    items: Tuple[Dict[str, Any]] = (
        { # MASK CLEAR.
            'label': "Mask Clear",
            'func': OPS.paint.mask_flood_fill,
            'args': (),
            'kwargs': {
                'mode':   'VALUE',
                'value':  0
            },
            'icon': Icon.MASK_CLEAR
        },
        { # MASK INVERT.
            'label': "Mask Invert",
            'func': OPS.paint.mask_flood_fill,
            'args': (),
            'kwargs': {
                'mode':   'INVERT',
            },
            'icon': Icon.MASK_INVERT
        },
        { # MASK GROW.
            'label': "Mask Grow",
            'func': OPS.sculpt.mask_filter,
            'args': (),
            'kwargs': {
                'filter_type':   'GROW',
            },
            'icon': 'G'
        },
        { # MASK SHRINK.
            'label': "Mask Shrink",
            'func': OPS.sculpt.mask_filter,
            'args': (),
            'kwargs': {
                'filter_type':   'SHRINK',
            },
            'icon': 'K'
        },
        { # MASK SMOOTH.
            'label': "Mask Smooth",
            'func': OPS.sculpt.mask_filter,
            'args': (),
            'kwargs': {
                'filter_type':   'SMOOTH',
            },
            'icon': 'S'
        },
        { # MASK SHARPEN.
            'label': "Mask Sharpen",
            'func': OPS.sculpt.mask_filter,
            'args': (),
            'kwargs': {
                'filter_type':   'SHARPEN',
            },
            'icon': 'N'
        },
        { # MASK CONTRAST INC.
            'label': "Mask Contrast Increase",
            'func': OPS.sculpt.mask_filter,
            'args': (),
            'kwargs': {
                'filter_type':   'CONTRAST_INCREASE',
                'auto_iteration_count': False,
                'iterations': 2
            },
            'icon': 'CI'
        },
        { # MASK CONTRAST DEC.
            'label': "Mask Contrast Decrease",
            'func': OPS.sculpt.mask_filter,
            'args': (),
            'kwargs': {
                'filter_type':   'CONTRAST_DECREASE',
                'auto_iteration_count': False,
                'iterations': 2
            },
            'icon': 'CD'
        },
    )


class MaskMultiGroup(MultiButtonGroup):
    fill_by: str = 'COLS'
    rows: int = 2
    align: str = 'LEFT'
    align_dir: str = 'RIGHT'
    relative_to_bar_pos = (0, 0)
    group_items: Tuple[Tuple[Dict[str, Any]]] = (
        (
            { # MASK CLEAR.
                'label': "Mask Clear",
                'func': OPS.paint.mask_flood_fill,
                'args': (),
                'kwargs': {
                    'mode':   'VALUE',
                    'value':  0
                },
                'icon': Icon.MASK_CLEAR
            },
            { # MASK INVERT.
                'label': "Mask Invert",
                'func': OPS.paint.mask_flood_fill,
                'args': (),
                'kwargs': {
                    'mode':   'INVERT',
                },
                'icon': Icon.MASK_INVERT
            },
            { # MASK GROW.
                'label': "Mask Grow",
                'func': OPS.sculpt.mask_filter,
                'args': (),
                'kwargs': {
                    'filter_type':   'GROW',
                },
                'icon': Icon.MASK_GROW,
                #'icon_color': (.9, .9, .9, .9)
            },
            { # MASK SHRINK.
                'label': "Mask Shrink",
                'func': OPS.sculpt.mask_filter,
                'args': (),
                'kwargs': {
                    'filter_type':   'SHRINK',
                },
                'icon': Icon.MASK_SHRINK,
                #'icon_color': (.9, .9, .9, .9)
            },
            { # MASK SMOOTH.
                'label': "Mask Smooth",
                'func': OPS.sculpt.mask_filter,
                'args': (),
                'kwargs': {
                    'filter_type':   'SMOOTH',
                },
                'icon': Icon.MASK_SMOOTH
            },
            { # MASK SHARPEN.
                'label': "Mask Sharpen",
                'func': OPS.sculpt.mask_filter,
                'args': (),
                'kwargs': {
                    'filter_type':   'SHARPEN',
                },
                'icon': Icon.MASK_SHARP
            },

            #{ # MASK CONTRAST INC.
            #    'func': OPS.sculpt.mask_filter,
            #    'args': (),
            #    'kwargs': {
            #        'filter_type':   'CONTRAST_INCREASE',
            #        'auto_iteration_count': False,
            #        'iterations': 2
            #    },
            #    'icon': 'CI'
            #},
            #{ # MASK CONTRAST DEC.
            #    'func': OPS.sculpt.mask_filter,
            #    'args': (),
            #    'kwargs': {
            #        'filter_type':   'CONTRAST_DECREASE',
            #        'auto_iteration_count': False,
            #        'iterations': 2
            #    },
            #    'icon': 'CD'
            #},
        ),


        (
            { # FACE SET GROW.
                'label': "Face Set Grow (Tool)",
                'func': OPS.wm.tool_set_by_id,
                'args': (),
                'kwargs': {
                    'name': "builtin.face_set_edit",
                },
                'post_func_ctx': lambda ctx: set_face_set_edit_mode(ctx, 'GROW'),
                'icon': Icon.FACESET_GROW,
                #'icon_color': (.9, .9, .9, .9)
                'toggle': lambda ctx: get_face_set_edit_mode(ctx) == 'GROW'
            },
            { # FACE SET SHRINK.
                'label': "Face Set Shrink (Tool)",
                'func': OPS.wm.tool_set_by_id,
                'args': (),
                'kwargs': {
                    'name': "builtin.face_set_edit",
                },
                'post_func_ctx': lambda ctx: set_face_set_edit_mode(ctx, 'SHRINK'),
                'icon': Icon.FACESET_SHRINK,
                #'icon_color': (.9, .9, .9, .9)
                'toggle': lambda ctx: get_face_set_edit_mode(ctx) == 'SHRINK'
            },
        ),

        (
            { # MASK BRUSH.
                'label': "Mask Brush Tool",
                'func': OPS.wm.tool_set_by_id,
                'args': (),
                'kwargs': {
                    'name': "builtin_brush.Mask",
                },
                'icon': BrushIcon.MASK,
                'icon_scale': 1.05,
                'toggle': lambda ctx: ctx.workspace.tools.from_space_view3d_mode(ctx.mode, create=False).idname == "builtin_brush.Mask"
            },
            { # DRAW FACE SETS.
                'label': "Draw Face Sets Tool",
                'func': OPS.wm.tool_set_by_id,
                'args': (),
                'kwargs': {
                    'name': "builtin_brush.Draw Face Sets",
                },
                'icon': BrushIcon.DRAW_FACE_SETS,
                'icon_scale': 1.05,
                'toggle': lambda ctx: ctx.workspace.tools.from_space_view3d_mode(ctx.mode, create=False).idname == "builtin_brush.Draw Face Sets"
            },
        ),
    )
