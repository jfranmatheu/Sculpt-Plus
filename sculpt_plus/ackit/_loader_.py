import os
import bpy
import sys
import typing
import inspect
import pkgutil
import importlib
from pathlib import Path

__all__ = (
    "init",
    "register",
    "unregister",
)

blender_version = bpy.app.version

modules = None
ordered_classes = None
registered = False

def init_modules():
    global modules
    global ordered_classes
    global registered

    if modules is not None:
        cleanse_modules()

    modules = get_all_submodules(Path(__file__).parent)
    ordered_classes = get_ordered_classes_to_register(modules)
    registered = False

    for module in modules:
        if module.__name__ == __name__:
            continue
        if hasattr(module, "init_pre"):
            module.init_pre()

    for module in modules:
        if module.__name__ == __name__:
            continue
        if hasattr(module, "init"):
            module.init()

    for module in modules:
        if module.__name__ == __name__:
            continue
        if hasattr(module, "init_post"):
            module.init_post()


def cleanse_modules():
    # Based on https://devtalk.blender.org/t/plugin-hot-reload-by-cleaning-sys-modules/20040
    global modules

    sys_modules = sys.modules
    sorted_addon_modules = sorted([module.__name__ for module in modules])
    for module_name in sorted_addon_modules:
        del sys_modules[module_name]


def register_modules():
    global registered
    global modules

    if modules is None:
        init_modules()
    if registered:
        return

    for cls in ordered_classes:
        bpy.utils.register_class(cls)

    for module in modules:
        if module.__name__ == __name__:
            continue
        if hasattr(module, "register_pre"):
            module.register_pre()

    for module in modules:
        if module.__name__ == __name__:
            continue
        if hasattr(module, "register"):
            module.register()

    for module in modules:
        if module.__name__ == __name__:
            continue
        if hasattr(module, "register_post"):
            module.register_post()

    registered = True

    from .globals import GLOBALS
    if GLOBALS.check_in_development():
        print("[Sculpt+] Generating types, ops and icons...")
        from ._auto_code_gen import AddonCodeGen
        AddonCodeGen.TYPES(types_alias='splus')
        AddonCodeGen.OPS()
        AddonCodeGen.ICONS()


def unregister_modules():
    global modules
    global registered
    if not registered:
        return

    for cls in reversed(ordered_classes):
        bpy.utils.unregister_class(cls)

    for module in modules:
        if module.__name__ == __name__:
            continue
        if hasattr(module, "unregister_pre"):
            module.unregister_pre()

    for module in modules:
        if module.__name__ == __name__:
            continue
        if hasattr(module, "unregister"):
            module.unregister()

    for module in modules:
        if module.__name__ == __name__:
            continue
        if hasattr(module, "unregister_post"):
            module.unregister_post()

    # Clear modules.
    for module in modules:
        if module.__name__ in sys.modules:
            del sys.modules[module.__name__]

    registered = False


# Import modules
#################################################

def get_all_submodules(directory):
    return list(iter_submodules(directory, __package__))

def iter_submodules(path, package_name):
    for name in sorted(iter_submodule_names(path)):
        yield importlib.import_module("." + name, package_name)

def iter_submodule_names(path, root=""):
    for _, module_name, is_package in pkgutil.iter_modules([str(path)]):
        if is_package:
            sub_path = path / module_name
            sub_root = root + module_name + "."
            yield from iter_submodule_names(sub_path, sub_root)
        else:
            yield root + module_name


# Find classes to register
#################################################

def get_ordered_classes_to_register(modules):
    return toposort(get_register_deps_dict(modules))

def get_register_deps_dict(modules):
    my_classes = set(iter_my_classes(modules))
    my_classes_by_idname = {cls.bl_idname : cls for cls in my_classes if hasattr(cls, "bl_idname")}

    deps_dict = {}
    for cls in my_classes:
        deps_dict[cls] = set(iter_my_register_deps(cls, my_classes, my_classes_by_idname))
    return deps_dict

def iter_my_register_deps(cls, my_classes, my_classes_by_idname):
    yield from iter_my_deps_from_annotations(cls, my_classes)
    yield from iter_my_deps_from_parent_id(cls, my_classes_by_idname)

def iter_my_deps_from_annotations(cls, my_classes):
    for value in typing.get_type_hints(cls, {}, {}).values():
        dependency = get_dependency_from_annotation(value)
        if dependency is not None:
            if dependency in my_classes:
                yield dependency

def get_dependency_from_annotation(value):
    if isinstance(value, bpy.props._PropertyDeferred):
        return value.keywords.get("type")
        prop_type: str = value.function.__name__
        prop_type = prop_type.replace('Property', '').upper()
        if prop_type in {'POINTER', 'COLLECTION'}:
            type = value.keywords.get('type')
            attr_name = value.keywords.get('attr')
            return type
    return None

def iter_my_deps_from_parent_id(cls, my_classes_by_idname):
    if issubclass(cls, bpy.types.Panel):
        parent_idname = getattr(cls, "bl_parent_id", None)
        if parent_idname is not None:
            parent_cls = my_classes_by_idname.get(parent_idname)
            if parent_cls is not None:
                yield parent_cls

def iter_my_classes(modules):
    base_types = get_register_base_types()
    for cls in get_classes_in_modules(modules):
        if any(issubclass(cls, base) for base in base_types):
            if not getattr(cls, "is_registered", False):
                yield cls

def get_classes_in_modules(modules):
    classes = set()
    for module in modules:
        for cls in iter_classes_in_module(module):
            classes.add(cls)
    return classes

def iter_classes_in_module(module):
    for value in module.__dict__.values():
        if inspect.isclass(value):
            yield value

def get_register_base_types():
    return set(getattr(bpy.types, name) for name in [
        "Panel", "Operator",
        "Header", "Menu",
        "UIList",
    ])


# Find order to register to solve dependencies
#################################################

def toposort(deps_dict):
    sorted_list = []
    sorted_values = set()
    while len(deps_dict) > 0:
        unsorted = []
        for value, deps in deps_dict.items():
            if len(deps) == 0:
                sorted_list.append(value)
                sorted_values.add(value)
            else:
                unsorted.append(value)
        deps_dict = {value : deps_dict[value] - sorted_values for value in unsorted}
    return sorted_list

def get_ordered_pg_classes_to_register(classes) -> list:
    my_classes = set(classes)
    deps_dict = {}

    for cls in my_classes:
        deps_dict[cls] = set(
            iter_my_deps_from_annotations(cls, my_classes)
        )

    return toposort(deps_dict)


# CLASS GETTERS.

def get_pg_classes():
    global ordered_classes
    return [
        cls for cls in ordered_classes
        if issubclass(cls, bpy.types.PropertyGroup)
    ]
