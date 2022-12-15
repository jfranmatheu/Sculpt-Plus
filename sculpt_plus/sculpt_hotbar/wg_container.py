from .wg_base import WidgetBase, Canvas, Vector, SCULPTPLUS_AddonPreferences


class WidgetContainer(WidgetBase):
    def __init__(self, canvas: Canvas, pos: Vector = Vector((0, 0)), size: Vector = Vector((0, 0))) -> None:
        self.hovered_widget = None
        self.modal_widget = None
        self._children: list[WidgetBase] = []

        super().__init__(canvas, pos, size)

    def update(self, cv: Canvas, prefs: SCULPTPLUS_AddonPreferences) -> None:
        if not self.enabled:
            return False

        super().update(cv, prefs)

        for child in self._children:
            child.update(cv, prefs)

    def add_child(self, widget: WidgetBase) -> None:
        self._children.append(widget)
        widget.parent = self

    def remove_child(self, widget: WidgetBase) -> None:
        self._children.remove(widget)
        widget.parent = None

    def on_hover(self, m) -> bool:
        if not self.enabled:
            return False
        if self.hovered_widget:
            if not self.hovered_widget.on_hover(m):
                self.hovered_widget = None
        if super().on_hover(m):
            for child in self._children:
                hov = child.on_hover(m)
                if hov:
                    self.hovered_widget = child
                    return True
        self.hovered_widget = None
        return False

    def on_hover_exit(self) -> None:
        if self.hovered_widget:
            self.hovered_widget.on_hover_exit()
            self.hovered_widget = None

    def invoke(self, ctx, evt, cv: Canvas, m: Vector) -> bool:
        if not self.enabled:
            return False
        if self.hovered_widget is None:
            return False
        return self.hovered_widget.invoke(ctx, evt, cv, m)

    def modal_enter(self, ctx, cv: Canvas, m: Vector) -> None:
        self.modal_widget = self.hovered_widget
        self.modal_widget.modal_enter(ctx, cv, m)

    def modal(self, ctx, evt, cv: Canvas, m: Vector) -> bool:
        if self.modal_widget is None:
            return False
        return self.modal_widget.modal(ctx, evt, cv, m)

    def modal_exit(self, ctx, cv: Canvas, m: Vector, cancel: bool = False) -> None:
        self.modal_widget.modal_exit(ctx, cv, m, cancel=cancel)
        self.modal_widget = None

    def draw_container(self, context, cv: Canvas, scale: float, prefs: SCULPTPLUS_AddonPreferences):
        pass

    def _draw(self, context, cv: Canvas, mouse: Vector, scale: float, prefs: SCULPTPLUS_AddonPreferences):
        super()._draw(context, cv, mouse, scale, prefs)

        if self.enabled:
            for child in self._children:
                child._draw(context, cv, mouse, scale, prefs)


class WidgetContainerChild(WidgetBase):
    parent: WidgetContainer
