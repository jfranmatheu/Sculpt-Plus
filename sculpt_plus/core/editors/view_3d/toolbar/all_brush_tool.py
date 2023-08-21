# This example adds an object mode tool to the toolbar.
# This is just the circle-select and lasso tools tool.
import bpy
from bpy.types import WorkSpaceTool, Operator


class SCULPTPLUS_OT_all_brush_tool(Operator):
    bl_idname: str = 'sculpt_plus.all_brush_tool'
    bl_label: str = "All Brush Tool"
    bl_description: str = ""


    def execute(self, context):
        # print("Holiwiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii toooooolll")
        from .override_tools import accept_brush_tools
        from sculpt_plus.props import Props, CM_UIContext, bm_data

        if context.space_data is None:
            return {'CANCELLED'}

        prev_active_tool = Props.SculptTool.get_stored()
        curr_active_tool, tool_type = Props.SculptTool.get_from_context(context)
        if curr_active_tool is None:
            print("[SCULPT+] WARN! Current active tool is NULL")
            return {'CANCELLED'}

        if prev_active_tool != curr_active_tool:
            print(f"Info! Changed tool from {prev_active_tool} to {curr_active_tool}.")
            is_hidden_brush_tool: bool = curr_active_tool not in accept_brush_tools and tool_type == 'builtin_brush'
            if is_hidden_brush_tool:
                Props.SculptTool.update_stored(context)
                return {'CANCELLED'}

            # if curr_active_tool == 'ALL_BRUSH':
            print("Sculpt Brush! All for One, One for All!")
            bpy.ops.wm.tool_set_by_id(name='builtin_brush.Draw')

            with CM_UIContext(context, mode='SCULPT', item_type='BRUSH'):
                if active_br := bm_data.active_brush:
                    active_br.set_active(context)
                elif active_cat := bm_data.active_category:
                    if active_cat.items.count > 0:
                        active_cat.items[0].set_active(context)
                #else:
                #    bpy.ops.wm.tool_set_by_id(name='builtin_brush.Draw')

            Props.SculptTool.update_stored(context)

        return {'FINISHED'}
