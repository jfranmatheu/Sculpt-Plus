import bpy
from bl_ui.space_toolsystem_toolbar import VIEW3D_PT_tools_active, _defs_transform, _defs_annotate, _defs_sculpt
from bl_ui.space_toolsystem_common import ToolDef, ToolSelectPanelHelper
from bpy.app import handlers

from typing import List, Dict

from .all_brush_tool import SCULPTPLUS_OT_all_brush_tool


unregistered_tools: List[ToolDef] = []

hidden_brush_tools: Dict[str, ToolDef] = {}

accept_brush_tools: set[str] = {'MASK', 'DRAW_FACE_SETS', 'DISPLACEMENT_ERASER', 'DISPLACEMENT_SMEAR', 'SIMPLIFY'}


def draw_settings__sculpt_brush_tool(self, context, tool):
    props = tool.operator_properties("SCULPT_OT_brush_stroke")


def generate_from_brushes(dummy=None):
    tool_defs = {}
    idname_prefix="builtin_brush."
    icon_prefix="brush.sculpt."
    type=bpy.types.Brush
    attr="sculpt_tool"
    for enum in type.bl_rna.properties[attr].enum_items_static:
        name = enum.name
        idname = enum.identifier
        # print(idname)
        if idname not in accept_brush_tools:
            continue
        tool_defs[idname] = ToolDef.from_dict(
            dict(
                idname=idname_prefix + name,
                label=name,
                icon=icon_prefix + idname.lower(),
                cursor='DEFAULT',
                data_block=idname,
            )
        )
    '''
    name = "Sculpt Brush"
    idname = "SCULPT_BRUSH"
    tool_defs[idname] = ToolDef.from_dict(
        dict(
            idname='sculpt_plus.' + name,
            label=name,
            icon=icon_prefix + 'draw',
            cursor='DEFAULT',
            keymap="3D View Tool: Sculpt",
            #data_block='SCULPT DRAW',
            draw_settings=draw_settings__sculpt_brush_tool,
            operator='sculpt.brush_stroke',
            #options={'KEYMAP_FALLBACK'},
        )
    )
    '''
    return tool_defs

'''
@ToolDef.from_fn
def all_brush_tool():
    def draw_settings(_context, layout, tool):
        props = tool.operator_properties(SCULPTPLUS_OT_all_brush_tool.bl_idname)
    return dict(
        idname="builtin.all_brush",
        label='Sculpt Brush',
        operator=SCULPTPLUS_OT_all_brush_tool.bl_idname,
        icon="brush.gpencil_draw.draw",
        # cursor='DEFAULT',
        keymap="3D View Tool: Sculpt Brush",
        draw_settings=draw_settings,
    )
'''


def set_sculpt_tools():
    '''
    from bpy import context as C

    tool_name = '3D View Tool: Sculpt, Sculpt Brush'
    cfg = C.window_manager.keyconfigs.default
    if tool_name not in cfg.keymaps:
        cfg.keymaps.new(tool_name, space_type='VIEW_3D', region_type='WINDOW')
        kmi = cfg.keymaps[tool_name].keymap_items
        if SCULPTPLUS_OT_all_brush_tool.bl_idname not in kmi:
            kmi.new(SCULPTPLUS_OT_all_brush_tool.bl_idname, 'MIDDLEMOUSE', 'PRESS', any=True)
    '''
    tools = generate_from_brushes()
    ALL_BRUSH = ToolDef.from_dict(
        dict(
            idname="builtin_brush.all_brush",
            label='Sculpt Brush',
            icon="brush.sculpt.draw",
            #icon="brush.gpencil_draw.draw",
            cursor='DEFAULT',
            data_block='DRAW',
            #operator='sculpt_plus.all_brush_tool',
            #keymap=tool_name,
        )
    )
    '''
    cfg = C.window_manager.keyconfigs.addon
    if tool_name not in cfg.keymaps:
        cfg.keymaps.new(tool_name, space_type='VIEW_3D', region_type='WINDOW')
        kmi = cfg.keymaps[tool_name].keymap_items
        if SCULPTPLUS_OT_all_brush_tool.bl_idname not in kmi:
            kmi.new(SCULPTPLUS_OT_all_brush_tool.bl_idname, 'MIDDLEMOUSE', 'ANY', any=True)
    '''

    VIEW3D_PT_tools_active._tools['SCULPT'] = [
        #tools['SCULPT_BRUSH'],
        ALL_BRUSH,
        None,
        _defs_sculpt.generate_from_brushes, # NOW These brush tools are skiped in the UI, hidden.
        None,
        tools['MASK'],
        (
            _defs_sculpt.mask_border,
            _defs_sculpt.mask_lasso,
            _defs_sculpt.mask_line,
        ),
        _defs_sculpt.mask_by_color,
        None,
        tools['DRAW_FACE_SETS'],
        (
            _defs_sculpt.face_set_box,
            _defs_sculpt.face_set_lasso,
        ),
        _defs_sculpt.face_set_edit,
        None,
        _defs_sculpt.hide_border,
        (
            _defs_sculpt.trim_box,
            _defs_sculpt.trim_lasso,
        ),
        _defs_sculpt.project_line,
        None,
        _defs_sculpt.mesh_filter,
        _defs_sculpt.cloth_filter,
        _defs_sculpt.color_filter,
        None,
        tools['SIMPLIFY'],
        tools['DISPLACEMENT_SMEAR'],
        tools['DISPLACEMENT_ERASER'],
        None,
        _defs_transform.translate,
        _defs_transform.rotate,
        _defs_transform.scale,
        _defs_transform.transform,
        None,
        *VIEW3D_PT_tools_active._tools_annotate,
    ]

    global hidden_brush_tools
    hidden_brush_tools = tools

def get_hidden_brush_tools() -> Dict[str, ToolDef]:
    global hidden_brush_tools
    return hidden_brush_tools


def register():
    if 'SCULPT' in VIEW3D_PT_tools_active._tools:
        set_sculpt_tools()

    #bpy.utils.register_tool(MyTool, after={"builtin_brush.Draw"}, separator=True)

def unregister():
    #bpy.utils.unregister_tool(MyTool)
    pass
