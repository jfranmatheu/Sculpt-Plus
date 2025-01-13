# OPERATOR DECORATORS.
from bpy_extras.io_utils import ExportHelper, ImportHelper
from bpy.props import StringProperty

from ..reg_types import RegType
from ...globals import GLOBALS


def ops_io(helper_cls, file_formats: tuple[str]):
    def decorator(deco_func):
        kwargs = {
            'bl_options': {'PRESET', 'UNDO'},
            'action': lambda op, ctx: deco_func(ctx, op.filepath),
        }
        if len(file_formats) == 1:
            kwargs['filename_ext'] = f".{file_formats[0]}"

        kwargs['__annotations__'] = {
            'filter_glob': StringProperty(
                default='*.' + ';*.'.join([file_format.lower() for file_format in file_formats]),
                options={'HIDDEN'}
            )
        }
        return OpsDecorators.FROM_FUNCTION(deco_func, ext_classes=(helper_cls,), **kwargs)
    return decorator


class OpsDecorators:
    IMPORT = lambda *file_formats: ops_io(ImportHelper, file_formats)
    EXPORT = lambda *file_formats: ops_io(ExportHelper, file_formats)

    def FROM_FUNCTION(deco_func: callable, ext_classes: tuple = (), **kwargs) -> RegType.OPS.ACTION:
        if 'action' not in kwargs:
            kwargs['action'] = lambda op, ctx: deco_func(ctx)
        new_op = type(
            deco_func.__name__,
            (*ext_classes, RegType.OPS.ACTION),
            {
                'label': deco_func.__name__.replace('_', ' ').title(),
                'bl_description': deco_func.__doc__ if deco_func.__doc__ is not None else '',
                **kwargs
            }
        )
        new_op.__module__ = deco_func.__module__
        return new_op
