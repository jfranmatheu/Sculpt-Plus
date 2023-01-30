from ctypes import POINTER, Structure, c_bool, c_char, c_char_p, c_double, c_float, c_int, c_longlong, c_wchar_p, c_short, c_byte, c_uint, sizeof, cast, byref, c_void_p
from enum import IntEnum, Enum


##############################################################
# TYPES
##############################################################

c_float_p = POINTER(c_float)
c_int_p = POINTER(c_int)
c_byte_p = POINTER(c_byte)
c_bool_p = POINTER(c_bool)


##############################################################
# CONVERSION
##############################################################

def to_cy_string(_string: str) -> c_wchar_p:
    return c_wchar_p(_string)

def to_cy_array_float(_list: list, ret_size: bool = False, size: int = 0):
    if _list == None:
        if ret_size:
            return None, c_int(0)
        else:
            return None
    if not size:
        size = len(_list)
    clist = (c_float * size)( * _list)
    if ret_size:
        return (c_float_p(clist), c_int(size))
    return c_float_p(clist)

def to_cy_array_int(_list: list, ret_size: bool = False, size: int = 0):
    if not size:
        size = len(_list)
    clist = (c_int * size)( * _list)
    if ret_size:
        return c_int_p(clist), c_int(size)
    return c_int_p(clist)

def to_cy_array_byte(_list: list, ret_size: bool = False, size: int = 0):
    if not size:
        size = len(_list)
    clist = (c_byte * size)( * _list)
    if ret_size:
        return (c_byte_p(clist), c_int(size))
    return c_byte_p(clist)


class ConvertTo(Enum):
    STRING = to_cy_string
    ARRAY_FLOAT = to_cy_array_float
    ARRAY_INT = to_cy_array_int
    ARRAY_BYTE = to_cy_array_byte

    INT = c_int
    FLOAT = c_float
    BYTE = c_byte
    BOOL = c_bool

    def __call__(self, input: str or list or tuple or bool, *args) -> c_wchar_p or c_float_p or c_int_p or c_byte_p or c_bool or c_int or c_float or c_byte:
        return self.value(input, *args)


##############################################################
# CONSTANTS.
##############################################################

UI_MAX_NAME_STR = 128


##############################################################
# STRUCT UTILS.
##############################################################

class EnumerationType(type(c_uint)):
    def __new__(metacls, name, bases, dict):
        if not "_members_" in dict:
            _members_ = {}
            for key,value in dict.items():
                if not key.startswith("_"):
                    _members_[key] = value
            dict["_members_"] = _members_
        cls = type(c_uint).__new__(metacls, name, bases, dict)
        for key,value in cls._members_.items():
            globals()[key] = value
        return cls

    def __contains__(self, value):
        return value in self._members_.values()

    def __repr__(self):
        return "<Enumeration %s>" % self.__name__

class Enumeration(c_uint):
    __metaclass__ = EnumerationType
    _members_ = {}
    def __init__(self, value):
        for k,v in self._members_.items():
            if v == value:
                self.name = k
                break
        else:
            raise ValueError("No enumeration member with value %r" % value)
        c_uint.__init__(self, value)
        

    @classmethod
    def from_param(cls, param):
        if isinstance(param, Enumeration):
            if param.__class__ != cls:
                raise ValueError("Cannot mix enumeration members")
            else:
                return param
        else:
            return cls(param)

    def __repr__(self):
        return "<member %s=%d of %r>" % (self.name, self.value, self.__class__)


##############################################################
# STRUCT DEFINITIONS.
##############################################################
'''
/** integer rectangle. */
typedef struct rcti {
  int xmin, xmax;
  int ymin, ymax;
} rcti;

/** float rectangle. */
typedef struct rctf {
  float xmin, xmax;
  float ymin, ymax;
} rctf;
'''

class CY_rect:
    @property
    def size_x(self):
        return self.xmax - self.xmin

    @property
    def size_y(self):
        return self.ymax - self.ymin

    @property
    def size(self) -> tuple:
        return self.size_x, self.size_y

