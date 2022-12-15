from .wg_base import WidgetBase, Vector, Canvas, SCULPTPLUS_AddonPreferences
from sculpt_plus.lib.icons import Icon
from sculpt_plus.sculpt_hotbar.di import DiRct, DiText, DiIco, get_text_dim, DiLine, DiIcoCol, DiCage


class Button(WidgetBase):
    interactable: bool = True

    def __init__(self, canvas: Canvas,
                 pos: Vector = Vector((0, 0)),
                 size: Vector = Vector((0, 0)),
                 on_click_callback: callable = None,
                 label: str = '',
                 color: tuple = (.1, .1, .1, .8),
                 text_color: tuple = (.92, .92, .92, .92),
                 text_size: int = 12,
                 icon: Icon = None,
                 icon_color: tuple = None,
                 outline_color: tuple = None) -> None:
        super().__init__(canvas, pos, size)
        self.states = {0}
        self.style = {
            'label': label,
            'color': color,
            'text_color': text_color,
            'text_size': text_size,
            'icon': icon,
            'icon_color': icon_color,
            'outline_color': outline_color,
        }
        self.on_click_callback = on_click_callback

    def set_state(self, state: str, remove: bool = False):
        if state == 'IDLE':
            state = 0
        elif state == 'HOVERED':
            state = 1
        elif state == 'ENABLED':
            state = 2
        elif state == 'DISABLED':
            state = 3
        else:
            state = 0
        if remove:
            if state in self.states:
                self.states.remove(state)
        else:
            self.states.add(state)

    def on_left_click(self, ctx, cv: Canvas, m: Vector) -> None:
        self.action(ctx, cv)
        return

    def action(self, ctx, cv: Canvas) -> None:
        if self.on_click_callback:
            self.on_click_callback(ctx, cv)

    def draw(self, scale: float, prefs: SCULPTPLUS_AddonPreferences) -> None:
        # states:
        # 0: idle
        # 1: highlighted
        # 2: active
        # 3: grayout
        style = self.style
        states = self.states
        # Priority order.
        if style['color']:
            DiRct(self.pos, self.size, style['color'])
        if 3 in states:
            DiRct(self.pos, self.size, (.1, .1, .1, .5))
        elif 2 in states:
            DiRct(self.pos, self.size, prefs.theme_active_slot_color)
        elif 1 in states or self._is_on_hover:
            DiRct(self.pos, self.size, (.64, .64, .64, .25))
        else:
            # 0
            pass

        if style['outline_color']:
            DiCage(self.pos, self.size, 1.5, style['outline_color'])

        padding = Vector((5, 5)) * scale
        inner_pos: Vector = self.pos + padding
        inner_size: Vector = self.size - padding * 2
        if style['label']:
            label_size: Vector = Vector(get_text_dim(style['label'], style['text_size'], scale))
            if style['icon'] is None:
                text_pos: Vector = self.get_pos_by_relative_point(Vector((.5, .5)))
            else:
                icon_pos: Vector = inner_pos.copy()
                icon_size: Vector = Vector((inner_size.y, inner_size.y))

                if style['icon_color']:
                    DiIcoCol(icon_pos, icon_size, style['icon'], style['icon_color'])
                else:
                    DiIco(icon_pos, icon_size, style['icon'])

                inner_pos.x += (icon_size.x + padding.x * .5)
                inner_size.x -= (icon_size.x + padding.x) # * 2)
                text_pos: Vector = inner_pos + inner_size * Vector((.5, .5))

            label_text = style['label']
            if label_size.y > inner_size.y:
                style['text_size'] -= 1
            if label_size.x > inner_size.x:
                character_count: int = len(label_text)
                size_per_character = label_size.x / max(1, character_count)
                overflow_size = label_size.x - inner_size.x
                max_text_length = character_count - int(overflow_size / max(1, size_per_character))
                label_text = label_text[:max_text_length] + '...'

            DiText(text_pos,
                    label_text,
                    style['text_size'],
                    scale,
                    style['text_color'],
                    pivot=(.5,.5))

        elif style['icon'] is not None:
            icon_pos: Vector = inner_pos # self.get_pos_by_relative_point(Vector((.5, 0)))
            icon_size: Vector = Vector((inner_size.y, inner_size.y))
            if style['icon_color']:
                DiIcoCol(icon_pos, icon_size, style['icon'], style['icon_color'])
            else:
                if style['icon_color']:
                    DiIcoCol(icon_pos, icon_size, style['icon'], style['icon_color'])
                else:
                    DiIco(icon_pos, icon_size, style['icon'])



