from . import Shaders as SH
from gpu.state import blend_set, line_width_set
from gpu_extras.batch import batch_for_shader as bat
from collections import OrderedDict


def widget_params(context, pos, size) -> dict:
    '''
    #define recti parameters[widgetID * MAX_PARAM + 0]
    #define rect parameters[widgetID * MAX_PARAM + 1]
    #define radsi parameters[widgetID * MAX_PARAM + 2].x
    #define rads parameters[widgetID * MAX_PARAM + 2].y
    #define faci parameters[widgetID * MAX_PARAM + 2].zw
    #define roundCorners parameters[widgetID * MAX_PARAM + 3]
    #define colorInner1 parameters[widgetID * MAX_PARAM + 4]
    #define colorInner2 parameters[widgetID * MAX_PARAM + 5]
    #define colorEdge parameters[widgetID * MAX_PARAM + 6]
    #define colorEmboss parameters[widgetID * MAX_PARAM + 7]
    #define colorTria parameters[widgetID * MAX_PARAM + 8]
    #define tria1Center parameters[widgetID * MAX_PARAM + 9].xy
    #define tria2Center parameters[widgetID * MAX_PARAM + 9].zw
    #define tria1Size parameters[widgetID * MAX_PARAM + 10].x
    #define tria2Size parameters[widgetID * MAX_PARAM + 10].y
    #define shadeDir parameters[widgetID * MAX_PARAM + 10].z
    #define alphaDiscard parameters[widgetID * MAX_PARAM + 10].w
    #define triaType parameters[widgetID * MAX_PARAM + 11].x
    '''
    # udpi = context.preferences.system.dpi
    upixelsize = context.preferences.system.pixel_size
    # pixels_per_inch = udpi * upixelsize

    x, y = pos
    w, h = size
    minx = x
    maxx = x + w
    miny = y
    maxy = y + h
    minxi = minx + upixelsize
    maxxi = maxx - upixelsize
    minyi = miny + upixelsize
    maxyi = maxy - upixelsize

    return [
        # recti
        (minxi, minyi, maxxi, maxyi),
        # rect
        (minx, miny, maxx, maxy),
        # radsi, rads, faci
        (
            1.0 / (maxxi - minxi) if (maxxi != minxi) else 0.0, # facix
            1.0 / (maxxi - minxi) if (maxxi != minxi) else 0.0  # faciy
        )
        # roundCorners
        # colorInner1
        (.11, .11, .11, .5),
        # colorInner2
        (.11, .11, .11, .5),
        # colorEdge
        (.24, .24, .24, 1.0),
        # colorEmboss
        (.28, .28, .28, 1.0),
        # colorTria
        (.15, .15, .15, 1.0),
        # tria1Center, tria2Center
        # tria1Size, tria2Size, shadeDir, alphaDiscard
        # triaType
    ]


def DiWidget(context, id: str, pos: tuple, size: tuple, update: bool = False):
    s = SH.WIDGET_BASE()
    x, y = pos
    w, h = size
    r = 8
    vertices = (
        # Widget. 0-3
        (x, y), (x+w, y), (x, y+h), (x+w, y+h),
        # Trias.
        ## Bottom-Left. 4-6
        (x, y), (x+r, y), (x, y+r),
        ## Bottom-Right. 6-8
    )
    tris_indices = (
        # Widget.
        (0, 1, 2),
        (2, 1, 3),
        # Trias.
        (4, 5, 6),
        (6, 5, 7),
        (8, 9, 10),
        (10, 9, 11)
    )

    wt_params = widget_params(context, pos, size)
    # b = bat(s, 'TRIS', {"pos": })

    blend_set('ALPHA')
    # b.draw(s)
    blend_set('NONE')
