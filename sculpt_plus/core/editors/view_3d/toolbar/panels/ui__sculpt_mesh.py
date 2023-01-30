from bpy.types import UILayout, MultiresModifier, VIEW3D_PT_sculpt_voxel_remesh, VIEW3D_PT_sculpt_dyntopo

from sculpt_plus.utils.modifiers import get_modifier_by_type
from sculpt_plus.props import Props

from ._dummy import DummyPanel


def draw_sculpt_sections(layout: UILayout, context):
    ui = Props.UI(context)
    active_section: str = ui.toolbar_sculpt_sections
    header_label: str = UILayout.enum_item_description(ui, 'toolbar_sculpt_sections', active_section)
    header_icon: int = UILayout.enum_item_icon(ui, 'toolbar_sculpt_sections', active_section)

    section = layout.column(align=True)

    header = section.box().row(align=True)
    header.scale_y = 1.5
    # header.label(text=header_label, icon_value=header_icon)
    #header.label(text="", icon_value=header_icon)
    _header = header.row(align=True)
    _header.scale_y = .5
    _header.scale_x = .75
    _header.template_icon(icon_value=header_icon, scale=2.0)
    tri_icon = 'TRIA_DOWN' if ui.show_sculpt_mesh_panel else 'TRIA_LEFT'
    header.prop(ui, 'show_sculpt_mesh_panel', expand=True, text=header_label, emboss=False)
    header.prop(ui, 'show_sculpt_mesh_panel', expand=True, text="", icon=tri_icon, emboss=False)

    if not ui.show_sculpt_mesh_panel:
        return

    mod = get_modifier_by_type(context.sculpt_object, 'MULTIRES')
    skip_selector = context.sculpt_object.use_dynamic_topology_sculpting or mod is not None 

    if not skip_selector:
        selector = section.grid_flow(align=True, row_major=True, even_columns=True, even_rows=True, columns=0)
        selector.use_property_split = False
        selector.scale_y = 1.4
        selector.prop(ui, 'toolbar_sculpt_sections', text="", expand=True)

    content = section.box().column(align=False)
    if not skip_selector:
        content.separator()
    content.use_property_split = True
    content.use_property_decorate = False
    content_args = (DummyPanel(content), context)

    if active_section == 'VOXEL_REMESH':
        # vox_size = content.column(align=True)
        # vox_size.box().row().label(text="Voxel Size Helpers")
        # vox_size = vox_size.box().column()
        mesh = context.sculpt_object.data
        row = content.row(align=True)
        row.prop(mesh, "remesh_voxel_size")
        props = row.operator("sculpt.sample_detail_size", text="", icon='EYEDROPPER')
        props.mode = 'VOXEL'

        content.prop(mesh, "remesh_voxel_adaptivity")
        if mesh.remesh_voxel_adaptivity == 0:
            content.prop(mesh, "use_remesh_fix_poles")

        vox_size = content.column(align=False)

        _vox_size = vox_size.column(align=True)
        _vox_size.label(text="Increment / Decrement Voxel Size :")
        vox_size_add = _vox_size.row(align=True)
        vox_size_add.label(text="", icon='ADD')
        vox_size_add.operator("sculpt_plus.remesh_voxel_increase_size", text="0.1").value = 0.1
        vox_size_add.operator("sculpt_plus.remesh_voxel_increase_size", text="0.01").value = 0.01
        vox_size_add.operator("sculpt_plus.remesh_voxel_increase_size", text="0.001").value = 0.001
        vox_size_add = _vox_size.row(align=True)
        vox_size_add.label(text="", icon='REMOVE')
        vox_size_add.operator("sculpt_plus.remesh_voxel_increase_size", text="-0.1").value = -0.1
        vox_size_add.operator("sculpt_plus.remesh_voxel_increase_size", text="-0.01").value = -0.01
        vox_size_add.operator("sculpt_plus.remesh_voxel_increase_size", text="-0.001").value = -0.001

        _vox_size = vox_size.column(align=True)
        _vox_size.label(text="Change Voxel Density (in %) :")
        vox_size_add = _vox_size.row(align=True)
        vox_size_add.label(text="", icon='ADD')
        vox_size_add.operator("sculpt_plus.remesh_voxel_increase_density", text="10%").value = 10
        vox_size_add.operator("sculpt_plus.remesh_voxel_increase_density", text="20%").value = 20
        vox_size_add.operator("sculpt_plus.remesh_voxel_increase_density", text="33%").value = 33
        vox_size_add.operator("sculpt_plus.remesh_voxel_increase_density", text="50%").value = 50
        vox_size_add = _vox_size.row(align=True)
        vox_size_add.label(text="", icon='REMOVE')
        vox_size_add.operator("sculpt_plus.remesh_voxel_increase_density", text="-10%").value = -10
        vox_size_add.operator("sculpt_plus.remesh_voxel_increase_density", text="-20%").value = -20
        vox_size_add.operator("sculpt_plus.remesh_voxel_increase_density", text="-33%").value = -33
        vox_size_add.operator("sculpt_plus.remesh_voxel_increase_density", text="-50%").value = -50

        #content.separator()

        #VIEW3D_PT_sculpt_voxel_remesh.draw(*content_args)
        

    elif active_section == 'QUAD_REMESH':
        content.scale_y = 1.5
        content.operator("object.quadriflow_remesh", text="QuadriFlow Remesh")
    elif active_section == 'DYNTOPO':
        if not context.sculpt_object.use_dynamic_topology_sculpting:
            msg = content.box()
            msg.scale_y = 1.5
            msg.label(text="You should enable Dyntopo!", icon='INFO')
            msg.operator("sculpt.dynamic_topology_toggle", text="Enable Dyntopo")
            return
        else:
            settings = VIEW3D_PT_sculpt_dyntopo.paint_settings(context)
            if settings is None:
                msg = content.box()
                msg.scale_y = 1.5
                msg.label(text="Only shown when using a brush.", icon='INFO')
                return
            VIEW3D_PT_sculpt_dyntopo.draw(*content_args)
            content.separator()
            op = content.row()
            op.scale_y = 1.5
            op.alert = True
            op.operator("sculpt.dynamic_topology_toggle", text="Disable Dyntopo")
    else:
        if mod is None:
            msg = content.box()
            msg.scale_y = 1.5
            msg.label(text="No Multires Modifier", icon='INFO')
            msg.operator('object.modifier_add', text="Add Multires Modifier").type = 'MULTIRES'
            return

        draw_sculpt_multires(content, mod)
        # DATA_PT_modifiers.draw(*content_args)

    content.separator(factor=0.1)


