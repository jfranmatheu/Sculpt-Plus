import bpy
from bpy.app.timers import register as register_timer, is_registered as is_timer_registered
from bpy.types import GizmoGroup as GZG, Gizmo as GZ, Region, Context
from mathutils import Vector
from sculpt_plus.prefs import get_prefs
from sculpt_plus.sculpt_hotbar.km import WidgetKM as KM
from sculpt_plus.sculpt_hotbar.canvas import Canvas as CV
from sculpt_plus.utils.gpu import LiveView
from sculpt_plus.props import Props, CM_UIContext, SculptTool
from sculpt_plus.globals import G
from bl_ui.space_toolsystem_toolbar import VIEW3D_PT_tools_active
from bl_ui.space_toolsystem_common import ToolSelectPanelHelper

from brush_manager.globals import GLOBALS
# from .km import create_hotbar_km

exclude_brush_tools: set[str] = {'MASK', 'DRAW_FACE_SETS', 'DISPLACEMENT_ERASER', 'DISPLACEMENT_SMEAR', 'SIMPLIFY'}

initialized = False




def initialize_brush():
    if GLOBALS.is_importing_a_library:
        return 0.5

    context = bpy.context

    if context != 'SCULPT':
        return 1.0

    with CM_UIContext(context, mode='SCULPT', item_type='BRUSH'):
        if active_br := G.bm_data.active_brush:
            active_br.set_active(context)
            SculptTool.update_stored(context)
        elif active_cat := G.bm_data.active_category:
            if active_cat.items.count > 0:
                try:
                    active_cat.items[0].set_active(context)
                except Exception:
                    return 1.0
        else:
            if context.space_data is None:
                SculptTool.clear_stored()
                return None
            bpy.ops.wm.tool_set_by_id(name='builtin_brush.Draw')
            SculptTool.update_stored(context)


def dummy_poll_view(ctx):
    global initialized
    if not initialized or SculptTool.get_stored() == 'NONE':
        # HACK. lol.
        # print("NOT ACTIVE BRUSH, LET'S CHANGE THAT!")
        if is_timer_registered(initialize_brush):
            return True
        initialized = True
        register_timer(initialize_brush, first_interval=.1)
    return True



class Master(GZ):
    bl_idname: str = 'VIEW3D_GZ_sculpt_hotbar'
    _cv_instance = None

    cv: CV
    reg: Region

    @classmethod
    def get_cv(cls, ctx: Context | None = None) -> CV:
        if cls._cv_instance is None:
            ctx = ctx if ctx is not None else bpy.context
            cls._cv_instance = CV(ctx.region, get_prefs(ctx))
        return cls._cv_instance

    def setup(x): pass
    def test_select(x,c,l): return Master.get_cv(c).test(c,l)
    def invoke(x,c,e): return Master.get_cv(c).invoke(c,e)
    def modal(x,c,e,t): return Master.get_cv(c).modal(c,e,t)
    def exit(x,c,ca): return Master.get_cv(c).exit(c,ca)
    def draw(x,c): pass



class Controller(GZG, KM):
    bl_idname: str = 'VIEW3D_GZG_sculpt_hotbar'
    bl_label: str = 'Sculpt Hotbar Controller'
    bl_space_type: str = 'VIEW_3D'
    bl_region_type: str = 'WINDOW'
    bl_options: set[str] = {'PERSISTENT', 'SHOW_MODAL_ALL'} #, 'EXCLUDE_MODAL' , '3D'}
    # gz: GZ = Master
    # setup_keymap = KM.setup_keymap

    @classmethod
    def poll(cls, y) -> bool:
        # dummy_poll_view(y) and
        res = y.object is not None and y.mode=='SCULPT' and y.scene.sculpt_hotbar.show_gizmo_sculpt_hotbar and y.space_data.show_gizmo and Props.Workspace(y) == y.workspace
        # print("poll result ->", res)
        # if res:
        #     dummy_poll_view(y)
        return res

    def setup(gzg, ctx):
        gzg.rdim = (ctx.region.width, ctx.region.height)
        gzg.roff = (0, 0)

        gzg.init_master(ctx, gzg.gizmos.new(Master.bl_idname))

    def draw_prepare(gzg, ctx: Context):
        gzg.update_master(ctx)

    def refresh(gzg, ctx: Context):
        cv = Master.get_cv(ctx)
        if cv.reg != ctx.region:
            setattr(cv, 'reg', ctx.region)
            gzg.update_master(ctx)


    def init_master(gzg, ctx: Context, gz_master: Master):
        gz_master.reg=ctx.region
        gz_master.use_event_handle_all = True
        gz_master.use_draw_modal = True
        gz_master.scale_basis = 1.0
        gzg.master=gz_master

    def update_master(gzg, ctx: Context):
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
        cv=Master.get_cv(ctx)
        if cv.reg != ctx.region or gzg.rdim[0] != width or gzg.rdim[1] != height or off_left != gzg.roff[0] or off_bot != gzg.roff[1]:
            cv.reg = ctx.region
            cv.refresh()
            gzg.roff = (off_left, off_bot)
            gzg.rdim = (width, height)
            p = get_prefs(ctx)
            cv.update((off_left, off_bot), (width, height), p.get_scale(ctx), p)


def register():
    bpy.sculpt_hotbar = Master

def unregister():
    del bpy.sculpt_hotbar
