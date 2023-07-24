from .wg_base import WidgetBase, Canvas, Vector, SCULPTPLUS_AddonPreferences
from .wg_but import ButtonGroup
from sculpt_plus.lib.icons import Icon

from brush_manager.api import BM, BM_UI


class SidebarContextSwitcher(ButtonGroup):
    but_ctx_brush: object
    but_ctx_texture: object

    def init(self) -> None:
        super().init()
        self.but_ctx_brush = None
        self.but_ctx_texture = None

        self.button_style['outline_color'] = (.24, .24, .24, .9)
        self.button_style['color'] = (.16, .16, .16, .65)

        self.style['separator_color'] = None

        def _toggle(cv: Canvas, ctx_type: str, target_button):
            if BM_UI.get_ctx_item() == ctx_type:
                return
            
            item_type: str = BM_UI.toggle_ctx_item()

            if item_type == 'TEXTURE':
                cv.shelf_grid_item_info.expand = True
            else:
                cv.shelf_grid_item_info.expand = False

            for but in self.buttons:
                but.set_state('ENABLED', remove=True)
            target_button.set_state('ENABLED')

        self.but_ctx_brush = self.new_button(
            "",
            icon=Icon.PAINT_BRUSH,
            on_click_callback=lambda ctx, cv: _toggle(cv, 'BRUSH', self.but_ctx_brush),
        )
        self.but_ctx_texture = self.new_button(
            "",
            icon=Icon.TEXTURE_OPACITY,
            on_click_callback=lambda ctx, cv: _toggle(cv, 'TEXTURE', self.but_ctx_texture),
        )

        self.but_ctx_brush.set_state('ENABLED')

    def update(self, cv: Canvas, prefs: SCULPTPLUS_AddonPreferences) -> None:
        parent = cv.shelf_sidebar
        margin = 8 * cv.scale
        self.size = Vector((32, 64 + margin)) * cv.scale
        self.pos = parent.get_pos_by_relative_point(Vector((0, 1)))
        self.pos.x -= (parent.margin + self.size.x)
        self.pos.y -= (self.size.y - parent.header_height)

        if self.but_ctx_brush is None or self.but_ctx_texture is None:
            return

        but_size = Vector((32, 32)) * cv.scale
        self.but_ctx_texture.pos = self.pos.copy()
        self.but_ctx_brush.pos   = self.pos + Vector((0, but_size.y + margin))
        self.but_ctx_brush.size  = self.but_ctx_texture.size = but_size

    def poll(self, _context, cv: Canvas) -> bool:
        return cv.shelf.expand and cv.shelf.size.y > self.size.y

    def draw_pre(self, context, cv: Canvas, mouse: Vector, scale: float, prefs: SCULPTPLUS_AddonPreferences):
        pass
