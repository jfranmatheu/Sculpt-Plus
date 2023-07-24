from .wg_base import WidgetBase
from typing import Tuple, Union
import bpy
from bpy import ops as OPS
from math import radians, cos, sin
from mathutils import Vector
from sculpt_plus.sculpt_hotbar.di import DiRct, DiText, DiCircle, DiTri, get_text_dim
from sculpt_plus.prefs import SCULPTPLUS_AddonPreferences
from sculpt_plus.utils.math import rotate_point_around_point, point_inside_circle, distance_between
from sculpt_plus.props import Props

from brush_manager.api import bm_types, BM_UI, BM_OPS, BM


item_types = Union[bm_types.Brush, bm_types.Texture, bm_types.BrushCategory, bm_types.TextureCategory]


class CtxPie(WidgetBase):
    interactable: bool = True
    target_item: item_types

    def get_options(self, item: item_types) -> Tuple[Tuple[str, str, str]]:
        return ()

    def init(self):
        self.enabled = False
        self.safety_radius: int = 20 * self.cv.scale
        self.radius: int = self.safety_radius * 3.5
        # self.target_item = None
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

    def show(self, cv, m: Vector, item: item_types) -> None:
        self.origin = m
        self.options = self.get_options(item)
        self.safety_radius: int = 20 * self.cv.scale
        self.radius: int = self.safety_radius * (3.32 * self.cv.scale)
        if not self.options:
            return
        angle_between = 360 / len(self.options)
        self.options_pos =  []
        # Rotate points for every option based on angle.
        top_point: Vector = self.origin + Vector((0, self.radius))
        for i, option in enumerate(self.options):
            label_dim = Vector(get_text_dim(option[1], 14, cv.scale)) / 2.0
            angle = radians(angle_between * i)
            p = rotate_point_around_point(self.origin, top_point, angle)
            displacement = p - self.origin
            displacement_factor = displacement / self.radius
            if displacement_factor.x != 0:
                p.x += (label_dim.x * displacement_factor.x)
            if displacement_factor.y != 0:
                p.y += (label_dim.y * displacement_factor.y)
            self.options_pos.append(p)

        self.target_item = item
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
        DiCircle(self.origin, 2.0, self.safety_radius, 16, (.92, .92, .92, .92) if self.hovered_option else (.9, .3, .2, .92))
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
    def get_options(self, item: Union[bm_types.Brush, bm_types.Texture]) -> Tuple[Tuple[str, str, str]]:
        item_type: str = BM_UI.get_ctx_item()
        if item_type == 'BRUSH':
            # act_cat_id: str = Props.ActiveBrushCat().uuid
            cat_count: int = Props.BrushCatsCount()
        elif item_type == 'TEXTURE':
            # act_cat_id: str = Props.ActiveTextureCat().uuid
            cat_count: int = Props.TextureCatsCount()
        else:
            return ()
        options = (
            ('MOVE', "Move", "Move item to another category") if cat_count > 1 else None,
            # if item.cat_id == act_cat_id else
            ## ('UNFAV', "Unmark Favourite", "Unmark item as favourite")
            ## if item.fav else
            ## ('FAV', "Mark Favourite", "Mark brush as favourite"),
            ('REMOVE', "Remove", "Remove item from category"),
            ('SAVE', "Save Default", "Save default state of the brush") if item_type=='BRUSH' else None,
            ('RESET', "Reset to Default", "Reset brush to default state") if item_type=='BRUSH' else None,
            ('ASSIGN_ICON', "Assign Icon", "Set custom icon to the brush") if item_type=='BRUSH' else None,
            ('RENAME', "Rename", "Change item name"),
            ## ('DUPLICATE', "Duplicate", "Make a brush copy") if item_type=='BRUSH' else None,
        )
        return tuple(op for op in options if op is not None)

    def execute_pie_option(self, ctx, option_id: str) -> None:
        # print(option_id)
        item_type: str = BM_UI.get_ctx_item(ctx)
        target_item_uuid = self.target_item.uuid
        if option_id == 'REMOVE':
            if item_type == 'BRUSH':
                Props.BrushManager(ctx).remove_brush(self.target_item)
                # Props.ActiveBrushCat().unlink_item(self.target_item)
            elif item_type == 'TEXTURE':
                Props.BrushManager(ctx).remove_texture(self.target_item)
                # Props.ActiveTextureCat().unlink_item(self.target_item)
        elif option_id == 'MOVE':
            BM_OPS.move_selected_to_category(uuid=target_item_uuid)
        elif option_id == 'ASSIGN_ICON':
            BM_OPS.asign_icon_to_active_brush(uuid=target_item_uuid)
        ## elif option_id == 'FAV':
        ##     self.target_item.fav = True
        ## elif option_id == 'UNFAV':
        ##     self.target_item.fav = False
        elif option_id == 'RENAME':
            BM_OPS.rename_item(uuid=target_item_uuid)
        ## elif option_id == 'DUPLICATE':
        ##     Props.BrushManager(ctx).duplicate_brush(self.target_item)


class ShelfSidebarCatCtxPie(CtxPie):
    def get_options(self, item: Union[bm_types.BrushCategory, bm_types.TextureCategory]) -> Tuple[Tuple[str, str, str]]:
        item_type: str = BM_UI.get_ctx_item()
        # if type == 'BRUSH':
        #     act_cat: str = Props.ActiveBrushCat()
        #     max_index: int = Props.BrushCatsCount() -1 
        # elif type == 'TEXTURE':
        #     act_cat: str = Props.ActiveTextureCat()
        #     max_index: int = Props.TextureCatsCount() -1
        # else:
        #     return ()
        # item_is_active = item == act_cat
        options = (
            ## ('MOVE_UP', "Move Up", "Move category upwards") if item_is_active and act_cat.index < max_index else None,
            ## ('MOVE_DOWN', "Move Down", "Move category upwards") if item_is_active and act_cat.index > 0 else None,
            ##  ('MOVE_UP', "Move Up", "Move category upwards") if item_is_active and act_cat.index > 0 else None,
            ('REMOVE', "Remove", "Remove category"),
            ('SAVE', "Save Brushes Defaults", "Save default state for every brush") if item_type=='BRUSH' else None,
            ('RESET', "Reset Brushes to Defaults", "Reset to default state for every brush") if item_type=='BRUSH' else None,
            ('ASSIGN_ICON', "Assign Icon", "Set custom icon to the category"),
            ('RENAME', "Rename", "Change item name"),
        )
        return tuple(op for op in options if op is not None)

    def execute_pie_option(self, ctx, option_id: str) -> None:
        item_type: str = BM_UI.get_ctx_item(ctx)
        target_item_uuid: str = self.target_item.uuid
        if option_id == 'REMOVE':
            if type == 'BRUSH':
                Props.BrushManager(ctx).remove_brush_cat(self.target_item)
            elif type == 'TEXTURE':
                Props.BrushManager(ctx).remove_texture_cat(self.target_item)
        ## elif option_id == 'MOVE_UP':
        ##     pass
        ## elif option_id == 'MOVE_DOWN':
        ##     pass
        elif option_id == 'ASSIGN_ICON':
            BM_OPS.asign_icon_to_active_category(uuid=target_item_uuid)
        elif option_id == 'SAVE':
            pass
        elif option_id == 'RESET':
            BM_OPS.reset_cat(uuid=target_item_uuid)
            pass
        elif option_id == 'RENAME':
            BM_OPS.rename_cat(uuid=target_item_uuid)