class CY_recti(CY_rect, Structure):
    _fields_ = [
        ('xmin', c_int),
        ('xmax', c_int),
        ('ymin', c_int),
        ('ymax', c_int)
    ]

class CY_rectf(CY_rect, Structure):
    _fields_ = [
        ('xmin', c_float),
        ('xmax', c_float),
        ('ymin', c_float),
        ('ymax', c_float)
    ]

class CY_ListBase(Structure):
    _fields_ = [
        ('first', c_void_p), # POINTER(ListBase)),
        ('last', c_void_p), # POINTER(ListBase)),
    ]

'''
enum uiItemType {
  ITEM_BUTTON,

  ITEM_LAYOUT_ROW,
  ITEM_LAYOUT_COLUMN,
  ITEM_LAYOUT_COLUMN_FLOW,
  ITEM_LAYOUT_ROW_FLOW,
  ITEM_LAYOUT_GRID_FLOW,
  ITEM_LAYOUT_BOX,
  ITEM_LAYOUT_ABSOLUTE,
  ITEM_LAYOUT_SPLIT,
  ITEM_LAYOUT_OVERLAP,
  ITEM_LAYOUT_RADIAL,

  ITEM_LAYOUT_ROOT
#if 0
      TEMPLATE_COLUMN_FLOW,
  TEMPLATE_SPLIT,
  TEMPLATE_BOX,

  TEMPLATE_HEADER,
  TEMPLATE_HEADER_ID,
#endif
};
'''
class uiItemType():
    ITEM_BUTTON = 0

    ITEM_LAYOUT_ROW = 1
    ITEM_LAYOUT_COLUMN = 2
    ITEM_LAYOUT_COLUMN_FLOW = 3
    ITEM_LAYOUT_ROW_FLOW = 4
    ITEM_LAYOUT_GRID_FLOW = 5
    ITEM_LAYOUT_BOX = 6
    ITEM_LAYOUT_ABSOLUTE = 7
    ITEM_LAYOUT_SPLIT = 8
    ITEM_LAYOUT_OVERLAP = 9
    ITEM_LAYOUT_RADIAL = 10

    ITEM_LAYOUT_ROOT = 11

'''
typedef enum eUIEmbossType {
  UI_EMBOSS = 0,          /* use widget style for drawing */
  UI_EMBOSS_NONE = 1,     /* Nothing, only icon and/or text */
  UI_EMBOSS_PULLDOWN = 2, /* Pull-down menu style */
  UI_EMBOSS_RADIAL = 3,   /* Pie Menu */
  /**
   * The same as #UI_EMBOSS_NONE, unless the button has
   * a coloring status like an animation state or red alert.
   */
  UI_EMBOSS_NONE_OR_STATUS = 4,

  UI_EMBOSS_UNDEFINED = 255, /* For layout engine, use emboss from block. */
} eUIEmbossType;
'''
class uiEmbossType():
    UI_EMBOSS = 0,          # use widget style for drawing
    UI_EMBOSS_NONE = 1,     # Nothing, only icon and/or text
    UI_EMBOSS_PULLDOWN = 2, # Pull-down menu style
    UI_EMBOSS_RADIAL = 3,   # Pie Menu
    '''
    * The same as #UI_EMBOSS_NONE, unless the button has
    * a coloring status like an animation state or red alert.
    '''
    UI_EMBOSS_NONE_OR_STATUS = 4,

    UI_EMBOSS_UNDEFINED = 255, # For layout engine, use emboss from block.


'''
struct uiItem {
  uiItem *next, *prev;
  uiItemType type;
  int flag;
};
'''
class CY_uiItem(Structure):
    '''
    @property
    def size(self):
        if self.type == uiItemType.ITEM_BUTTON:
            # uiButtonItem *bitem = (uiButtonItem *)item;
            CY_uiButtonItem_p = POINTER(CY_uiButtonItem)
            bitem = cast(byref(self), CY_uiButtonItem_p).contents

            bitem.but.rect
            w = 
    '''
    def to_layout(self) -> 'CY_uiLayout':
        return cast(byref(self), POINTER(CY_uiLayout)).contents

    def next_item(self) -> 'CY_uiItem' or None:
        if self.next <= 0:
            return None
        return CY_uiItem.from_address(self.next)

    _fields_ = [
        ('next', c_void_p), # POINTER(CY_uiItem)),
        ('prev', c_void_p), # POINTER(CY_uiItem)),
        ('type', c_int), # ENUM # c_short # c_uint
        ('flag', c_int)
    ]

