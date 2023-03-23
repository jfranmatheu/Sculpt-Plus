import bpy

from sculpt_plus.core.ops.gestures import SCULPTPLUS_OT_gesture_size_strength


def register():
    act_keymap_config = bpy.context.window_manager.keyconfigs.active
    sculpt_km = act_keymap_config.keymaps['Sculpt']
    
    for kmi in reversed(sculpt_km.keymap_items):
        if kmi.name == 'Sculpt Context Menu':
            sculpt_km.keymap_items.remove(kmi)

    # sculpt_km.keymap_items.new_modal()
    sculpt_km.keymap_items.new(SCULPTPLUS_OT_gesture_size_strength.bl_idname, 'RIGHTMOUSE', 'CLICK_DRAG')
