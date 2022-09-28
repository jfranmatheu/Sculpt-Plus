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
op = 'gizmogroup.gizmo_tweak'
def register():
    from . ops import SCULPTHOTBAR_OT_select_brush, SCULPTHOTBAR_OT_swap_set
    from bpy import context as C
    cfg = C.window_manager.keyconfigs.addon
    opid = SCULPTHOTBAR_OT_select_brush.bl_idname
    for idx, key in enumerate(keys):
        if not cfg.keymaps.__contains__('Sculpt'):
            cfg.keymaps.new('Sculpt', space_type='EMPTY', region_type='WINDOW')
        kmi = cfg.keymaps['Sculpt'].keymap_items
        kmi.new(opid, key, 'PRESS').properties.index = idx
        kmi.new(opid, key, 'PRESS', alt=True).properties.index = idx
        kmi.new(SCULPTHOTBAR_OT_swap_set.bl_idname, 'LEFT_ALT', 'PRESS', alt=True).properties.enabled = True
        kmi.new(SCULPTHOTBAR_OT_swap_set.bl_idname, 'LEFT_ALT', 'RELEASE', alt=False).properties.enabled = False
def unregister():
    from . ops import SCULPTHOTBAR_OT_select_brush
    from bpy import context as C
    cfg = C.window_manager.keyconfigs.addon
    opid = SCULPTHOTBAR_OT_select_brush.bl_idname
    if cfg.keymaps.__contains__('Sculpt'):
        for kmi in cfg.keymaps['Sculpt'].keymap_items:
            if kmi.idname == opid:
                cfg.keymaps['Sculpt'].keymap_items.remove(kmi)
class WidgetKM:
    @classmethod
    def setup_keymap(cls, keyconfig):
        km = keyconfig.keymaps.get(cls.bl_idname, None)
        if km and km.keymap_items and len(km.keymap_items) > 1: return km
        km = keyconfig.keymaps.new(name=cls.bl_idname, space_type='VIEW_3D', region_type='WINDOW')
        for key in hotkeys: km.keymap_items.new(op, key, 'ANY', any=True);km.keymap_items.new(op, key, 'RELEASE', any=True)
        km.keymap_items.new(op, 'LEFT_ALT', 'ANY', alt=True)
        return km
