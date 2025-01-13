from enum import Enum

from bpy.types import WindowManager as WM, UILayout, Context

from ...globals import GLOBALS
from ..._auto_code_gen.icons import IconsEnum

booleans_to_register = {}
wm_path = f"{GLOBALS.ADDON_MODULE_SHORT.lower()}_ui_panels"


def new_custom_panel(panel_title: str | tuple[callable, str], icon: str | int = 'NONE', default_closed: bool = False, align_left: bool = False, draw_header: callable = None, flags: set[str] = set()):

    if isinstance(panel_title, tuple):
        _panel_title = panel_title[1]
    else:
        _panel_title = panel_title

    prop_name = f"show_{_panel_title.replace(' ', '_').replace('-', '_').lower()}"
    booleans_to_register[prop_name] = {
        'name': _panel_title,
        'description': f"Disclose {_panel_title} panel",
        'default': not default_closed
    }
    use_icon = icon not in {'NONE', 0}
    # Formating E x a m p l e:
    # header_label = ' '.join(_panel_title)
    # without format:
    header_label = _panel_title

    def wrapper(func):
        def inner(context: Context, layout: UILayout, **kwargs: dict):
            global wm_path
            panel_toggles = getattr(context.window_manager, wm_path)
            disclosed = getattr(panel_toggles, prop_name)
            col = layout.column(align=True)

            if use_icon:
                header = col.row(align=True)
                header.box().prop(
                    panel_toggles,
                    prop_name,
                    text='',
                    icon=icon if isinstance(icon, str) else 'NONE',
                    icon_value=icon if isinstance(icon, int) else icon.icon_id if isinstance(icon, IconsEnum) else 0,
                    emboss=False
                )
            else:
                header = col.box().row(align=True)
            header.scale_y = 0.9
            if use_icon:
                header = header.box().row(align=True)

            if isinstance(panel_title, tuple):
                # Formating E x a m p l e:
                # header_text = ' '.join(panel_title[0](context))
                # without format:
                header_text = header_label
            else:
                header_text = header_label

            if align_left:
                row = header.row(align=True)
                row.ui_units_x = 1.5
                row.prop(
                    panel_toggles,
                    prop_name,
                    text='',
                    icon='DOWNARROW_HLT' if disclosed else 'RIGHTARROW',
                    emboss=False)
                header.label(text=header_text)
            else:
                header.prop(
                    panel_toggles,
                    prop_name,
                    text=header_text,
                    icon='DOWNARROW_HLT' if disclosed else 'RIGHTARROW',
                    emboss=False)

            # print(dir(func.__code__))

            if draw_header is not None:
                draw_header(context, header)

            if disclosed:
                if 'NO_BOX' in flags:
                    content = col.column(align=True)
                else:
                    content = col.box().column()
                content.use_property_decorate = False
                content.use_property_split = True
                func(context, header, content, **kwargs)

            layout.separator(factor=0.5)

        return inner

    return wrapper


def register_pre():
    from ..reg_decorators import RegDeco
    from ..property_types import PropertyTypes

    RegDeco.PROP_GROUP.ROOT.WINDOW_MANAGER(wm_path)(type(
        f"{GLOBALS.ADDON_MODULE_SHORT}_ui_panel_toggles",
        (),
        {
            '__annotations__': {
                prop_name: PropertyTypes.BOOL(**prop_kwargs)
                for prop_name, prop_kwargs in booleans_to_register.items()
            }
        }
    ))
