from collections import defaultdict
import functools
from subprocess import call
from time import time
from typing import Dict, List, Set, Tuple
from mathutils import Vector
from bpy.app import timers

from bpy.app import version
if version <= (3, 4, 1):
    USE_BGL = True
    from bgl import glScissor, glEnable, GL_SCISSOR_TEST, glDisable, GL_BLEND, GL_DEPTH_TEST
else:
    USE_BGL = False
    from gpu import state

# gpu.stet.scissor has bug lol...
# from bgl import glScissor, glEnable, GL_SCISSOR_TEST, glDisable, GL_BLEND, GL_DEPTH_TEST
# USE_BGL = True

from sculpt_plus.sculpt_hotbar.canvas import Canvas
from sculpt_plus.sculpt_hotbar.di import DiRct, DiText
from sculpt_plus.prefs import SCULPTPLUS_AddonPreferences

from sculpt_plus.utils.math import ease_quad_in_out, lerp
from sculpt_plus.utils.cursor import Cursor, CursorIcon

num_str = {
    'ONE':1,
    'TWO':2,
    'THREE':3,
    'FOUR':4,
    'FIVE':5,
    'SIX':6,
    'SEVEN':7,
    'EIGHT':8,
    'NINE':9,
    'ZERO':0
}

class WidgetBase:
    use_scissor: bool = False
    scissor_padding: Vector = Vector((0, 0))
    interactable: bool = True
    modal_trigger: Set[str] = set()
    cursor: CursorIcon = CursorIcon.DEFAULT
    msg_on_enter: str = None

    parent: 'WidgetBase' or Canvas
    closes_itself: bool

    def __init__(self,
                 canvas: Canvas,
                 pos: Vector = Vector((0, 0)),
                 size: Vector = Vector((0, 0))) -> None:
        self.cv = canvas
        self._is_on_hover = False
        self.in_modal = False
        self.enabled = True
        # self._is_selected = False
        self.pos = pos
        self.size = size
        self.anim_pool: Dict[str, dict] = {} # Dict[str, List] = defaultdict(list) # ID: animations_data
        self.scroll_prev_time = time()
        self.parent = None
        self.closes_itself = False
        self.init()

    def anim_running(self) -> bool:
        return self.anim_pool=={}

    def init(self) -> None:
        pass

    def update(self, cv: Canvas, prefs: SCULPTPLUS_AddonPreferences) -> None:
        pass

    def poll(self, _context, cv: Canvas) -> bool:
        return True

    def invoke(self, ctx, evt, cv: Canvas, m: Vector) -> bool:
        if not self.enabled:
            return False
        ret = None
        if evt.type == 'LEFTMOUSE':
            if evt.value == 'PRESS':
                ret = self.on_leftmouse_press(ctx, cv, m)
            elif evt.value == 'RELEASE':
                ret = self.on_leftmouse_release(ctx, cv, m)
            elif evt.value == 'CLICK':
                ret = self.on_left_click(ctx, cv, m)
            elif evt.value == 'CLICK_DRAG':
                ret = self.on_left_click_drag(ctx, cv, m)
            elif evt.value == 'DOUBLE_CLICK':
                ret = self.on_double_click(ctx, cv, m)
        elif evt.type == 'RIGHTMOUSE':
            if evt.value == 'PRESS':
                ret = self.on_rightmouse_press(ctx, cv, m)
            elif evt.value == 'RELEASE':
                ret = self.on_rightmouse_release(ctx, cv, m)
            elif evt.value == 'CLICK':
                ret = self.on_right_click(ctx, cv, m)
        elif evt.value == 'PRESS' and evt.type in {'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            if time() - self.scroll_prev_time < .01:
                # BLENDER BUG: It spams scroll twice,
                # so let's limit this based on time between events.
                return False
            if evt.type == 'WHEELUPMOUSE':
                self.on_scroll_up(ctx, cv)
            elif evt.type == 'WHEELDOWNMOUSE':
                self.on_scroll_down(ctx, cv)
            self.scroll_prev_time = time()
        elif evt.type in num_str and evt.value == 'CLICK':
            ret = self.on_numkey(ctx, num_str[evt.type], cv, m)
        if ret is not None: return bool(ret)
        return self.event(ctx, evt, cv, m)

    def event(self, ctx, evt, cv: Canvas, m: Vector) -> bool:
        return evt.type in self.modal_trigger

    def modal_enter(self, ctx, cv: Canvas, m: Vector) -> None:
        pass

    def modal_exit(self, ctx, cv: Canvas, m: Vector, cancel: bool = False) -> None:
        pass

    def modal(self, ctx, evt, cv: Canvas, m: Vector) -> bool:
        # print(evt.type, evt.value)
        if evt.type in {'ESC', 'RIGHTCLICK'}:
            return False
        if evt.value == 'RELEASE':
            if evt.type == 'RIGHTMOUSE':
                self.on_rightmouse_release(ctx, cv, m)
            elif evt.type == 'LEFTMOUSE':
                self.on_leftmouse_release(ctx, cv, m)
            return False
        if evt.type == 'MOUSEMOVE':
            self.on_mousemove(ctx, cv, m)
            return True
        return True

    def _on_hover(self, ctx, m) -> bool:
        if not self.enabled:
            return False
        if not self.poll(ctx, self.cv):
            return False
        if self.on_hover(m):
            self.cv.refresh(ctx)
            # print("Hover...", self)
            if not self._is_on_hover:
                self.cv.refresh(ctx)
                if self.msg_on_enter:
                    ctx.area.header_text_set(self.msg_on_enter)
                self._is_on_hover = True
                self.on_hover_enter()
            if self.cursor:
                Cursor.set_icon(ctx, self.cursor)
            res =  self.on_hover_stay(m)
            if res:
                self.cv.refresh(ctx)
            return True
        else:
            if self._is_on_hover:
                if self.cursor and self.cursor != CursorIcon.DEFAULT:
                    Cursor.set_icon(ctx, CursorIcon.DEFAULT)
                if self.msg_on_enter:
                    ctx.area.header_text_set(None)
                self._is_on_hover = False
                self.on_hover_exit()
                self.cv.refresh(ctx)
            return False


    ''' OnHover Methods. '''
    @staticmethod
    def check_hover(widget: 'WidgetBase', m: Vector, p: Vector = None, s: Vector = None) -> bool:
        p = p if p else widget.pos
        s = s if s else widget.size
        return m.x>p.x and m.x<p.x+s.x and m.y>p.y and m.y<p.y+s.y and s.x > 2 and s.y > 2

    def on_hover(self, m: Vector, p: Vector = None, s: Vector = None) -> bool:
        p = p if p else self.pos
        s = s if s else self.size
        return m.x>p.x and m.x<p.x+s.x and m.y>p.y and m.y<p.y+s.y and s.x > 2 and s.y > 2

    def on_hover_enter(self) -> None:
        pass

    def on_hover_exit(self) -> None:
        pass

    def on_hover_stay(self, m: Vector) -> bool:
        return False


    ''' Event Methods.'''
    def on_leftmouse_press(self, ctx, cv: Canvas, m: Vector) -> None:
        pass

    def on_leftmouse_release(self, ctx, cv: Canvas, m: Vector) -> None:
        pass

    def on_left_click(self, ctx, cv: Canvas, m: Vector) -> None:
        pass

    def on_left_click_drag(self, ctx, cv: Canvas, m: Vector) -> None:
        pass

    def on_double_click(self, ctx, cv: Canvas, m: Vector) -> None:
        pass

    def on_rightmouse_press(self, ctx, cv: Canvas, m: Vector) -> None:
        pass

    def on_rightmouse_release(self, ctx, cv: Canvas, m: Vector) -> None:
        pass

    def on_right_click(self, ctx, cv: Canvas, m: Vector) -> None:
        pass

    def on_numkey(self, ctx, number: int, cv: Canvas, m: Vector) -> None:
        pass

    def on_mousemove(self, ctx, cv: Canvas, m: Vector) -> None:
        pass

    def on_scroll_up(self, ctx, cv: Canvas):
        pass

    def on_scroll_down(self, ctx, cv: Canvas):
        pass


    ''' Transform Methods. '''
    def move(self, x: int = 0, y: int = 0,
             animate: bool = False,
             anim_change_callback: callable = None,
             anim_finish_callback: callable = None) -> None:
        if x == 0 and y == 0:
            return
        self.move_to(self.pos.x + x, self.pos.y + y,
                     animate=animate,
                     anim_change_callback=anim_change_callback,
                     anim_finish_callback=anim_finish_callback)

    def move_to(self, x: int = 0, y: int = 0,
                animate: bool = False,
                anim_change_callback: callable = None,
                anim_finish_callback: callable = None) -> None:
        if not animate:
            if x != 0:
                self.pos.x = int(x)
            if y != 0:
                self.pos.y = int(y)
            return

        if x != 0:
            self.anim(
                'pos_x',
                self.pos, 'x', int(x),
                duration=0.4, delay=0.01,
                smooth=True,
                change_callback=anim_change_callback,
                finish_callback=anim_finish_callback)
        if y != 0:
            self.anim(
                'pos_y',
                self.pos, 'y', int(y),
                duration=0.4, delay=0.01,
                smooth=True,
                change_callback=anim_change_callback,
                finish_callback=anim_finish_callback)

    def scale(self, x: float = 1, y: float = 1,
              animate: bool = False,
              anim_change_callback: callable = None,
              anim_finish_callback: callable = None) -> None:
        if x == 1 and y == 1:
            return
        self.move_to(self.size.x * x, self.size.y * y,
                     animate=animate,
                     anim_change_callback=anim_change_callback,
                     anim_finish_callback=anim_finish_callback)

    def resize(self, x: float = 1, y: float = 1,
               animate: bool = False,
               anim_change_callback: callable = None,
               anim_finish_callback: callable = None) -> None:
        if not animate:
            if x != 1:
                self.size.x = int(x)
            if y != 1:
                self.size.y = int(y)
            return

        if x != 1:
            self.anim(
                'size_x',
                self.size, 'x', int(x),
                duration=0.3, delay=0.01,
                smooth=True,
                change_callback=anim_change_callback,
                finish_callback=anim_finish_callback)
        if y != 1:
            self.anim(
                'size_y',
                self.size, 'y', int(y),
                duration=0.3, delay=0.01,
                smooth=True,
                change_callback=anim_change_callback,
                finish_callback=anim_finish_callback)


    ''' Util Methods. '''
    def get_pos_by_relative_point(self, rel_point: Vector) -> Vector:
        return self.pos + self.size * rel_point
        '''
        Vector((
            self.pos.x + self.size.x * rel_point.x,
            self.pos.y + self.size.y * rel_point.y
        ))
        '''

    def get_pos_size_by_anchor(self, anchor: Vector) -> Tuple[Vector, Vector]:
        p_min = self.pos + self.size * anchor.xz
        p_max = self.pos + self.size * anchor.yw
        return p_min, p_max - p_min
        '''
        Vector((
            self.pos.x + self.size.x * anchor.x,
            self.pos.y + self.size.y * anchor.z
        )), Vector((
            self.pos.x + self.size.x * anchor.y,
            self.pos.y + self.size.y * anchor.w
        ))
        '''

    def anim(self,
             idname: str,
             data,
             attr: str,
             target_value: float or int,
             duration: float,
             smooth: bool = False,
             delay: float = 0.01,
             change_callback: callable = None,
             finish_callback: callable = None,
             attr_index: int = None,
             block_existing_anim: bool = False) -> None:

        if not hasattr(data, attr):
            return

        def _anim_done(_idname: str) -> None:
            del self.anim_pool[_idname]

        def _anim(ease_fun: callable, anim: dict):
            t: float = min(time() - anim['start_time'], anim['time']) / anim['time']
            if t >= .98:
                if anim['attr_index']:
                    getattr(anim['data'], anim['attr'])[attr_index] = anim['end_value']
                else:
                    setattr(anim['data'], anim['attr'], anim['end_value'])
                if anim['change_callback']:
                    anim['change_callback']()
                if anim['finish_callback']:
                    anim['finish_callback']()
                _anim_done(anim['idname'])
                #print("Finish Anim!")
                return None

            if anim['value_dimension'] == 1:
                value = ease_fun(anim['start_value'], anim['end_value'], t)
                #print("start, end", anim['start_value'], anim['end_value'])
                #print(anim['data'], anim['attr'], value)
                if anim['attr_index']:
                    getattr(anim['data'], anim['attr'])[attr_index] = value
                else:
                    setattr(anim['data'], anim['attr'], value)
            else:
                for i in range(anim['value_dimension']):
                    value = lerp(anim['start_value'][i], anim['end_value'][i], t) #anim_timer/data['time'])
                    getattr(anim['data'], anim['attr'])[i] = value

            if anim['change_callback']:
                anim['change_callback']()
            #print("ANIM, value", value)

            return 0.001 # data['interval']

        def _anim_wait(start_time: float, anim: dict):
            pass

        if idname not in self.anim_pool:
            current_value = getattr(data, attr)
            if not isinstance(current_value, (Vector, list, int, float)):
                print("Animating an incompatible type!")
                return
            #print("Current:", current_value, "Target:", target_value)
            anim_data = {
                'idname': idname,
                'data': data,
                'attr': attr,
                'attr_index': attr_index,
                'start_value': current_value,
                'end_value': target_value,
                'value_dimension': len(current_value) if isinstance(current_value, (Vector, list)) else 1,
                'start_time': time(),
                'time': duration,
                'change_callback': change_callback,
                'finish_callback': finish_callback,
            }
            ease_fun: callable = ease_quad_in_out if smooth else lerp
            self.anim_pool[idname] = anim_data
            self.time_fun(_anim, delay, ease_fun, self.anim_pool[idname])
        else:
            # Hey leave me to breath, uh.
            if not block_existing_anim and time() - self.anim_pool[idname]['start_time'] < 0.2:
                #print("UPDATE WTF U DOIN'")
                return
            self.anim_pool[idname].update(
                end_value=getattr(data, attr),
                time=duration,
                start_time=time(),
            )

    def time_fun(self, fun, time=0.1, *args, **kwargs):
        if timers.is_registered(fun):
            return
        timers.register(functools.partial(fun, *args, **kwargs), first_interval=time)

    def _draw(self, context, cv: Canvas, mouse: Vector, scale: float, prefs: SCULPTPLUS_AddonPreferences):
        if not self.enabled:
            return False
        if self.size.x == 0 or self.size.y == 0:
            return False
        if not self.poll(context, cv):
            return False
        if not self.draw_poll(context, cv):
            return False
        self.draw_pre(context, cv, mouse, scale, prefs)
        if self.use_scissor:
            #glDisable(GL_DEPTH_TEST)
            if USE_BGL:
                glEnable(GL_SCISSOR_TEST)
            else:
                state.scissor_test_set(True)
            self.draw_scissor_apply(self.pos, self.size)
            DiText(Vector((0,0)), ' ', 1, scale, prefs.theme_text)
        self.draw(context, cv, mouse, scale, prefs)
        if self.use_scissor:
            if USE_BGL:
                glDisable(GL_SCISSOR_TEST)
            else:
                state.scissor_test_set(False)
            self.draw_scissor_apply(Vector((0, 0)), Vector((context.region.width, context.region.height)))
            self.draw_post(context, cv, mouse, scale, prefs)

    def draw_scissor_apply(self, _p: Vector, _s: Vector):
        if USE_BGL:
            glScissor(
                int(_p.x)-1+int(self.scissor_padding.x),
                int(_p.y)-1+int(self.scissor_padding.x),
                int(_s.x)+2-int(self.scissor_padding.x*2),
                int(_s.y)+2-int(self.scissor_padding.x*2))
        else:
            state.scissor_set(
                int(_p.x)-1+int(self.scissor_padding.x),
                int(_p.y)-1+int(self.scissor_padding.x),
                int(_s.x)+2-int(self.scissor_padding.x*2),
                int(_s.y)+2-int(self.scissor_padding.x*2))

    def draw_poll(self, context, cv: Canvas) -> bool:
        return True
    
    def draw_pre(self, context, cv: Canvas, mouse: Vector, scale: float, prefs: SCULPTPLUS_AddonPreferences):
        pass

    def draw_post(self, context, cv: Canvas, mouse: Vector, scale: float, prefs: SCULPTPLUS_AddonPreferences):
        pass

    def draw_over(self, context, cv: Canvas, mouse: Vector, scale: float, prefs: SCULPTPLUS_AddonPreferences):
        pass

    def draw(self, context, cv: Canvas, mouse: Vector, scale: float, prefs: SCULPTPLUS_AddonPreferences):
        #print("Draw::", self, self.pos, self.size)
        DiRct(self.pos, self.size, (.1, .1, .1, .8))
