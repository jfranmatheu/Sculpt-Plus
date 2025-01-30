import bpy

from .core.ops.gestures import GestureSizeStrength


def register():
    act_keymap_config = bpy.context.window_manager.keyconfigs.active
    sculpt_km = act_keymap_config.keymaps['Sculpt']
    
    for kmi in reversed(sculpt_km.keymap_items):
        if kmi.name == 'Sculpt Context Menu':
            sculpt_km.keymap_items.remove(kmi)

    # sculpt_km.keymap_items.new_modal()
    sculpt_km.keymap_items.new(GestureSizeStrength.bl_idname, 'RIGHTMOUSE', 'CLICK_DRAG', alt=True)

    # if act_keymap_config.keymaps.get('VIEW3D_GZG_sculpt_hotbar', None) is None:
    #     from .sculpt_hotbar.km import hotkeys, op
    #     km = act_keymap_config.keymaps.new(name='VIEW3D_GZG_sculpt_hotbar', space_type='VIEW_3D', region_type='WINDOW')
    #     print("KM CREATE!", km, 'VIEW3D_GZG_sculpt_hotbar')
    #     for key in hotkeys:
    #         km.keymap_items.new(op, key, 'ANY', any=True);km.keymap_items.new(op, key, 'RELEASE', any=True)
    #     km.keymap_items.new(op, 'LEFT_ALT', 'ANY', alt=True)
