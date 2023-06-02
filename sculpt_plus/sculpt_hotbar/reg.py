import bpy
from bpy.app.timers import register as register_timer, is_registered as is_timer_registered
from bpy.types import GizmoGroup as GZG, Gizmo as GZ
from mathutils import Vector
from sculpt_plus.prefs import get_prefs
from sculpt_plus.sculpt_hotbar.km import WidgetKM as KM
from sculpt_plus.sculpt_hotbar.canvas import Canvas as CV
from sculpt_plus.utils.gpu import LiveView
from sculpt_plus.props import Props
from bl_ui.space_toolsystem_toolbar import VIEW3D_PT_tools_active
from bl_ui.space_toolsystem_common import ToolSelectPanelHelper
# from .km import create_hotbar_km

exclude_brush_tools: set[str] = {'MASK', 'DRAW_FACE_SETS', 'DISPLACEMENT_ERASER', 'DISPLACEMENT_SMEAR', 'SIMPLIFY'}



def initialize_brush():
    ctx = bpy.context
    if active_br := Props.GetActiveBrush():
        Props.SelectBrush(ctx, active_br)
    elif brushes := list(Props.BrushManager().brushes.values()):
        Props.SelectBrush(ctx, brushes[0])
    else:
        if ctx.space_data is None:
            Props.BrushManager().active_sculpt_tool = 'NULL'
            return None
        bpy.ops.wm.tool_set_by_id(name='builtin_brush.Draw')
        curr_active_tool = ToolSelectPanelHelper.tool_active_from_context(ctx)
        if curr_active_tool is None:
            return
        type, curr_active_tool = curr_active_tool.idname.split('.')
        curr_active_tool = curr_active_tool.replace(' ', '_').upper()
        if curr_active_tool in exclude_brush_tools or type != 'builtin_brush':
            return
        Props.BrushManager().active_sculpt_tool = curr_active_tool


def ensure_brush_manager(ctx):
    manager = Props.BrushManager()
    if not manager.initilized or not manager.active_sculpt_tool:
        # HACK. lol.
        # print("NOT ACTIVE BRUSH, LET'S CHANGE THAT!")
        if is_timer_registered(initialize_brush):
            return True
        manager.initilized = True
        register_timer(initialize_brush, first_interval=.1)
    return True


def update_transform(gzg,ctx,cv):
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
        gzg.roff = (off_left, off_bot)
        gzg.rdim = (width, height)
        return CV.get(ctx).update(ctx, (off_left, off_bot), (width, height))
        # cv.update((off_left, off_bot), (width, height), p.get_scale(ctx), p)


class Master(GZ):
    bl_idname: str = 'VIEW3D_GZ_sculpt_hotbar'
    _cv_instance = None

    def init(x, c): CV.get(c).update(c, (0,0), (c.region.width, c.region.height))
    def setup(x): pass
    def test_select(x,c,l): return CV.get(c).test(c,l)
    def invoke(x,c,e): return CV.get(c).invoke(c,e)
    def modal(x,c,e,t): return CV.get(c).modal(c,e,t)
    def exit(x,c,ca):
        return CV.get(c).exit(c,cancel=ca)
    def draw(x,c): 
        return CV.get(c).draw(c)


class Controller(GZG, KM):
    bl_idname: str = 'VIEW3D_GZG_sculpt_hotbar'
    bl_label: str = 'Sculpt Hotbar Controller'
    bl_space_type: str = 'VIEW_3D'
    bl_region_type: str = 'WINDOW'
    bl_options: set[str] = {'PERSISTENT', 'SHOW_MODAL_ALL'} #, 'EXCLUDE_MODAL' , '3D'}

    @classmethod
    def poll(cls, y) -> bool:
        return y.object is not None and y.mode=='SCULPT' and\
               y.scene.sculpt_hotbar.show_gizmo_sculpt_hotbar and y.space_data.show_gizmo and\
               Props.Workspace(y) == y.workspace and CV.get(y).poll_region(y, update_if_missing=True)

    def setup(x, y):
        ensure_brush_manager(y)
        x.init_master(y,x.gizmos.new(Master.bl_idname))

    def init_master(gzg,ctx,gmaster:GZ):
        gzg.roff = (0, 0)
        gzg.rdim = (ctx.region.width, ctx.region.height)
        gmaster.init(ctx)
        gmaster.use_event_handle_all = True
        gmaster.use_draw_modal = True
        gmaster.scale_basis = 1.0
        gzg.master = gmaster

    def draw_prepare(x, y): x.refresh(y)

    def refresh(x, y):
        cv = CV.get(y)
        cv.poll_region(y, update_if_missing=False)
        update_transform(x,y,cv)

bpy.sculpt_hotbar = Master