'''
struct uiButtonItem {
  uiItem item;
  uiBut *but;
};
'''
class CY_uiButtonItem(Structure):
    _fields_ = [
        ('item', CY_uiItem),
        ('but', c_longlong) # POINTER(CY_uiBut))
    ]

'''
struct uiLayout {
  uiItem item;

  uiLayoutRoot *root;
  bContextStore *context;
  uiLayout *parent;
  ListBase items;

  char heading[UI_MAX_NAME_STR];

  /** Sub layout to add child items, if not the layout itself. */
  uiLayout *child_items_layout;

  int x, y, w, h;
  float scale[2];
  short space;
  bool align;
  bool active;
  bool active_default;
  bool activate_init;
  bool enabled;
  bool redalert;
  bool keepaspect;
  /** For layouts inside grid-flow, they and their items shall never have a fixed maximal size. */
  bool variable_size;
  char alignment;
  eUIEmbossType emboss;
  /** for fixed width or height to avoid UI size changes */
  float units[2];
};
'''
class CY_uiLayout(Structure):
    x: int
    y: int
    w: int
    h: int

    @property
    def position(self) -> tuple[int, int]:
        return self.x, self.y

    @property
    def size(self) -> tuple[int, int]:
        return self.w, self.h

    @property
    def children_layout(self) -> 'CY_uiLayout' or None:
        if self.child_items_layout == 0:
            return None
        return CY_uiLayout.from_address(self.child_items_layout)

    @property
    def children(self) -> list['CY_uiLayout']:
        if self.items is None:
            return []
        children = []
        layout_size = sizeof(CY_uiLayout)
        next_item = self.items.first
        last_item = self.items.last
        while next_item < last_item:
            children.append(
                CY_uiItem.from_address(next_item))
            next_item += layout_size
        children.append(
            CY_uiItem.from_address(last_item))
        #print(children)
        return children


    _fields_ = [
        ('item', CY_uiItem), # not pointer, just the struct.
        ('root', c_longlong), # uiLayoutRoot
        ('context', c_longlong), # bContextStore
        ('parent', c_longlong), # uiLayout
        ('items', CY_ListBase), # not pointer, just the struct.
        ('heading', c_char * UI_MAX_NAME_STR),
        # Sub layout to add child items, if not the layout itself.
        ('child_items_layout', c_longlong), # uiLayout
        ('x', c_int),
        ('y', c_int),
        ('w', c_int),
        ('h', c_int),
        ('scale', c_float * 2),
        ('space', c_short),
        ('align', c_bool),
        ('active', c_bool),
        ('active_default', c_bool),
        ('activate_init', c_bool),
        ('enabled', c_bool),
        ('redalert', c_bool),
        ('keepaspect', c_bool),
        # For layouts inside grid-flow, they and their items shall never have a fixed maximal size.
        ('variable_size', c_bool),
        ('alignment', c_char),
        ('emboss', c_int), # c_short
        # for fixed width or height to avoid UI size changes */
        ('units', c_float * 2)
    ]

######################################
# AREGION

