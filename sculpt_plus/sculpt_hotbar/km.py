keys = (
    'ONE',
    'TWO',
    'THREE',
    'FOUR',
    'FIVE',
    'SIX',
    'SEVEN',
    'EIGHT',
    'NINE',
    'ZERO'
)
hotkeys=(
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
    'ZERO', 'ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE',
    'LEFT_ARROW', 'DOWN_ARROW', 'RIGHT_ARROW', 'UP_ARROW',
    'LEFTMOUSE', 'MIDDLEMOUSE', 'RIGHTMOUSE', 'PEN', 'ERASER', #'MOUSEMOVE', 'INBETWEEN_MOUSEMOVE',
    'WHEELUPMOUSE', 'WHEELDOWNMOUSE', 'WHEELINMOUSE', 'WHEELOUTMOUSE',
    'RET', 'SPACE', 'BACK_SPACE', 'DEL',
    'TIMER'
)
addon_keymaps = []
import bpy
from bpy.types import KeyConfig, KeyConfigPreferences, KeyConfigurations, KeyMap, KeyMapItem, KeyMapItems
op = 'gizmogroup.gizmo_tweak'
def register():
    from .reg import Controller
    from . ops import SCULPTHOTBAR_OT_set_brush
    from sculpt_plus.management.operators import SCULPTPLUS_OT_set_hotbar_alt
    # from sculpt_plus.core.editors.view_3d.toolbar.all_brush_tool import SCULPTPLUS_OT_all_brush_tool
    from bpy import context as C
    cfg = C.window_manager.keyconfigs.addon
    if not cfg:
        return
    opid = SCULPTHOTBAR_OT_set_brush.bl_idname
    for idx, key in enumerate(keys):
        if not cfg.keymaps.__contains__('Sculpt'):
            cfg.keymaps.new('Sculpt', space_type='EMPTY', region_type='WINDOW')
        kmi = cfg.keymaps['Sculpt'].keymap_items
        kmi.new(opid, key, 'PRESS').properties.index = idx
        kmi.new(opid, key, 'PRESS', alt=True).properties.index = idx
    kmi.new(SCULPTPLUS_OT_set_hotbar_alt.bl_idname, 'LEFT_ALT', 'PRESS', alt=True).properties.enabled = True
    kmi.new(SCULPTPLUS_OT_set_hotbar_alt.bl_idname, 'LEFT_ALT', 'RELEASE', alt=False).properties.enabled = False
    kmi.new(SCULPTPLUS_OT_set_hotbar_alt.bl_idname, 'LEFT_ALT', 'RELEASE', alt=False).properties.enabled = False

    # km = cfg.keymaps.get('Sculpt') # cfg.keymaps.new(name='Window', space_type='EMPTY')
    # kmi = km.keymap_items.new(Controller.bl_idname, type = 'P', value = 'PRESS', ctrl=False, shift=True)
    # for key in hotkeys:
    #     kmi = km.keymap_items.new(Controller.bl_idname, key, 'ANY', any=True)
    #     addon_keymaps.append((km, kmi))
    #     kmi = km.keymap_items.new(Controller.bl_idname, key, 'RELEASE', any=True)
    #     addon_keymaps.append((km, kmi))
    # kmi = km.keymap_items.new(Controller.bl_idname, 'LEFT_ALT', 'ANY', alt=True)
    # addon_keymaps.append((km, kmi))

def unregister():
    # handle the keymap
    # for km, kmi in addon_keymaps:
    #     km.keymap_items.remove(kmi)
    # addon_keymaps.clear()
    from . ops import SCULPTHOTBAR_OT_set_brush
    from sculpt_plus.management.operators import SCULPTPLUS_OT_set_hotbar_alt
    from bpy import context as C
    cfg = C.window_manager.keyconfigs.addon
    opid = {SCULPTHOTBAR_OT_set_brush.bl_idname, SCULPTPLUS_OT_set_hotbar_alt.bl_idname}
    if cfg.keymaps.__contains__('Sculpt'):
        for kmi in cfg.keymaps['Sculpt'].keymap_items:
            if kmi.idname == opid: # in opid:
                cfg.keymaps['Sculpt'].keymap_items.remove(kmi)
class WidgetKM:
    @classmethod
    def setup_keymap(cls, keyconfig: KeyConfig):
        return create_hotbar_km(cls, keyconfig) # bpy.context.window_manager.keyconfigs.active.keymaps.get(master.bl_idname, None)


def create_hotbar_km(cls=None, keyconfig=None):
    if cls:
        pass
    else:
        from .reg import Controller
        cls = Controller
    if keyconfig is None:
        keyconfig = bpy.context.window_manager.keyconfigs.addon
    print("******************************************************\n [[SCULPT+] WIDGET KEYMAP SETUP \n******************************************************")
    # print(keyconfig.name, keyconfig.preferences.bl_idname, keyconfig.keymaps.keys(), cls.bl_idname)
    if keyconfig.preferences is None:
        km = bpy.context.window_manager.keyconfigs.addon.keymaps.new(cls.bl_idname, space_type='VIEW_3D', region_type='WINDOW')
        print("INVALID! -> CREATE!", km, cls.bl_idname)
        for key in hotkeys:
            km.keymap_items.new(op, key, 'ANY', any=True);km.keymap_items.new(op, key, 'RELEASE', any=True)
        km.keymap_items.new(op, 'LEFT_ALT', 'ANY', alt=True)
        return km

    print(keyconfig.name, keyconfig.preferences.bl_idname, cls.bl_idname)
    if km:=keyconfig.keymaps.get(cls.bl_idname, None):
        if km.keymap_items and len(km.keymap_items) > 1:
            print("EXISTS!", km, cls.bl_idname, len(km.keymap_items))
            return km
    # import bpy
    # act_keymap_config: KeyConfig = bpy.context.window_manager.keyconfigs.active
    # sculpt_km = act_keymap_config.keymaps['Sculpt']
    # for keyconfig in bpy.context.window_manager.keyconfigs:
    km = keyconfig.keymaps.new(name=cls.bl_idname, space_type='VIEW_3D', region_type='WINDOW')
    print("CREATE!", km, cls.bl_idname)
    for key in hotkeys:
        km.keymap_items.new(op, key, 'ANY', any=True);km.keymap_items.new(op, key, 'RELEASE', any=True)
    km.keymap_items.new(op, 'LEFT_ALT', 'ANY', alt=True)
    return km
