from bpy.types import UILayout

from sculpt_plus.props import Props
from sculpt_plus.previews import Previews
from sculpt_plus.prefs import get_prefs

from sculpt_plus.core.data.cy_structs import CyBlStruct


def _draw_mask_filters(content: UILayout, only_icons: bool = False, align: bool = True, scale_y: float = 1):
    grid = content.grid_flow(align=align, even_columns=True, even_rows=True, row_major=True, columns=0 if only_icons else 2)
    grid.scale_y = scale_y

    grid.operator('sculpt.mask_filter', text='' if only_icons else "Smooth", icon_value=Previews.Mask.SMOOTH()).filter_type = 'SMOOTH'
    grid.operator('sculpt.mask_filter', text='' if only_icons else "Sharpen", icon_value=Previews.Mask.SHARP()).filter_type = 'SHARPEN'
    grid.operator('sculpt.mask_filter', text='' if only_icons else "Grow", icon_value=Previews.Mask.GROW()).filter_type = 'GROW'
    grid.operator('sculpt.mask_filter', text='' if only_icons else "Shrink", icon_value=Previews.Mask.SHRINK()).filter_type = 'SHRINK'
    grid.operator('sculpt.mask_filter', text='' if only_icons else "Contrast +", icon_value=Previews.Mask.CONTRAST_UP()).filter_type = 'CONTRAST_INCREASE'
    grid.operator('sculpt.mask_filter', text='' if only_icons else "Contrast -", icon_value=Previews.Mask.CONTRAST_DOWN()).filter_type = 'CONTRAST_DECREASE'


def _draw_mask_expand(content: UILayout, use_mask_preserve: bool, invert: bool, use_reposition_pivot: bool = True, align=False, scale_y: float = 1):
    expand_methods = (
        ('TOPOLOGY', {'icon': 'MONKEY'}),
        ('NORMALS', {'icon': 'SNAP_NORMAL'}),
        ('TOPOLOGY_DIAGONALS', {'icon': 'MONKEY'}),
        ('GEODESIC', {'icon': 'MESH_ICOSPHERE'}),
        ('BOUNDARY_TOPOLOGY', {'icon': 'OVERLAY'}),
        ('SPHERICAL', {'icon': 'MESH_UVSPHERE'}),
    )
    grid = content.grid_flow(align=align, even_columns=True, even_rows=True, row_major=True, columns=2)
    grid.scale_y = scale_y
    
    for (falloff_type, draw_props) in expand_methods:
        mask_op = grid.operator('sculpt.expand', text=falloff_type.replace('_', ' ').title(), **draw_props)
        mask_op.target = 'MASK'
        mask_op.falloff_type = falloff_type
        mask_op.use_reposition_pivot  = use_reposition_pivot
        mask_op.use_mask_preserve  = use_mask_preserve
        mask_op.invert = invert


def _draw_mask_effects(content, align: bool = False):
    row = content.row(align=align)
    row.operator('sculpt.mask_init', icon_value=Previews.Mask.RANDOM(), text="Random").mode = 'RANDOM_PER_VERTEX'
    row.operator('sculpt.mask_from_cavity', icon_value=Previews.Mask.CAVITY(), text="Cavity").settings_source = 'OPERATOR'


def _draw_mask_to_mesh(content, align: bool = False):
    row = content.row(align=align)
    row.operator('mesh.paint_mask_extract', icon_value=Previews.Mask.EXTRACT())
    row.operator('mesh.paint_mask_slice', icon_value=Previews.Mask.SLICE()) # sculpt_plus.mask_slice_wrapper # (mask_threshold=0.5, fill_holes=True, new_object=True)


