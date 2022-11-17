from .wg_base import WidgetBase
from typing import Tuple
from sculpt_plus.props import Props
import bpy
from math import radians
from mathutils import Vector
from sculpt_plus.sculpt_hotbar.di import DiRct, DiText, DiCircle, DiTri
from sculpt_plus.prefs import SCULPTPLUS_AddonPreferences
from sculpt_plus.utils.math import rotate_point_around_point, point_inside_circle, distance_between


class CtxPie(WidgetBase):
    interactable: bool = True

    def get_options(self, item) -> Tuple[Tuple[str, str, str]]:
        return ()

    def init(self):
        self.enabled = False
        self.safety_radius: int = 16 * self.cv.scale
        self.radius: int = self.safety_radius * 4
        self.target_item = None
        self.hovered_option = None
        '''
        super().init()

        self.add_defaults(
            {
                "value": 0,
                "label": "",
                "color": "black",
                "background_color": "white",
                "border_color": "black",
                "border_width": 0,
                "border_radius": 0,
            })
        '''

    def show(self, cv, m: Vector, item) -> None:
        self.origin = m
        self.options = self.get_options(item)
        self.angle_between = 360 / len(self.options)
        self.options_pos =  []
        # Rotate points for every option based on angle.
        top_point: Vector = self.origin + Vector((0, self.radius))
        for i in range(len(self.options)):
            self.options_pos.append(
                rotate_point_around_point(m, top_point, radians(self.angle_between * i))
            )
            #top_point = rotate_point_around_point(self.origin, top_point, self.angle_between)
        self.target_item = item
        print(self.options_pos)

        self.enabled = True
        cv.inject_ctx_widget(self)

    def on_mousemove(self, ctx, cv, m: Vector) -> None:
        if point_inside_circle(m, self.origin, self.safety_radius):
            self.hovered_option = None
            return
        distances = tuple(
            distance_between(m, option_pos) for option_pos in self.options_pos
        )
        min_distance: float = min(distances)
        nearest_option_index: int = distances.index(min_distance)
        self.hovered_option: str = self.options[nearest_option_index][0]
        cv.mouse = m # HACK to force update of mpos.
        return True

    def modal_exit(self, ctx, cv, m: Vector, cancel: bool = False) -> None:
        if not cancel:
            self.on_rightmouse_release(ctx, cv, m)
        self.enabled = False
        self.target_item = None
        self.hovered_option = None

    def on_rightmouse_release(self, ctx, cv, m: Vector) -> None:
        #print("on_rightmouse_release")
        if point_inside_circle(m, self.origin, self.safety_radius):
            return
        if self.hovered_option is None:
            return
        # Search for the option under mouse position.
        # Execute pie option action 'execute_pie_option'.
        self.execute_pie_option(ctx, self.hovered_option)

    def execute_pie_option(self, ctx, option_id: str) -> None:
        pass

    def draw(self, context, cv, mouse: Vector, scale: float, prefs: SCULPTPLUS_AddonPreferences):
        DiCircle(self.origin, 1.5, self.safety_radius, 16, (.92, .92, .92, .92))
        for option, option_pos in zip(self.options, self.options_pos):
            #DiCircle(option_pos, 1.5, self.safety_radius, 12, (0, 0, 0, .9))
            DiText(option_pos, option[1], 14,
                scale,
                (1,1,1,1),
                pivot=(.5,.5),
                draw_rect_props={
                    'color':(.12,.12,.12,.95),
                    'margin': 6,
                    'outline_color':(.05,.05,.05,.92) if self.hovered_option != option[0] else prefs.theme_active_slot_color
                })

class ShelfGridItemCtxPie(CtxPie):
    def get_options(self, brush: bpy.types.Brush) -> Tuple[Tuple[str, str, str]]:
        act_cat_id: str = Props.ActiveBrushCat(bpy.context).uid
        return (
            ('REMOVE', "Remove", "Remove brush from active category")
            if 'cat_id' in brush and brush['cat_id'] == act_cat_id else
            ('ADD', "Add", "Add brush to active category"),
            ('FAV', "Mark Favourite", "Mark brush as favourite")
            if 'fav' not in brush or ('fav' in brush and brush['fav'] == 0) else #brush.fav == False else
            ('UNFAV', "Unmark Favourite", "Unmark brush as favourite"),
            ('ASSIGN_ICON', "Assign Icon", "Set custom icon to the brush")
        )

    def execute_pie_option(self, ctx, option_id: str) -> None:
        print(option_id)
        if option_id == 'REMOVE':
            Props.ActiveBrushCat(ctx).remove_brush(self.target_item)
        elif option_id == 'ADD':
            Props.ActiveBrushCat(ctx).add_brush(self.target_item)
        elif option_id == 'ASSIGN_ICON':
            # brush: bpy.types.Brush = self.target_item
            # brush.use_custom_icon = True
            # TODO: operator should open browser window to select custom icon.
            pass
        elif option_id == 'FAV':
            self.target_item['fav'] = 1
        elif option_id == 'UNFAV':
            self.target_item['fav'] = 0
