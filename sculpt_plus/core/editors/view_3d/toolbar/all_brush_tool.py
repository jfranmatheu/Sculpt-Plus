# This example adds an object mode tool to the toolbar.
# This is just the circle-select and lasso tools tool.
import bpy
from bpy.types import WorkSpaceTool, Operator


class SCULPTPLUS_OT_all_brush_tool(Operator):
    bl_idname: str = 'sculpt_plus.all_brush_tool'
    bl_label: str = "All Brush Tool"
    bl_description: str = ""

    #def draw(self, context):
    #    self.layout.label(text="This action will remove everything!", icon='ERROR')
    #    self.layout.label(text="A R E  Y O U  S U R E  ?")

    def execute(self, context):
        # print("Holiwiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii toooooolll")
        from .override_tools import accept_brush_tools, ToolSelectPanelHelper
        from sculpt_plus.props import Props

        prev_active_tool = Props.BrushManager().active_sculpt_tool
        curr_active_tool = ToolSelectPanelHelper.tool_active_from_context(context)
        if curr_active_tool is None:
            return {'CANCELLED'}
        type, curr_active_tool = curr_active_tool.idname.split('.')
        curr_active_tool = curr_active_tool.replace(' ', '_').upper()
        if prev_active_tool != curr_active_tool:
            print(f"Info! Changed tool from {prev_active_tool} to {curr_active_tool}.")
            is_hidden_brush_tool: bool = curr_active_tool not in accept_brush_tools and type == 'builtin_brush'
            if is_hidden_brush_tool:
                Props.BrushManager().active_sculpt_tool = curr_active_tool
                return {'CANCELLED'}

            # if curr_active_tool == 'ALL_BRUSH':
            print("Sculpt Brush! All for One, One for All!")
            if active_br := Props.GetActiveBrush():
                Props.SelectBrush(context, active_br)
            elif brushes := list(Props.BrushManager().brushes.values()):
                Props.SelectBrush(context, brushes[0])
            else:
                bpy.ops.wm.tool_set_by_id(name='builtin_brush.Draw')

            curr_active_tool = ToolSelectPanelHelper.tool_active_from_context(context)
            curr_active_tool = curr_active_tool.idname.split('.')[1].replace(' ', '_').upper()
            Props.BrushManager().active_sculpt_tool = curr_active_tool

        return {'FINISHED'}

'''
class MyTool(WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'SCULPT'

    # The prefix of the idname should be your add-on name.
    bl_idname = "builtin_brush.all_brush"
    bl_label = "All Brush"
    bl_description = (
        "Unified Brush Tool\n"
        "Bye Bye to a lot of messy brushes here!"
    )
    bl_icon = "brush.gpencil_draw.draw"
    bl_widget = None
    bl_keymap = (
        ("sculpt_plus.all_brush_tool", {"type": 'MOVEMOUSE', "value": 'ANY'},
         {})
    )

    def draw_settings(context, layout, tool):
        pass
'''
'''
class MyOtherTool(WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'OBJECT'

    bl_idname = "my_template.my_other_select"
    bl_label = "My Lasso Tool Select"
    bl_description = (
        "This is a tooltip\n"
        "with multiple lines"
    )
    bl_icon = "ops.generic.select_lasso"
    bl_widget = None
    bl_keymap = (
        ("view3d.select_lasso", {"type": 'LEFTMOUSE', "value": 'PRESS'}, None),
        ("view3d.select_lasso", {"type": 'LEFTMOUSE', "value": 'PRESS', "ctrl": True},
         {"properties": [("mode", 'SUB')]}),
    )

    def draw_settings(context, layout, tool):
        props = tool.operator_properties("view3d.select_lasso")
        layout.prop(props, "mode")


class MyWidgetTool(WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'OBJECT'

    bl_idname = "my_template.my_gizmo_translate"
    bl_label = "My Gizmo Tool"
    bl_description = "Short description"
    bl_icon = "ops.transform.translate"
    bl_widget = "VIEW3D_GGT_tool_generic_handle_free"
    bl_widget_properties = [
        ("radius", 75.0),
        ("backdrop_fill_alpha", 0.0),
    ]
    bl_keymap = (
        ("transform.translate", {"type": 'LEFTMOUSE', "value": 'PRESS'}, None),
    )

    def draw_settings(context, layout, tool):
        props = tool.operator_properties("transform.translate")
        layout.prop(props, "mode")
'''