'''
/** View 2D data - stored per region. */
typedef struct View2D {
  /** Tot - area that data can be drawn in; cur - region of tot that is visible in viewport. */
  rctf tot, cur;
  /** Vert - vertical scroll-bar region; hor - horizontal scroll-bar region. */
  rcti vert, hor;
  /** Mask - region (in screen-space) within which 'cur' can be viewed. */
  rcti mask;

  /** Min/max sizes of 'cur' rect (only when keepzoom not set). */
  float min[2], max[2];
  /** Allowable zoom factor range (only when (keepzoom & V2D_LIMITZOOM)) is set. */
  float minzoom, maxzoom;

  /** Scroll - scroll-bars to display (bit-flag). */
  short scroll;
  /** Scroll_ui - temp settings used for UI drawing of scrollers. */
  short scroll_ui;

  /** Keeptot - 'cur' rect cannot move outside the 'tot' rect? */
  short keeptot;
  /** Keepzoom - axes that zooming cannot occur on, and also clamp within zoom-limits. */
  short keepzoom;
  /** Keepofs - axes that translation is not allowed to occur on. */
  short keepofs;

  /** Settings. */
  short flag;
  /** Alignment of content in totrect. */
  short align;

  /** Storage of current winx/winy values, set in UI_view2d_size_update. */
  short winx, winy;
  /** Storage of previous winx/winy values encountered by UI_view2d_curRect_validate(),
   * for keepaspect. */
  short oldwinx, oldwiny;

  /** Pivot point for transforms (rotate and scale). */
  short around;

  /* Usually set externally (as in, not in view2d files). */
  /** Alpha of vertical and horizontal scroll-bars (range is [0, 255]). */
  char alpha_vert, alpha_hor;
  char _pad[6];

  /* animated smooth view */
  struct SmoothView2DStore *sms;
  struct wmTimer *smooth_timer;
} View2D;'''

class CY_SmoothView2DStore(Structure):
    _fields_ = [
        ('orig_cur', CY_rectf),
        ('new_rect', CY_rectf),
        ('time_allowed', c_double)
    ]

class CY_View2D(Structure):
    _fields_ = [
        ('tot', CY_rectf),
        ('cur', CY_rectf),
        ('vert', CY_recti),
        ('hor', CY_recti),
        ('mask', CY_recti),
        ('min', c_float * 2),
        ('max', c_float * 2),
        ('minzoom', c_float),
        ('maxzoom', c_float),
        ('scroll', c_short),
        ('scroll_ui', c_short),
        ('keeptot', c_short),
        ('keepzoom', c_short),
        ('keepofs', c_short),
        ('flag', c_short),
        ('align', c_short),
        ('winx', c_short),
        ('winy', c_short),
        ('oldwinx', c_short),
        ('oldwiny', c_short),
        ('around', c_short),
        ('alpha_vert', c_char),
        ('alpha_hor', c_char),
        ('_pad', c_char * 6),
        ('sms', POINTER(CY_SmoothView2DStore)),
        ('smooth_timer', c_longlong) # POINTER(wmTimer)
    ]


'''
typedef struct ARegion_Runtime {
  /* Panel category to use between 'layout' and 'draw'. */
  const char *category;

  /**
   * The visible part of the region, use with region overlap not to draw
   * on top of the overlapping regions.
   *
   * Lazy initialize, zero'd when unset, relative to #ARegion.winrct x/y min. */
  rcti visible_rect;

  /* The offset needed to not overlap with window scroll-bars. Only used by HUD regions for now. */
  int offset_x, offset_y;

  /* Maps uiBlock->name to uiBlock for faster lookups. */
  struct GHash *block_name_map;
} ARegion_Runtime;
'''
class CY_ARegion_Runtime(Structure):
    _fields_ = [
        ('category', c_char_p),
        ('visible_rect', CY_recti),
        ('offset_x', c_int),
        ('offset_y', c_int),
        ('block_name_map', c_longlong) # POINTER(GHash)
    ]


