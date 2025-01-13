from bpy.types import Context, UILayout


def section(layout: UILayout, title: str, icon: str = 'NONE', align: bool = False) -> tuple[UILayout, UILayout]:
        main = layout.column(align=True)
        header = main.box().row(align=align)
        header.label(text=title,
                     icon=icon if isinstance(icon, str) else 'NONE',
                     icon_value=icon if isinstance(icon, int) else 0)
        # header.scale_y = 0.85
        content = main.box().column(align=align)
        return header, content


def section_dropdown(layout: UILayout, data, attr: str, title: str, icon: str = None, align: bool = False) -> tuple[UILayout, UILayout]:
    main = layout.column(align=True)
    if icon:
        header = main.row(align=align)
        header.box().label(
            text='',
            icon=icon if isinstance(icon, str) else 'NONE',
            icon_value=icon if isinstance(icon, int) else 0)
        header = header.box().row(align=align)
    else:
        header = main.box().row(align=align)
    header.prop(data, attr, text=title, icon='DOWNARROW_HLT' if getattr(data, attr) else 'RIGHTARROW', emboss=False)
    if getattr(data, attr):
        content = main.box().column(align=align)
    else:
        content = None
    return header, content