def draw_mask(layout: UILayout, context):
    layout.use_property_decorate = False

    scene_props = Props.Scene(context)
    use_front_faces_only = scene_props.mask_op_use_front_faces_only
    use_mask_preserve = not scene_props.mask_op_clear_previous_mask
    invert_mask = scene_props.mask_op_invert
    use_reposition_pivot = scene_props.mask_op_use_reposition_pivot

    prefs = get_prefs(context)
    # TODO: Make the use mask tabs workaroudn better here below...

    row = layout.row()
    row.scale_y = 1.25
    mask_op = row.operator('paint.mask_flood_fill', text="Fill", icon_value=Previews.Main.FILL())
    mask_op.mode = 'VALUE'
    mask_op.value = 1
    mask_op = row.operator('paint.mask_flood_fill', text="Clear", icon_value=Previews.Mask.CLEAR())
    mask_op.mode = 'VALUE'
    mask_op.value = 0
    row.operator('paint.mask_flood_fill', text="Invert", icon_value=Previews.Mask.INVERT()).mode = 'INVERT'

    mask_tool_col = layout.column()

    row = mask_tool_col.split(factor=0.37, align=True)
    tag = row.box()
    tag.scale_y = 0.5
    tag.label(text="Box Tool")#, icon_value=Previews.Mask.BOX())
    mask_tool = row.operator('paint.mask_box_gesture', text="Fill")
    mask_tool.mode = 'VALUE'
    mask_tool.value = 0
    mask_tool.use_front_faces_only = use_front_faces_only
    mask_tool = row.operator('paint.mask_box_gesture', text="Clear")
    mask_tool.mode = 'VALUE'
    mask_tool.value = 1
    mask_tool.use_front_faces_only = use_front_faces_only
    mask_tool = row.operator('paint.mask_box_gesture', text="Invert")
    mask_tool.mode = 'INVERT'
    mask_tool.use_front_faces_only = use_front_faces_only

    row = mask_tool_col.split(factor=0.37, align=True)
    tag = row.box()
    tag.scale_y = 0.5
    tag.label(text="Lasso Tool")#, icon_value=Previews.Mask.LASSO())
    mask_tool = row.operator('paint.mask_lasso_gesture', text="Fill")
    mask_tool.mode = 'VALUE'
    mask_tool.value = 1
    mask_tool.use_front_faces_only = use_front_faces_only
    mask_tool = row.operator('paint.mask_lasso_gesture', text="Clear")
    mask_tool.mode = 'VALUE'
    mask_tool.value = 0
    mask_tool.use_front_faces_only = use_front_faces_only
    mask_tool = row.operator('paint.mask_lasso_gesture', text="Invert")
    mask_tool.mode = 'INVERT'
    mask_tool.use_front_faces_only = use_front_faces_only

    row = mask_tool_col.row()
    row.use_property_split = True
    row.prop(scene_props, 'mask_op_use_front_faces_only', text="Front Faces Only")

    if prefs.toolbar_panel_mask_layout == 'COMPACT':
        main_col = mask_tool_col.column(align=True)

        def _compact_section(title: str, icon: str = 'NONE', header_inject = None) -> UILayout:
            col = main_col.column(align=True)
            box = col.box().row(align=False)
            box.scale_y = 0.66
            box.alignment = 'EXPAND'
            box.label(text='\t'+title, icon=icon)
            if header_inject is not None:
                header_inject(box)
            return col

        def _draw_expand_toggles(layout):
            toggles = layout.row(align=True)
            toggles.scale_x = 1.2
            toggles.prop(scene_props, 'mask_op_clear_previous_mask', text="", icon_value=Previews.Mask.CLEAR())
            toggles.prop(scene_props, 'mask_op_invert', text="", icon_value=Previews.Mask.INVERT())
            toggles.prop(scene_props, 'mask_op_use_reposition_pivot', text="", icon='PIVOT_BOUNDBOX')

        _draw_mask_filters(_compact_section("Mask Filters"), only_icons=False, scale_y=1.0)
        _draw_mask_expand(_compact_section("Mask Expand", header_inject=_draw_expand_toggles), use_mask_preserve, invert_mask, use_reposition_pivot, align=True)
        _draw_mask_effects(_compact_section("Mask Generator"), align=True)
        _draw_mask_to_mesh(_compact_section("Mask to Mesh"), align=True)

        return

    use_mask_tabs: bool = prefs.toolbar_panel_mask_layout == 'TABS'
    if not use_mask_tabs:
        sections_col = mask_tool_col.column(align=True)

    
    ''' MASK FILTERS. '''
    if use_mask_tabs:
        pass
    else:
        filter_col = sections_col.column(align=True)
        header = filter_col.box()
        header.scale_y = 0.8
        header.label(text="M a s k   F i l t e r s :")
        filter_col = filter_col.column(align=True)
        filter_col.scale_y = 1.25
        _draw_mask_filters(filter_col, scale_y=.85)


    ''' MASK EXPAND. '''
    if use_mask_tabs:
        pass
    else:
        sections_col.separator(factor=1.25)
        mask_mod_ops_col = sections_col.column(align=True)
        header = mask_mod_ops_col.box().row()
        header.label(text="M a s k   E x p a n d :")
        header.scale_y = 0.8
        header_toggles = header.row(align=True)
        header_toggles.scale_x = 1.2
        header_toggles.prop(scene_props, 'mask_op_clear_previous_mask', text="", icon_value=Previews.Mask.CLEAR())
        header_toggles.prop(scene_props, 'mask_op_invert', text="", icon_value=Previews.Mask.INVERT())
        header_toggles.prop(scene_props, 'mask_op_use_reposition_pivot', text="", icon='PIVOT_BOUNDBOX')
        mask_mod_ops_col = mask_mod_ops_col.column(align=True)
        mask_mod_ops_col.scale_y = 1.25
        _draw_mask_expand(mask_mod_ops_col.column(align=True), use_mask_preserve, invert_mask, use_reposition_pivot, align=True, scale_y=.85)


    ''' MASK EFFECTS. '''
    if use_mask_tabs:
        pass
    else:
        sections_col.separator(factor=1.25)
        mask_mods_col = sections_col.column(align=True)
        header = mask_mods_col.box()
        header.scale_y = 0.8
        header.label(text="M a s k   G e n e r a t o r :")
        mask_mods_col = mask_mods_col.column(align=True)
        mask_mods_col.scale_y = 1.25
        _draw_mask_effects(mask_mods_col.column(align=True), align=True)


    ''' MASK TO MESH. '''
    if use_mask_tabs:
        pass
    else:
        sections_col.separator(factor=1.25)
        mask_mesh_col = sections_col.column(align=True)
        header = mask_mesh_col.box()
        header.scale_y = 0.8
        header.label(text="M a s k   to   M e s h :")
        mask_mesh_col = mask_mesh_col.column(align=True) #box() #.grid_flow(row_major=True, even_columns=True, even_rows=True, columns=2)
        mask_mesh_col.scale_y = 1.25
        _draw_mask_to_mesh(mask_mesh_col, align=True)


    if use_mask_tabs:
        ui_props = Props.UI(context)
        act_mask_tab = ui_props.mask_panel_tabs
        mask_tab = layout.column(align=True)
        mask_tab_selector = mask_tab.row(align=True)
        mask_tab_selector.prop(ui_props, 'mask_panel_tabs', text="Filters", expand=True)
        mask_tab_selector.scale_y = 1.4
        mask_tab_content = mask_tab.box() # .grid_flow(row_major=True, even_columns=True, even_rows=True, columns=2)
        mask_tab_content.scale_y = 1.2
        if act_mask_tab == 'MASK_EXPAND':
            _draw_mask_expand(mask_tab_content.column(), use_mask_preserve, invert_mask, use_reposition_pivot)
        elif act_mask_tab == 'MASK_EFFECTS':
            _draw_mask_effects(mask_tab_content.column())
        elif act_mask_tab == 'MASK_FILTERS':
            _draw_mask_filters(mask_tab_content.column(), align=False)
        elif act_mask_tab == 'MASK_TO_MESH':
            _draw_mask_to_mesh(mask_tab_content.column())