def draw_sculpt_multires(layout: UILayout, mod: MultiresModifier):
    layout.use_property_split = False

    levels_layout = layout.column(align=True)
    levels_layout.box().label(text="L e v e l s", icon='ALIASED')
    levels_layout = levels_layout.grid_flow(row_major=True, columns=4, even_columns=True, even_rows=True, align=True)
    levels_layout.scale_y = 1.5
    for i in range(mod.total_levels + 1):
        levels_layout.operator('sculpt_plus.multires_change_level', text=str(i), depress=i==mod.sculpt_levels).level = i

    layout.separator(factor=0.25)

    ops_layout = layout.column(align=True)
    ops_layout.box().label(text='L e v e l   U p !  (Subdivide)', icon='SORT_DESC')
    ops_layout = ops_layout.row(align=True)
    ops_layout.scale_y = 1.5
    op = ops_layout.operator('object.multires_subdivide', text='Smooth')
    op.modifier = mod.name
    op.mode = 'CATMULL_CLARK'
    op = ops_layout.operator('object.multires_subdivide', text='Simple')
    op.modifier = mod.name
    op.mode = 'SIMPLE'
    op = ops_layout.operator('object.multires_subdivide', text='Linear')
    op.modifier = mod.name
    op.mode = 'LINEAR'

    layout.separator(factor=0.25)

    ops_layout = layout.column(align=True)
    ops_layout.box().label(text='L e v e l   D o w n !', icon='SORT_ASC')
    ops_layout = ops_layout.column(align=True)
    ops_layout.operator('object.multires_unsubdivide', text='Rebuild Lower Level from Base Level')
    ops_layout.operator('object.multires_higher_levels_delete', text='Delete Higher Levels from Level ' + str(mod.sculpt_levels))

    layout.separator(factor=0.25)

    ops_layout = layout.column(align=True)
    ops_layout.box().label(text='S h a p e   M o r p h', icon='MONKEY')
    ops_layout = ops_layout.column(align=True)
    ops_layout.operator('object.multires_reshape', text='Reshape')
    ops_layout.operator('object.multires_base_apply', text='Apply Base')

    layout.separator()

    layout.prop(mod, 'use_sculpt_base_mesh')
    # layout.prop(mod, 'show_only_control_edges')

    layout.separator()

    actions = layout.column(align=False) 
    row = actions.split(factor=0.33,align=False)
    row.scale_y = 1.5
    row.operator('sculpt_plus.multires_apply', text="Apply").as_shape_key = False
    row.operator('sculpt_plus.multires_apply', text="Apply as ShapeKey").as_shape_key = False
    actions.separator(factor=0.5)
    row = actions.row()
    row.scale_y = 1.2
    row.alert = True
    row.operator('sculpt_plus.multires_remove', text="Remove")

    #row = content.row()
    #row.scale_y = 1.5
    #row.operator('object.modifier_apply', text="Apply Multires Modifier").modifier = mod.name
