
import bpy
sculpt_hotbar_classes = []

def register():
    print("[SculptHotbar] Registering...")
    from bpy.types import GizmoGroup as GZG, Gizmo as GZ
    from mathutils import Vector
    from sculpt_hotbar.prefs import get_prefs
    from sculpt_hotbar.km import WidgetKM as KM
    from sculpt_hotbar.canvas import Canvas as CV
    def init_master(gzg,ctx,gmaster):
        gzg.rdim = (ctx.region.width, ctx.region.height)
        gmaster.reg=ctx.region
        gmaster.init(ctx)
        gmaster.use_event_handle_all = True
        gmaster.use_draw_modal = True
        gmaster.scale_basis = 1.0
        if not bpy.sculpt_hotbar._cv_instance:
            bpy.sculpt_hotbar._cv_instance = gmaster.cv
            ctx.scene.sculpt_hotbar.init_brushes()
        gzg.master = gmaster
    def update_master(gzg,ctx,cv):
        if cv.reg != ctx.region or gzg.rdim[0] != ctx.region.width or gzg.rdim[1] != ctx.region.height:
            cv.reg = ctx.region
            gzg.rdim = ctx.region.width, ctx.region.height
            p = get_prefs(ctx)
            cv.update(Vector(gzg.rdim),p.get_scale(ctx), p)
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
            'poll': classmethod(lambda x, y: y.object and y.mode=='SCULPT' and y.scene.sculpt_hotbar.show_gizmo_sculpt_hotbar),
            'draw_prepare': lambda x,y: update_master(x,y,x.master.cv) if hasattr(x,'master') and hasattr(x.master,'cv') else None,
            'setup': lambda x,y: init_master(x,y,x.gizmos.new(x.__class__.gz)),
            'refresh': lambda x,y: setattr(x.master.cv,'reg',y.region) if hasattr(x,'master') and hasattr(x.master,'cv') else None,
        }
    )
    master=type(
        "SculptHotbarGMaster",
        (GZ,),
        {
            'bl_idname':"VIEW3D_GZ_sculpt_hotbar",
            '_cv_instance':None,
            'get':classmethod(lambda x,r: x._cv_instance if x._cv_instance is not None else CV(r)),
            'init':lambda x, c: x.cv.update(Vector((c.region.width, c.region.height)), get_prefs(c).get_scale(c), get_prefs(c)),
            'setup':lambda x: setattr(x, 'cv', x.__class__.get(bpy.context.region)),
            'test_select':lambda x,c,_: x.cv.test(c,_) if hasattr(x,'cv') else -1,
            'invoke':lambda x,c,e: x.cv.invoke(c,e) if hasattr(x,'cv') else {'FINISHED'},
            'modal':lambda x,c,e,_: x.cv.modal(c,e,_) if hasattr(x,'cv') else {'FINISHED'},
            'exit':lambda x,c,_: x.cv.exit(c,_) if hasattr(x,'cv') else None,
            'draw':lambda x,c: x.cv.draw(c) if hasattr(x,'cv') else None,
        }
    )
    global sculpt_hotbar_classes
    sculpt_hotbar_classes = [master,controller]
    for cls in sculpt_hotbar_classes:
        bpy.utils.register_class(cls)
    bpy.sculpt_hotbar = master


def register():
    print("[SculptHotbar] Unregistering...")
    for cls in sculpt_hotbar_classes:
        bpy.utils.unregister_class(cls)
    if 'sculpt_hotbar' in bpy:
        del bpy.sculpt_hotbar
    sculpt_hotbar_classes.clear()
