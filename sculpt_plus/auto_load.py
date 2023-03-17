import bpy
import typing
import inspect
import pkgutil
import importlib
from pathlib import Path
import sys
import importlib


__all__ = (
    "init",
    "register",
    "unregister",
)

global sculpt_hotbar_classes
sculpt_hotbar_classes = []

if __package__ == 'sculpt_plus':
    blender_version = bpy.app.version

    modules = None
    ordered_classes = None

    def init(USE_DEV_ENVIRONMENT):
        from . import install_deps
        install_deps.install()

        global modules
        global ordered_classes
        global classes

        modules = get_all_submodules(Path(__file__).parent, USE_DEV_ENVIRONMENT)
        ordered_classes = get_ordered_classes_to_register(modules)
        classes = []

    def register():
        global modules
        global ordered_classes

        # When installing new version over... it tends to not run the init LMAO.
        if ordered_classes is None:
            init(False)

        for cls in ordered_classes:
            bpy.utils.register_class(cls)

        for module in modules:
            if module.__name__ == __name__:
                continue
            if hasattr(module, "register"):
                module.register()

    def unregister():
        global modules
        global ordered_classes
        global sculpt_hotbar_classes

        for cls in sculpt_hotbar_classes:
            bpy.utils.unregister_class(cls)

        for cls in reversed(ordered_classes):
            bpy.utils.unregister_class(cls)

        for module in modules:
            if module.__name__ == __name__:
                continue
            if hasattr(module, "unregister"):
                module.unregister()

        for module in modules:
            del sys.modules[module.__name__]


    # Import modules
    #################################################

    def get_all_submodules(directory, USE_DEV_ENVIRONMENT):
        return list(iter_submodules(directory, directory.name, USE_DEV_ENVIRONMENT))

    def iter_submodules(path, package_name, USE_DEV_ENVIRONMENT):
        #print(sys.modules.keys())
        for name in sorted(iter_submodule_names(path)):
            full_name = __package__ + '.' + name
            print(full_name)
            if not USE_DEV_ENVIRONMENT and full_name in sys.modules:
                #print("\t - reload")
                yield importlib.reload(sys.modules[full_name])
            else:
                #print("\t - import")
                yield importlib.import_module(full_name) # "." + name, package_name)

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
        if blender_version >= (2, 93):
            if isinstance(value, bpy.props._PropertyDeferred):
                return value.keywords.get("type")
        else:
            if isinstance(value, tuple) and len(value) == 2:
                if value[0] in (bpy.props.PointerProperty, bpy.props.CollectionProperty):
                    return value[1]["type"]
        return None

    def iter_my_deps_from_parent_id(cls, my_classes_by_idname):
        if bpy.types.Panel in cls.__bases__:
            parent_idname = getattr(cls, "bl_parent_id", None)
            if parent_idname is not None:
                parent_cls = my_classes_by_idname.get(parent_idname)
                if parent_cls is not None:
                    yield parent_cls

    def iter_my_classes(modules):
        base_types = get_register_base_types()
        for cls in get_classes_in_modules(modules):
            if any(base in base_types for base in cls.__bases__):
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
            "UIList","Panel","PropertyGroup","AddonPreferences","Gizmo","GizmoGroup","Operator"
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