def draw_facesets(layout: UILayout, context):
    ui_props = Props.UI(context)
    scene_props = Props.Scene(context)
    use_front_faces_only = scene_props.facesets_op_use_front_faces_only

    #split = layout.split(align=True, factor=0.25)
    #split.prop_tabs_enum(ui_props, 'mask_panel_tabs', icon_only=True)
    layout = layout.column()

    def _sub(title: str, icon: str ='NONE', toggle_prop: str = None, columns: int = 2, align: bool = True, use_content_box: bool = False, scale_y=1.25):
        layout.separator(factor=0.4)
        sub = layout.column(align=True)
        header = sub.box().row(align=True)
        header.scale_y = 0.8
        if toggle_prop is None:
            header.label(text=title, icon=icon)
        else:
            #header = header.row(align=True)
            header.alignment = 'LEFT'
            toggle_value = getattr(ui_props, toggle_prop)
            header.prop(ui_props, toggle_prop, text=title, icon='TRIA_DOWN' if toggle_value else 'TRIA_RIGHT', emboss=False)
            if not toggle_value:
                return header, None
        if use_content_box:
            sub = sub.box()
        if columns is not None:
            content = sub.grid_flow(align=align, columns=columns, even_columns=True, even_rows=True, row_major=True)
        else:
            content = sub
        content.scale_y = scale_y
        return header, content

    layout.operator('sculpt.face_sets_randomize_colors', text="Random Colors")
    layout.separator(factor=0.5)

    header, content = _sub("T o o l s :", icon='TOOL_SETTINGS', align=True, use_content_box=False, columns=2, )
    toggles = header.row(align=True)
    toggles.scale_x = 1.2
    toggles.prop(scene_props, 'facesets_op_use_front_faces_only', text='', icon_value=Previews.Main.FRONT_FACES())
    content.operator('sculpt_plus.select_tool__face_set_edit', text="Grow", icon_value=Previews.FaceSets.GROW()).mode='GROW'
    content.operator('sculpt_plus.select_tool__face_set_edit', text="Shrink", icon_value=Previews.FaceSets.SHRINK()).mode='SHRINK'
    content.operator('sculpt.face_set_box_gesture', text="Box Tool", icon_value=Previews.FaceSets.BOX()).use_front_faces_only = use_front_faces_only
    content.operator('sculpt.face_set_lasso_gesture', text="Lasso Tool", icon_value=Previews.FaceSets.LASSO()).use_front_faces_only = use_front_faces_only

    header, content = _sub("V i s i b i l i t y :", icon='CAMERA_STEREO', align=True, use_content_box=False, columns=2)
    content.operator('sculpt.reveal_all', text='Reveal All', icon='HIDE_OFF')
    content.operator('sculpt.face_set_change_visibility', text='Isolate', icon='HOLDOUT_ON').mode='TOGGLE'

    header, content = _sub("C r e a t e   F a c e - S e t   f r o m ...", toggle_prop='show_facesets_panel_createfrom_section')
    if content:
        content.operator('sculpt.face_sets_create', text="Mask", icon='MOD_MASK').mode='MASKED'
        content.operator('sculpt.face_sets_create', text="Visible", icon='HIDE_OFF').mode='VISIBLE'
        content.operator('sculpt.face_sets_create', text="EditMode Selection", icon='RESTRICT_SELECT_OFF').mode='SELECTION'
    # box = content.box()

    header, content = _sub("I n i t   F a c e - S e t s   B y ...", toggle_prop='show_facesets_panel_initialize_section', columns=2, scale_y=1)
    if content:
        content.operator('sculpt.face_sets_init', text="Loose Parts", icon='GP_CAPS_FLAT').mode='LOOSE_PARTS'
        content.operator('sculpt.face_sets_init', text="Materials", icon='MATERIAL').mode='MATERIALS'
        content.operator('sculpt.face_sets_init', text="Normals", icon='ORIENTATION_NORMAL').mode='NORMALS'
        #-
        content.operator('sculpt.face_sets_init', text="FaceSet Boundaries", icon='CLIPUV_DEHLT').mode='FACE_SET_BOUNDARIES'
        content.operator('sculpt.face_sets_init', text="Face Maps", icon='FACE_MAPS').mode='FACE_MAPS'
        content.operator('sculpt.face_sets_init', text="UV Seams", icon='UV').mode='UV_SEAMS'
        #-
        content.operator('sculpt.face_sets_init', text="Edge Creases", icon='BRUSH_CREASE').mode='CREASES'
        content.operator('sculpt.face_sets_init', text="Bevel Weight", icon='MOD_VERTEX_WEIGHT').mode='BEVEL_WEIGHT'
        content.operator('sculpt.face_sets_init', text="Sharp Edges", icon='SHARPCURVE').mode='SHARP_EDGES'

    header, content = _sub("F a c e  S e t   t o   M e s h :", icon='MESH_GRID', columns=2)
    content.operator('mesh.face_set_extract', text="Extract", icon_value=Previews.Mask.EXTRACT())