'''
typedef struct ARegion {
  struct ARegion *next, *prev;

  /** 2D-View scrolling/zoom info (most regions are 2d anyways). */
  View2D v2d;
  /** Coordinates of region. */
  rcti winrct;
  /** Runtime for partial redraw, same or smaller than winrct. */
  rcti drawrct;
  /** Size. */
  short winx, winy;

  /** Region is currently visible on screen. */
  short visible;
  /** Window, header, etc. identifier for drawing. */
  short regiontype;
  /** How it should split. */
  short alignment;
  /** Hide, .... */
  short flag;

  /** Current split size in unscaled pixels (if zero it uses regiontype).
   * To convert to pixels use: `UI_DPI_FAC * region->sizex + 0.5f`.
   * However to get the current region size, you should usually use winx/winy from above, not this!
   */
  short sizex, sizey;

  /** Private, cached notifier events. */
  short do_draw;
  /** Private, cached notifier events. */
  short do_draw_paintcursor;
  /** Private, set for indicate drawing overlapped. */
  short overlap;
  /** Temporary copy of flag settings for clean full-screen. */
  short flagfullscreen;

  /** Callbacks for this region type. */
  struct ARegionType *type;

  /** #uiBlock. */
  ListBase uiblocks;
  /** Panel. */
  ListBase panels;
  /** Stack of panel categories. */
  ListBase panels_category_active;
  /** #uiList. */
  ListBase ui_lists;
  /** #uiPreview. */
  ListBase ui_previews;
  /** #wmEventHandler. */
  ListBase handlers;
  /** Panel categories runtime. */
  ListBase panels_category;

  /** Gizmo-map of this region. */
  struct wmGizmoMap *gizmo_map;
  /** Blend in/out. */
  struct wmTimer *regiontimer;
  struct wmDrawBuffer *draw_buffer;

  /** Use this string to draw info. */
  char *headerstr;
  /** XXX 2.50, need spacedata equivalent? */
  void *regiondata;

  ARegion_Runtime runtime;
} ARegion;'''

class CY_ARegion(Structure):
    @property
    def size(self) -> tuple[int, int]:
        return self.sizex, self.sizey

    def resize_x(self, width) -> None:
        self.sizex = width

    def resize_y(self, height) -> None:
        self.sizey = height

    @property
    def size_win(self) -> tuple[int, int]:
        return self.winx, self.winy

    @property
    def size_view2d(self) -> tuple[int, int]:
        return self.v2d.cur.size

    @property
    def view2d_scroll(self) -> int:
        return self.v2d.scroll

    _fields_ = [
        ('next', c_longlong), # ARegion
        ('prev', c_longlong), # ARegion
        ('v2d', CY_View2D),
        ('winrct', CY_recti),
        ('drawrct', CY_recti),
        ('winx', c_short),
        ('winy', c_short),
        ('visible', c_short),
        ('regiontype', c_short),
        ('alignment', c_short),
        ('flag', c_short),
        # Current split size in unscaled pixels (if zero it uses regiontype).
        #    To convert to pixels use: `UI_DPI_FAC * region->sizex + 0.5f`.
        #    However to get the current region size, you should usually use winx/winy from above, not this! '''
        ('sizex', c_short),
        ('sizey', c_short),
        ('do_draw', c_short),
        ('do_draw_paintcursor', c_short),
        ('overlap', c_short),
        ('flagfullscreen', c_short),
        ('type', c_longlong), # POINTER(ARegionType)
        ('uiblocks', CY_ListBase),
        ('panels', CY_ListBase),
        ('panels_category_active', CY_ListBase),
        ('ui_lists', CY_ListBase),
        ('ui_previews', CY_ListBase),
        ('handlers', CY_ListBase),
        ('panels_category', CY_ListBase),
        ('gizmo_map', c_longlong), # POINTER(wmGizmoMap)
        ('regiontimer', c_longlong), # POINTER(wmTimer)
        ('draw_buffer', c_longlong), # POINTER(wmDrawBuffer)
        ('headerstr', c_char),
        ('runtime', CY_ARegion_Runtime) # ARegion_Runtime
    ]



######################################

class CyBlStruct(Enum):
    _UI_ITEM = CY_uiItem
    _UI_LAYOUT = CY_uiLayout
    _UI_REGION = CY_ARegion

    @classmethod
    def UI_LAYOUT(cls, bl_struct) -> CY_uiLayout:
        return cls._UI_LAYOUT(bl_struct)

    @classmethod
    def UI_ITEM(cls, bl_struct) -> CY_uiItem:
        return cls._UI_ITEM(bl_struct)

    @classmethod
    def UI_REGION(cls, bl_struct) -> CY_ARegion:
        return cls._UI_REGION(bl_struct)

    def __call__(self, bl_struct):
        return self.value.from_address(bl_struct.as_pointer())
