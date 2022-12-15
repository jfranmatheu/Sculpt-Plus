import bpy
from bl_ui.space_toolsystem_toolbar import VIEW3D_PT_tools_active, _defs_transform, _defs_annotate, _defs_sculpt
from bl_ui.space_toolsystem_common import ToolDef, ToolSelectPanelHelper

from typing import List


unregistered_tools: List[ToolDef] = []


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
        if idname not in {'MASK', 'DRAW_FACE_SETS', 'DISPLACEMENT_ERASER', 'DISPLACEMENT_SMEAR', 'SIMPLIFY'}:
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


def set_sculpt_tools():
    tools = generate_from_brushes()
    VIEW3D_PT_tools_active._tools['SCULPT'] = [
        #tools['SCULPT_BRUSH'],
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

def register():
    if 'SCULPT' in VIEW3D_PT_tools_active._tools:
        set_sculpt_tools()

def unregister():
    pass