def draw_mask_facesets(layout: UILayout, context):
    from sculpt_plus.core.data.wm import SCULPTPLUS_PG_ui_toggles
    ui_props: SCULPTPLUS_PG_ui_toggles = Props.UI(context)

    ui = Props.UI(context)
    active_section: str = ui.toolbar_maskfacesets_sections
    header_label: str = UILayout.enum_item_description(ui, 'toolbar_maskfacesets_sections', active_section)
    header_icon: int = UILayout.enum_item_icon(ui, 'toolbar_maskfacesets_sections', active_section)

    panel = layout.column(align=True)
    header = panel.box()
    # cy_box = CyBlStruct.UI_LAYOUT_BOX(header)
    # print(tuple(cy_box.button.col))
    # cy_box.button.col = (0, 100, 255, 255)
    header = header.row(align=True)
    header.scale_y = 1.5
    _header = header.row(align=True)
    _header.scale_y = .5
    _header.scale_x = .75
    _header.template_icon(icon_value=header_icon, scale=2.0)
    # header.label(text=ui_props.toolbar_maskfacesets_sections.capitalize() + " Options", icon='BRUSH_SOFTEN')
    # header.label(text="", icon='BRUSH_SOFTEN')
    tri_icon = 'TRIA_DOWN' if ui_props.show_mask_facesets_panel else 'TRIA_LEFT'
    header.prop(ui_props, 'show_mask_facesets_panel', expand=True, text=header_label, emboss=False)
    header.prop(ui_props, 'show_mask_facesets_panel', expand=True, text="", icon=tri_icon, emboss=False)

    if not ui_props.show_mask_facesets_panel:
        return

    selector = panel.row(align=True)
    selector.prop(ui_props, 'toolbar_maskfacesets_sections', text="Mask", expand=True)
    selector.scale_y = 1.35
    # selector.ui_units_y = 2

    selector_line_bot = panel.box()#.column(align=True)
    selector_line_bot.ui_units_y = 0.1

    '''
    cy_layout = CyBlStruct.UI_LAYOUT(selector)
    print("Align:", cy_layout.align, "Type:", cy_layout.item.type)
    print("Pos:", cy_layout.position, "Size:", cy_layout.size)
    print("Scale", tuple(cy_layout.scale), "Units:", tuple(cy_layout.units))
    cy_children_layout = cy_layout.children_layout
    if cy_children_layout:
        print("__Children Layout__")
        print("\tAlign:", cy_children_layout.align, "Type:", cy_children_layout.item.type)
        print("\tPos:", cy_children_layout.position, "Size:", cy_children_layout.size)
        print("\tScale", tuple(cy_children_layout.scale))
    for child in cy_layout.children:
        print("__Children__")
        print("\tType:", child.type)
        print("\tSize:", child.to_layout().size)
    '''

    content = panel.box()#.column()
    content.separator(factor=0.1)

    if ui_props.toolbar_maskfacesets_sections == 'MASK':
        draw_mask(content, context)
    elif ui_props.toolbar_maskfacesets_sections == 'FACESETS':
        draw_facesets(content, context)

    #content.separator(factor=0.1)
