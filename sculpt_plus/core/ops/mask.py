from bpy import ops as OPS
from mathutils import Vector

from sculpt_plus.utils.operator import create_op_props_popup_wrapper, create_op_modal_exec_wrapper

from sculpt_plus.prefs import get_prefs


class SCULPTPLUS_OT_mask_slice_wrapper:
    bl_idname = 'sculpt_plus.mask_slice_wrapper'
    bl_label = "Mask Slice"
    # bl_options = {'REGISTER', 'UNDO'}

    def post_execute(self, context):
        if context.mode != 'SCULPT':
            OPS.object.mode_set(False, mode='SCULPT')

'''
class SCULPTPLUS_OT_expand_normal_wrapper:
    bl_idname = 'sculpt_plus.mask_expand_normal_wrapper'
    bl_label = "Mask Expand by Normals"

    options = {'DRAW_2D'} # , 'DRAW_3D', 'RAYCAST', 'EVAL_ACTIVE_OBJECT'}

    def post_modal(self, context, event):
        pass

    def pre_execute(self, context):
        if self.invert:
            OPS.paint.mask_flood_fill(False, mode='INVERT')

    def draw_2d(self, context):
        scale = get_prefs(context).get_scale(context)
        center = context.region.width / 2
        top = context.region.height - 64*scale
        DiText(Vector((center, top)), "Left-Click over mesh surface to start expanding a Mask by normals", 24, scale, pivot=(.5, 1), draw_rect_props={})


class SCULPTPLUS_OT_expand_wrapper:
    bl_idname = 'sculpt_plus.mask_expand_wrapper'
    bl_label = "Mask Expand by Topology"

    options = {'DRAW_2D'} # , 'DRAW_3D', 'RAYCAST', 'EVAL_ACTIVE_OBJECT'}

    def post_modal(self, context, event):
        pass

    def pre_execute(self, context):
        if self.invert:
            OPS.paint.mask_flood_fill(False, mode='INVERT')

    def draw_2d(self, context):
        scale = get_prefs(context).get_scale(context)
        center = context.region.width / 2
        top = context.region.height - 64*scale
        DiText(Vector((center, top)), "Left-Click over mesh surface to start expanding a Mask by topology", 24, scale, pivot=(.5, 0), draw_rect_props={})
'''


def register_post():
    create_op_props_popup_wrapper(
        OPS.mesh.paint_mask_slice,
        SCULPTPLUS_OT_mask_slice_wrapper
    )

    '''
    create_op_modal_exec_wrapper(
        OPS.sculpt.expand,
        SCULPTPLUS_OT_expand_wrapper,
        props_overwrite={
            # 'target': 'MASK',
            # 'falloff_type': 'NORMALS',
            # 'use_normals': False,
            # 'keep_previous_mask': True,
            # 'invert': False,
            # 'create_face_set': False,
            # 'edge_sensitivity': 2000,
            #'smooth_iterations': 0,
        },
        copy_props=True
    )

    create_op_modal_exec_wrapper(
        OPS.sculpt.expand,
        SCULPTPLUS_OT_expand_normal_wrapper,
        props_overwrite={
            # 'target': 'MASK',
            # 'falloff_type': 'NORMALS',
            # 'use_normals': True,
            # 'keep_previous_mask': True,
            # 'invert': False,
            # 'create_face_set': False,
            # 'edge_sensitivity': 2000,
            # 'smooth_iterations': 0,
        },
        copy_props=True
    )
    '''
