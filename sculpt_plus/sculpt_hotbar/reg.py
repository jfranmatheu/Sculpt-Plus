import bpy
from bpy.app.timers import register as register_timer, is_registered as is_timer_registered
from bpy.types import GizmoGroup as GZG, Gizmo as GZ
from mathutils import Vector
from sculpt_plus.prefs import get_prefs
from sculpt_plus.sculpt_hotbar.km import WidgetKM as KM
from sculpt_plus.sculpt_hotbar.canvas import Canvas as CV
from sculpt_plus.utils.gpu import LiveView
from sculpt_plus.props import Props, CM_UIContext, bm_data
from bl_ui.space_toolsystem_toolbar import VIEW3D_PT_tools_active
from bl_ui.space_toolsystem_common import ToolSelectPanelHelper
# from .km import create_hotbar_km

exclude_brush_tools: set[str] = {'MASK', 'DRAW_FACE_SETS', 'DISPLACEMENT_ERASER', 'DISPLACEMENT_SMEAR', 'SIMPLIFY'}

initialized = False


def init_master(gzg,ctx,gmaster):
    gzg.roff = (0, 0)
    gzg.rdim = (ctx.region.width, ctx.region.height)
    gmaster.reg=ctx.region
    gmaster.init(ctx)
    gmaster.use_event_handle_all = True
    gmaster.use_draw_modal = True
    gmaster.scale_basis = 1.0
    gzg.master = gmaster



def initialize_brush():
    context = bpy.context

    with CM_UIContext(context, mode='SCULPT', item_type='BRUSH'):
        if active_br := bm_data.active_brush:
            active_br.set_active(context)
        elif active_cat := bm_data.active_category:
            if active_cat.items.count > 0:
                active_cat.items[0].set_active(context)
        else:
            if context.space_data is None:
                Props.SculptTool.clear_stored()
                return None
            bpy.ops.wm.tool_set_by_id(name='builtin_brush.Draw')
            Props.SculptTool.update_stored(context)


def dummy_poll_view(ctx):
    if ctx.mode != 'SCULPT':
        return False
    global initialized
    if not initialized or Props.SculptTool.get_stored() == 'NULL':
        # HACK. lol.
        # print("NOT ACTIVE BRUSH, LET'S CHANGE THAT!")
        if is_timer_registered(initialize_brush):
            return True
        initialized = True
        register_timer(initialize_brush, first_interval=.1)
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
        gzg.roff = (off_left, off_bot)
        gzg.rdim = (width, height)
        p = get_prefs(ctx)
        cv.update((off_left, off_bot), (width, height), p.get_scale(ctx), p)


class Master(GZ):
    bl_idname: str = 'VIEW3D_GZ_sculpt_hotbar'
    _cv_instance = None

    @classmethod
    def get(cls, r) -> CV:
        if cls._cv_instance is None:
            cls._cv_instance = CV(r)
        return cls._cv_instance

    def init(x, c): x.cv.update((0,0), (c.region.width, c.region.height), get_prefs(c).get_scale(c), get_prefs(c))
    def setup(x): setattr(x, 'cv', x.__class__.get(bpy.context.region))
    def test_select(x,c,l):
        res = x.cv.test(c,l) if hasattr(x,'cv') else -1
        # print("test result ->", res)
        return res
    def invoke(x,c,e): return x.cv.invoke(c,e) if hasattr(x,'cv') else {'FINISHED'}
    def modal(c,x,e,t): return x.cv.modal(c,e,t) if hasattr(x,'cv') else {'FINISHED'}
    def exit(x,c,ca): return x.cv.exit(c,ca) if hasattr(x,'cv') else None
    def draw(x,c): x.cv.draw(c) if hasattr(x,'cv') else None

'''
class Test(GZG, KM):
    bl_idname: str = 'VIEW3D_GZG_test_sculpt_plus'
    bl_label: str = 'Test Sculpt Plus'
    bl_space_type: str = 'VIEW_3D'
    bl_region_type: str = 'WINDOW'
    bl_options: set[str] = {'PERSISTENT', 'SHOW_MODAL_ALL'}

    @classmethod
    def poll(cls, y) -> bool:
        return y.mode == 'SCULPT'

    def setup(x, y):
        pass # x.gizmos.new("GIZMO_GT_button_2d")
'''

class Controller(GZG, KM):
    bl_idname: str = 'VIEW3D_GZG_sculpt_hotbar'
    bl_label: str = 'Sculpt Hotbar Controller'
    bl_space_type: str = 'VIEW_3D'
    bl_region_type: str = 'WINDOW'
    bl_options: set[str] = {'PERSISTENT', 'SHOW_MODAL_ALL'} #, 'EXCLUDE_MODAL' , '3D'}
    gz: GZ = Master

    # setup_keymap = KM.setup_keymap

    @classmethod
    def poll(cls, y) -> bool:
        res = dummy_poll_view(y) and y.object and y.mode=='SCULPT' and y.scene.sculpt_hotbar.show_gizmo_sculpt_hotbar and y.space_data.show_gizmo and Props.Workspace(y) == y.workspace
        # print("poll result ->", res)
        return res

    def setup(x, y): init_master(x,y,x.gizmos.new(x.__class__.gz.bl_idname))

    def draw_prepare(x, y):
        # create_hotbar_km()
        if hasattr(x,'master') and hasattr(x.master,'cv'):
            update_master(x,y,x.master.cv)

    def refresh(x, y):
        if on_refresh(x,y) and hasattr(x,'master') and hasattr(x.master,'cv'):
            setattr(x.master.cv,'reg',y.region)

bpy.sculpt_hotbar = Master
