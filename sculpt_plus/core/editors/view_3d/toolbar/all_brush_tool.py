# This example adds an object mode tool to the toolbar.
# This is just the circle-select and lasso tools tool.
import bpy
from bpy.types import WorkSpaceTool, Operator

from .override_tools import accept_brush_tools
from .override_region import toolbar_hidden_brush_tools
from sculpt_plus.props import Props, CM_UIContext, bm_data



class SCULPTPLUS_OT_all_brush_tool(Operator):
    bl_idname: str = 'sculpt_plus.all_brush_tool'
    bl_label: str = "All Brush Tool"
    bl_description: str = "All for One. One for All."


    def execute(self, context):
        # INVALID MODE!
        if context.mode != 'SCULPT':
            return {'CANCELLED'}

        if context.space_data is None:
            return {'CANCELLED'}

        # INVALID WORKSPACE!
        workspace = Props.Workspace(context)
        if workspace is None or context.workspace != workspace:
            return {'CANCELLED'}

        ## print("Holiwiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii toooooolll")

        stored_tool_id = Props.SculptTool.get_stored()

        # TOOL IS NONE! IDK WHY...
        if stored_tool_id == 'NONE':
            # IDK RICK.
            return {'CANCELLED'}

        # BRUSH TOOL BUT OF SPECIAL TYPE.
        if stored_tool_id in accept_brush_tools:
            bpy.ops.wm.tool_set_by_id(name='builtin_brush.' + stored_tool_id.replace('_', ' ').title())
            return {'FINISHED'}

        if stored_tool_id not in toolbar_hidden_brush_tools:
            return {'FINISHED'}

        ## print("Sculpt Brush! All for One, One for All!")
        bpy.ops.wm.tool_set_by_id(name='builtin_brush.Draw')

        with CM_UIContext(context, mode='SCULPT', item_type='BRUSH'):
            if active_br := bm_data.active_brush:
                active_br.set_active(context)
            elif active_cat := bm_data.active_category:
                if active_cat.items.count > 0:
                    active_cat.items[0].set_active(context)

        Props.SculptTool.update_stored(context)

        return {'FINISHED'}
