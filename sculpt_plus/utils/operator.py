from bpy.types import Operator, Context, Event, Object, PointerProperty, Property, FloatProperty, IntProperty, BoolProperty, StringProperty
from bpy.utils import register_class, unregister_class
from bpy import props as BPY_PROPS
from mathutils import Vector, Matrix
from bpy_extras import view3d_utils

from .raycast import RaycastInfo


dynamic_operators = []


class OpsReturn:
    FINISH = {'FINISHED'}
    CANCEL = {'CANCELLED'}
    PASS = {'PASS_THROUGH'}
    RUN = {'RUNNING_MODAL'}
    UI = {'INTERFACE'}


def add_modal_handler(context, operator):
    if not context.window_manager.modal_handler_add(operator):
        print("WARN! Operator failed to add modal handler!")
        return OpsReturn.CANCEL
    return OpsReturn.RUN



def get_bpy_prop_kwargs(prop, override_value = None) -> dict:
    kwargs = {
        'name': prop.name,
        'description': prop.description,
        'subtype': prop.subtype,
    }
    if isinstance(prop, (FloatProperty, IntProperty)):
        kwargs['min'] = prop.hard_min
        kwargs['max'] = prop.hard_max
        kwargs['soft_min'] = prop.soft_min
        kwargs['soft_max'] = prop.soft_max
        kwargs['default'] = prop.default
    elif isinstance(prop, BoolProperty):
        kwargs['default'] = prop.default
    elif isinstance(prop, StringProperty):
        kwargs['default'] = prop.default
    # Vectors... .default_array as 'default'... also array dimensions...
    if override_value is not None:
        kwargs['default'] = override_value
    return kwargs


class OpWrapper:
    # bl_operator_kwargs: dict

    def invoke(self, context: Context, event: Event):
        return self.execute(context)

    def pre_execute(self, context):
        pass

    def post_execute(self, context):
        pass

    def execute(self, context):
        # Call original operator with self properties.
        self.pre_execute(context)
        self.original_bl_operator('INVOKE_DEFAULT', False, **self.get_props_dict()) # , **self.bl_operator_kwargs)
        self.post_execute(context)
        return {'FINISHED'}


class OpExecutePropsWrapper(OpWrapper):
    def invoke(self, context: Context, event: Event):
        return context.window_manager.invoke_props_dialog(self, width=300)


class OpModalOnReleaseExecuteWrapper(OpWrapper):
    options = {'DRAW_2D', 'DRAW_3D', 'RAYCAST', 'EVAL_ACTIVE_OBJECT'}
    mouse_pos: Vector

    def update_mouse(self, event: Event):
        self.mouse_pos = Vector((event.mouse_region_x, event.mouse_region_y))

    def invoke(self, context: Context, event: Event):
        context.window_manager.modal_handler_add(self)
        self.update_mouse(event)
        options = self.__class__.options
        if 'DRAW_2D' in options:
            self._draw_handler_2d = context.space_data.draw_handler_add(self._draw, (context, self.draw_2d), 'WINDOW', 'POST_PIXEL')
        if 'DRAW_3D' in options:
            self._draw_handler_3d = context.space_data.draw_handler_add(self._draw, (context, self.draw_3d), 'WINDOW', 'POST_VIEW')
        if 'RAYCAST' in options:
            self.raycast = RaycastInfo(context.active_object)
            self.raycast.result = False
            self.active_object: Object = context.active_object
            if 'EVAL_ACTIVE_OBJECT' in options:
                depsgraph = context.evaluated_depsgraph_get()
                self.eval_active_object: Object = self.active_object.evaluated_get(depsgraph)
            else:
                self.eval_active_object = None
        self.ctx_area = context.area
        self.modal_start(context)
        self.ctx_area.tag_redraw()
        self._modal_checker = None
        return {'RUNNING_MODAL'}

    def execute(self, context):
        if not hasattr(self, '_modal_checker'):
            # DOES NOT WORK IF NOT USING MODAL (VIA INVOKE).
            return {'CANCELLED'}
        return super().execute(context)

    def modal_start(self, context: Context):
        pass

    def modal_finish(self, context: Context):
        pass

    def pre_modal(self, context: Context, event: Event):
        pass

    def post_modal(self, context: Context, event: Event):
        pass

    def draw_2d(self, context: Context):
        pass

    def draw_3d(self, context: Context):
        pass

    def finish(self, context: Context):
        options = self.__class__.options
        if 'DRAW_2D' in options:
            self._draw_handler_2d = context.space_data.draw_handler_remove(self._draw_handler_2d, 'WINDOW')
            del self._draw_handler_2d
        if 'DRAW_3D' in options:
            self._draw_handler_3d = context.space_data.draw_handler_remove(self._draw_handler_3d, 'WINDOW')
            del self._draw_handler_3d
        if 'RAYCAST' in options:
            del self.raycast
        self.ctx_area.tag_redraw()
        self.modal_finish(context)

    def modal(self, context: Context, event: Event):
        self.pre_modal(context, event)
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            self.finish(context)
            return self.execute(context)
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            self.finish(context)
            return {'CANCELLED'}
        if event.type == 'MOUSEMOVE':
            self.update_mouse(event)
            if 'RAYCAST' in self.__class__.options:
                self.raycast.update(context, self.mouse_pos)
        context.region.tag_redraw()
        self.post_modal(context, event)
        return {'RUNNING_MODAL'}

    def _draw(self, context: Context, callback) -> None:
        if context.area != self.ctx_area:
            return
        callback(context)


def get_operator_properties(op: Operator):
    builtin_op_rna = op.get_rna_type()
    props = builtin_op_rna.properties
    ok_props: dict[str, Property] = {name: prop for (name, prop) in props.items() if name not in {'rna_type'} and type(prop) not in {PointerProperty}}
    return ok_props


def create_op_wrapper(builtin_op, your_class, base_class, props_overwrite: dict = {}, copy_props: bool = True):
    ok_props = {}
    if copy_props:
        ok_props = get_operator_properties(builtin_op)

    op = type(
        your_class.__name__,
        (your_class, base_class, Operator),
        {
            'original_bl_operator': builtin_op,
            'prop_names': tuple(name for name in ok_props.keys()),
            '__annotations__': {
                name: getattr(BPY_PROPS, type(prop).__name__)(
                    **get_bpy_prop_kwargs(prop, props_overwrite.get(name, None))
                ) for name, prop in ok_props.items()
            },
            'get_props_dict': lambda s: {name: getattr(s, name) for name in s.prop_names},
        } # builtin_op.__annotations__,
    )
    dynamic_operators.append(op)
    register_class(op)
    return op


def create_op_props_popup_wrapper(builtin_op, your_class) -> Operator:
    create_op_wrapper(builtin_op, your_class, OpExecutePropsWrapper, copy_props=True)


def create_op_modal_exec_wrapper(builtin_op, your_class, props_overwrite={}, copy_props=True):
    create_op_wrapper(builtin_op, your_class, OpModalOnReleaseExecuteWrapper, props_overwrite=props_overwrite, copy_props=copy_props)


'''
def register():
    pass

def unregister():
    for op in dynamic_operators:
        unregister_class(op)
'''
