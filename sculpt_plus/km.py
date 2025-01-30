import bpy

from .core.ops.gestures import SCULPTPLUS_OT_gesture_size_strength


def register():
    act_keymap_config = bpy.context.window_manager.keyconfigs.active
    sculpt_km = act_keymap_config.keymaps['Sculpt']
    
    for kmi in reversed(sculpt_km.keymap_items):
        if kmi.name == 'Sculpt Context Menu':
            sculpt_km.keymap_items.remove(kmi)

    # sculpt_km.keymap_items.new_modal()
    sculpt_km.keymap_items.new(SCULPTPLUS_OT_gesture_size_strength.bl_idname, 'RIGHTMOUSE', 'CLICK_DRAG')

    # if act_keymap_config.keymaps.get('VIEW3D_GZG_sculpt_hotbar', None) is None:
    #     from .sculpt_hotbar.km import hotkeys, op
    #     km = act_keymap_config.keymaps.new(name='VIEW3D_GZG_sculpt_hotbar', space_type='VIEW_3D', region_type='WINDOW')
    #     print("KM CREATE!", km, 'VIEW3D_GZG_sculpt_hotbar')
    #     for key in hotkeys:
    #         km.keymap_items.new(op, key, 'ANY', any=True);km.keymap_items.new(op, key, 'RELEASE', any=True)
    #     km.keymap_items.new(op, 'LEFT_ALT', 'ANY', alt=True)