class ButtonGroup(WidgetBase):
    buttons: list[Button]
    hovered_button: Button

    def __init__(self,
                 canvas: Canvas,
                 pos: Vector = Vector((0, 0)),
                 size: Vector = Vector((0, 0)),
                 but_spacing: int = 0,
                 bg_color: tuple = (.1, .1, .1, .8),
                 text_color: tuple = (.92, .92, .92, .92),
                 text_size: int = 12,
                 icon_color: tuple = (.75, .75, .75, .75),
                 outline_color: tuple = None,
                 separator_color: tuple = (.5, .5, .5, .5)) -> None:
        self.style = {
            'color': bg_color,
            'separator_color': separator_color,
        }

        self.button_style = {
            'color': None, # color,
            'text_color': text_color,
            'text_size': text_size,
            'icon_color': icon_color,
            'outline_color': outline_color,
        }

        self.but_spacing = but_spacing

        self.buttons = []
        self.hovered_button = None

        super().__init__(canvas, pos, size)

    def init(self) -> None:
        pass

    def new_button(self, label: str = '', icon: Icon = None, on_click_callback: callable = None) -> Button:
        button = Button(self.cv, Vector((0, 0)), Vector((0, 0)), on_click_callback=on_click_callback, label=label, icon=icon, **self.button_style)
        self.add_button(button)
        return button

    def add_button(self, button: Button) -> None:
        self.buttons.append(button)
        self.update(self.cv, None)

    def update(self, cv: Canvas, prefs: SCULPTPLUS_AddonPreferences) -> None:
        # super().update(cv, prefs)
        p = self.pos.copy()
        s = self.size.copy()

        button_count = len(self.buttons)
        if self.but_spacing == 0:
            sep = None
        else:
            sep = self.but_spacing * cv.scale
            #p.x -= ((button_count-1) * sep)

        if self.but_spacing == 0 or not all([but.style['icon'] is not None for but in self.buttons]):
            width_per_button: float = s.x / button_count
            if sep:
                width_per_button -= (((button_count-1) * sep) / button_count)
        else:
            width_per_button = s.y # + sep # margin between

        for i, button in enumerate(self.buttons):
            button.pos.x = p.x + i * width_per_button
            if sep:
                button.pos.x += (sep * i)
            button.pos.y = p.y
            button.size.x = width_per_button
            button.size.y = s.y

    def on_left_click(self, ctx, cv: Canvas, m: Vector) -> None:
        if not self.hovered_button:
            return
        self.hovered_button.on_left_click(ctx, cv, m)

    def on_hover_stay(self, m: Vector) -> bool:
        for button in self.buttons:
            if button.on_hover(m):
                if button != self.hovered_button:
                    if self.hovered_button:
                        self.hovered_button.set_state('HOVERED', remove=True)
                    self.hovered_button = button
                    button.set_state('HOVERED')
                    return True
                return False
        if self.hovered_button:
            self.hovered_button.set_state('HOVERED', remove=True)
        self.hovered_button = None

    def on_hover_exit(self) -> None:
        if self.hovered_button:
            self.hovered_button.set_state('HOVERED', remove=True)
        self.hovered_button = None

        for button in self.buttons:
            button.on_hover_exit()

    def draw_pre(self, context, cv: Canvas, mouse: Vector, scale: float, prefs: SCULPTPLUS_AddonPreferences):
        DiRct(self.pos, self.size, self.style['color'])

    def draw(self, context, cv: Canvas, mouse: Vector, scale: float, prefs: SCULPTPLUS_AddonPreferences):
        DiText(self.pos, '.', 1, 1, (0, 0, 0, .1))
        for button in self.buttons:
            # is_hovered = button==self.hovered_button
            button.draw(scale, prefs)

        if self.style['separator_color']:
            for button in (self.buttons[:-1] if self.but_spacing != 0 else self.buttons):
                top_right = button.get_pos_by_relative_point(Vector((1, 1)))
                bot_right = button.get_pos_by_relative_point(Vector((1, 0)))
                DiLine(top_right, bot_right, 1.25, self.style['separator_color'])
