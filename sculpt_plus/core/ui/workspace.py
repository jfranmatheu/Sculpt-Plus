from bpy.types import Operator, Context, Event, WorkSpace, Menu
import bpy
from bl_ui.space_topbar import TOPBAR_HT_upper_bar

from ...props import Props
from ...path import SculptPlusPaths
from ...previews import Previews

from ...ackit import ACK


class SetupWorkspace(ACK.Type.OPS.ACTION):
    label = 'Setup Sculpt+ Workspace'
    tooltip = "Add the 'Sculpt+' Workspace to your .blend and set it up to start using Sculpt+ in your project!"

    def invoke(self, context: 'Context', event: 'Event'):
        workspace = Props().Workspace(context)
        if workspace is not None:
            return {'CANCELLED'}

        # old_workspace = context.window.workspace
        try:
            # Workaround to ensure context is OK before workspace.append_active.
            Props.Temporal(context).test_context = True
        except RuntimeError as e:
            print(e)
            return {'CANCELLED'}

        bpy.ops.workspace.append_activate(False, idname='Sculpt+', filepath=SculptPlusPaths.BLEND_WORKSPACE())
        workspace: WorkSpace = bpy.data.workspaces.get('Sculpt+', None)
        context.window.workspace = workspace

        # Set-up the workspace.
        if 'sculpt_plus' not in workspace:
            workspace['sculpt_plus'] = 1
        workspace['first_time'] = 1

        workspace.use_filter_by_owner = True

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context: 'Context', event: 'Event'):
        bpy.ops.wm.owner_enable('INVOKE_DEFAULT', False, owner_id="sculpt_plus")
        return {'FINISHED'}


def draw_workspace_setup_op(self, context: Context):
    if context.region.alignment != 'RIGHT' and Props.Workspace(context) is None:
        if issubclass(self.__class__, Menu):
            self.layout.separator()
            self.layout.operator(SetupWorkspace.bl_idname, text="Sculpt +", icon_value=Previews.Main.BRUSH_BROOM())
        else:
            self.layout.operator(SetupWorkspace.bl_idname, text="S+", icon_value=Previews.Main.BRUSH_BROOM())

def register():
    TOPBAR_HT_upper_bar.append(draw_workspace_setup_op)

def unregister():
    TOPBAR_HT_upper_bar.remove(draw_workspace_setup_op)
