import bpy
import functools
from bpy.app.timers import register as register_timer, is_registered as is_timer_registered
sculpt_hotbar_classes = []
exclude_brush_tools: set[str] = {'MASK', 'DRAW_FACE_SETS', 'DISPLACEMENT_ERASER', 'DISPLACEMENT_SMEAR', 'SIMPLIFY'}
def register():
    print("[SculptHotbar] Registering...")
    from mathutils import Vector
    from sculpt_plus.prefs import get_prefs
    from sculpt_plus.sculpt_hotbar.km import WidgetKM as KM
    from sculpt_plus.sculpt_hotbar.canvas import Canvas as CV
    from sculpt_plus.utils.gpu import LiveView
    from sculpt_plus.props import Props
    from bl_ui.space_toolsystem_toolbar import VIEW3D_PT_tools_active
    from bl_ui.space_toolsystem_common import ToolSelectPanelHelper
    def init_master(gzg,ctx,gmaster):
        gzg.roff = (0, 0)
        gzg.rdim = (ctx.region.width, ctx.region.height) # get_reg_off_dim(ctx)
        gmaster.reg=ctx.region
        gmaster.init(ctx)
        gmaster.use_event_handle_all = True
        gmaster.use_draw_modal = True
        gmaster.scale_basis = 1.0
        if not bpy.sculpt_hotbar._cv_instance:
            bpy.sculpt_hotbar._cv_instance = gmaster.cv
            # Now Blender says:
            # "AttributeError: Writing to ID classes in this context is not allowed:
            # Scene, Scene datablock, error setting SculptHotbarPG.<UNKNOWN>"
            # ctx.scene.sculpt_hotbar.init_brushes()
        gzg.master = gmaster
        #LiveView.get().start_handler(ctx)
    def initialize_brush():
        ctx = bpy.context
        if active_br := Props.GetActiveBrush():
            Props.SelectBrush(ctx, active_br)
        elif brushes := list(Props.BrushManager().brushes.values()):
            Props.SelectBrush(ctx, brushes[0])
        else:
            bpy.ops.wm.tool_set_by_id(name='builtin_brush.Draw')
            curr_active_tool = ToolSelectPanelHelper.tool_active_from_context(ctx)
            if curr_active_tool is None:
                return True
            type, curr_active_tool = curr_active_tool.idname.split('.')
            curr_active_tool = curr_active_tool.replace(' ', '_').upper()
            if curr_active_tool in exclude_brush_tools or type != 'builtin_brush':
                return True
            Props.BrushManager().active_sculpt_tool = curr_active_tool
    def dummy_poll_view(ctx):
        if ctx.mode != 'SCULPT':
            return False
        #if ctx.mode != 'SCULPT':
        #    LiveView.get().stop_handler()
        #else:
        #    LiveView.get().start_handler(ctx)
        #print(Props.BrushManager().active_sculpt_tool)
        manager = Props.BrushManager()
        if not manager.initilized or not manager.active_sculpt_tool:
            # HACK. lol.
            # print("NOT ACTIVE BRUSH, LET'S CHANGE THAT!")
            if is_timer_registered(initialize_brush):
                return True
            manager.initilized = True
            register_timer(initialize_brush, first_interval=.1)
        '''
        prev_active_tool = Props.BrushManager().active_sculpt_tool
        curr_active_tool = ToolSelectPanelHelper.tool_active_from_context(ctx)
        if curr_active_tool is None:
            return
        type, curr_active_tool = curr_active_tool.idname.split('.')
        curr_active_tool = curr_active_tool.replace(' ', '_').upper()
        if prev_active_tool != curr_active_tool:
            if curr_active_tool in exclude_brush_tools or type != 'builtin_brush':
                return True
            Props.BrushManager().active_sculpt_tool = curr_active_tool
            print(f"Info! Changed tool from {prev_active_tool} to {curr_active_tool}.")
            if curr_active_tool == 'ALL_BRUSH':
                if active_br := Props.GetActiveBrush():
                    Props.SelectBrush(ctx, active_br)
                elif brushes := list(Props.BrushManager().brushes.values()):
                    Props.SelectBrush(ctx, brushes[0])
                else:
                    bpy.ops.wm.tool_set_by_id(name='builtin_brush.draw')
        '''
        return True
    def on_refresh(gzg,ctx):
        return True
    def update_master(gzg,ctx,cv):
        off_left = 0
        off_bot = 0
        off_top = 0
        off_right = 0
        for reg in ctx.area.regions:
            if reg.type == 'TOOLS':
                off_left += reg.width
            elif reg.type == 'UI':
                off_right += reg.width
        width = ctx.region.width - off_right - off_left
        height = ctx.region.height - off_top - off_bot
        if cv.reg != ctx.region or gzg.rdim[0] != width or gzg.rdim[1] != height or off_left != gzg.roff[0] or off_bot != gzg.roff[1]:
            cv.reg = ctx.region
            cv.refresh()
            # update_off_dim(gzg,ctx)
            gzg.roff = (off_left, off_bot)
            gzg.rdim = (width, height)
            p = get_prefs(ctx)
            cv.update((off_left, off_bot), (width, height), p.get_scale(ctx), p)
    from bpy.types import GizmoGroup as GZG, Gizmo as GZ
    from ..utils.gpu import OffscreenBuffer
    controller=type(
        "SculptHotbarGController",
        (GZG,KM),
        {
            'bl_idname': "VIEW3D_GZG_sculpt_hotbar",
            'bl_label': "Sculpt Hotbar Controller",
            'bl_space_type': 'VIEW_3D',
            'bl_region_type': 'WINDOW',
            'bl_options': {'PERSISTENT', 'SHOW_MODAL_ALL'},
            'gz': "VIEW3D_GZ_sculpt_hotbar",
            'poll': classmethod(lambda x, y: dummy_poll_view(y) and y.object and y.mode=='SCULPT' and y.scene.sculpt_hotbar.show_gizmo_sculpt_hotbar and y.space_data.show_gizmo),
            'draw_prepare': lambda x,y: update_master(x,y,x.master.cv) if hasattr(x,'master') and hasattr(x.master,'cv') else None,
            'setup': lambda x,y: init_master(x,y,x.gizmos.new(x.__class__.gz)),
            'refresh': lambda x,y: setattr(x.master.cv,'reg',y.region) if on_refresh(x,y) and hasattr(x,'master') and hasattr(x.master,'cv') else None,
        }
    )
    master=type(
        "SculptHotbarGMaster",
        (GZ,),
        {
            'bl_idname':"VIEW3D_GZ_sculpt_hotbar",
            '_cv_instance':None,
            'get':classmethod(lambda x,r: x._cv_instance if x._cv_instance is not None else CV(r)),
            'init':lambda x, c: x.cv.update((0,0), (c.region.width, c.region.height), get_prefs(c).get_scale(c), get_prefs(c)),
            'setup':lambda x: setattr(x, 'cv', x.__class__.get(bpy.context.region)),
            'test_select':lambda x,c,_: x.cv.test(c,_) if hasattr(x,'cv') else -1,
            'invoke':lambda x,c,e: x.cv.invoke(c,e) if hasattr(x,'cv') else {'FINISHED'},
            'modal':lambda x,c,e,_: x.cv.modal(c,e,_) if hasattr(x,'cv') else {'FINISHED'},
            'exit':lambda x,c,_: x.cv.exit(c,_) if hasattr(x,'cv') else None,
            'draw':lambda x,c: OffscreenBuffer.draw(c), # x.cv.draw(c) if hasattr(x,'cv') else None,
        }
    )
    global sculpt_hotbar_classes
    sculpt_hotbar_classes = [master,controller]
    for cls in sculpt_hotbar_classes:
        bpy.utils.register_class(cls)
    bpy.sculpt_hotbar = master
def unregister():
    print("[SculptHotbar] Unregistering...")
    for cls in sculpt_hotbar_classes:
        bpy.utils.unregister_class(cls)
    if getattr(bpy, 'sculpt_hotbar', None):
        del bpy.sculpt_hotbar
    sculpt_hotbar_classes.clear()
