from .wg_base import WidgetBase, Vector, SCULPTPLUS_AddonPreferences, Canvas
from .di import DiLine, DiRct, DiText, get_rect_center, DiCage


class WidgetSelector(WidgetBase):
    static_items = ()
    default_item = None
    label = "Select an item"

    active_item: str
    active_index: int

    def load_items(self):
        return ()

    def init(self) -> None:
        self.expanded = False
        self.hovered_index = None
        self.active_item = self.default_item
        self.active_index = -1 if self.default_item is None else self.items.index(self.default_item)
        if self.static_items:
            self.items = self.static_items
        else:
            self.items = self.load_items()

    def update(self, cv: Canvas, prefs: SCULPTPLUS_AddonPreferences) -> None:
        self.item_height = 30 * cv.scale

        if not self.expanded:
            return

        act_idx = max(0, self.active_index)
        tot_rows = len(self.items)
        s_y = tot_rows * self.item_height
        y_off = act_idx * self.item_height

        self.pos = self.pos + Vector((0, y_off - s_y))
        self.size = Vector((self.size.x, s_y))

    '''
    def on_hover(self, m: Vector, p: Vector = None, s: Vector = None) -> bool:
        if self.expanded:
            ret = super().on_hover(m)
            if not ret:
                return False
            #print("Iter items hover item...")
            #self.hovered_index = self.iter_items(self.on_hover_item, m) # self.hovered_index = 
            return True

        return super().on_hover(m, p, s)
    '''

    def on_leftmouse_press(self, ctx, cv: Canvas, m: Vector) -> None:
        return not self.expanded

    def modal_enter(self, ctx, cv: Canvas, m: Vector) -> None:
        print("Start")
        if not self.items:
            self.items = self.load_items()

        self.expanded = True
        self.update(cv, None)

    def confirm(self, ctx, cv: Canvas, m: Vector) -> None:
        if not self.expanded:
            return False
        print(self.hovered_index)
        if self.hovered_index:
            self.active_index = self.hovered_index
            self.active_item = self.items[self.hovered_index]

    def modal_exit(self, ctx, cv: Canvas, m: Vector, cancel: bool = False) -> None:
        print("End")
        if not cancel:
            self.confirm(ctx, cv, m)

        self.hovered_index = None
        self.expanded = False
        self.update(cv, None)

    def iter_items(self, callback: callable, *args, **kwargs):
        '''
        act_idx = self.active_index
        tot_rows = len(self.items)
        s_y = tot_rows * self.item_height
        y_off = act_idx * self.item_height
        p = self.pos.copy()
        p.y += (y_off - s_y)
        '''
        p = self.pos.copy()
        isize = Vector((self.size.x, self.item_height))
        hovered = None
        for idx, item in enumerate(self.items):
            if hovered is None and self.on_hover_item(p, isize, None, None, self.cv.mouse):
                hovered = idx
            callback(p, isize, item, idx, *args, **kwargs)
            #    return idx
            p.y += self.item_height

        self.hovered_index = idx

    def on_hover_item(self, ipos, isize, item, index, m: Vector) -> int:
        return super(WidgetSelector, self).on_hover(m, ipos, isize)

    def draw_item(self, ipos, isize, item, index: int, scale: float, prefs: SCULPTPLUS_AddonPreferences):
        label = item[1] if self.expanded else item[1] + '  ▼' 
        DiText(get_rect_center(ipos, isize), label, 14, scale, pivot=(.5, .5))
        if index == self.active_index:
            DiCage(ipos, isize, 1.5, prefs.theme_active_slot_color)
        else:
            DiLine(ipos, ipos+Vector((isize.x, 0)), 1.5, Vector((prefs.theme_sidebar)) * 1.25)

    def draw(self, context, cv: Canvas, mouse: Vector, scale: float, prefs: SCULPTPLUS_AddonPreferences):
        isize = Vector((self.size.x, self.item_height))

        DiRct(self.pos, self.size, (.24, .24, .24, .9))
        DiCage(self.pos, self.size, 2.4, (.16, .16, .16, .9))

        if self.expanded:
            self.iter_items(self.draw_item, scale, prefs)
            if self.active_item is None:
                self.draw_item(self.pos, isize, (None, self.label), None, scale, prefs)

        else:
            self.draw_item(self.pos, isize, self.active_item if self.active_item else (None, self.label), self.active_index if self.active_item else None, scale, prefs)

        
