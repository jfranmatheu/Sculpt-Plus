from string import Template
from collections import defaultdict
from pathlib import Path
import inspect
import re

import bpy
from bpy.types import AnyType, PropertyGroup, BlenderRNA
from bpy.props import _PropertyDeferred

from ..globals import GLOBALS


class RootPropertyGroup:
    bpy_type: AnyType
    prop_name: str
    original_idname: str
    data_path: str
    bl_rna: BlenderRNA


prefs_getter_template = Template("""
\t@staticmethod
\tdef Preferences(context: bpy.types.Context) -> ${cls_name}:
\t\treturn context.preferences.addons['${package_name}'].preferences
""")

coll_class_wrapper_template = Template("""
class ${class_name}_Collection:
\tdef __getitem__(coll, index: int) -> '${class_name}': pass
\tdef add(coll) -> '${class_name}': pass
\tdef remove(coll, item_index: int) -> None: pass
\tdef clear(coll) -> None: pass
\tdef move(coll, item_index_1: int, item_index_2: int) -> None: pass
""")

pg_class_wrapper_template = Template("""
class ${class_name}:${comment}
${property_defs}
""")

pg_class_get_data_template = Template("""
\t@classmethod
\tdef get_data(cls, context: Context) -> '${class_name}':
\t\tbpy_type_data: Extended${bpy_type} = context.${bpy_type_context}
\t\tif hasattr(bpy_type_data, \"${pg_data_idname}\"): 
\t\t\t\treturn bpy_type_data.${pg_data_idname}

""")

example_typing_template = Template("""
\n\n# EXAMPLE ++++++++++++++++++++++++++++++++++++++++++++++++++\n'''
from ${addon_module}.types import ${alias_name}_types

# Your property_group variable will have the correct typing. :-)
${alias_name}_${pg_name_lower} = ${alias_name}_types.${pg_name}(context)
${prop_name} = property_group.${prop_name}
print(${prop_name})
'''\n""")


def prop_type_to_py_type(prop) -> str:
    if isinstance(prop, _PropertyDeferred):
        bpy_prop_name = prop.function.__name__
        is_array = 'Vector' in bpy_prop_name
    else:
        # print(dir(prop))
        bpy_prop_name = type(prop).__name__
        is_array = hasattr(prop, 'is_array') and prop.is_array

    if 'Float' in bpy_prop_name:
        return 'tuple[float]' if is_array else 'float'
    if 'Int' in bpy_prop_name:
        return 'tuple[int]' if is_array else 'int'
    if 'Bool' in bpy_prop_name:
        return 'tuple[bool]' if is_array else 'bool'
    if 'String' in bpy_prop_name or 'Enum' in bpy_prop_name:
        return 'str'
    if 'Pointer' in bpy_prop_name:
        if isinstance(prop, _PropertyDeferred):
            return f'{prop.keywords["type"].__name__}'
        else:
            if hasattr(prop.fixed_type, 'original_idname'):
                return prop.fixed_type.original_idname
            # print(prop.type, prop.fixed_type.name)
            return 'bpy.types.' + prop.fixed_type.name
    if 'Collection' in bpy_prop_name:
        if isinstance(prop, _PropertyDeferred):
            return f'{prop.keywords["type"].__name__}_Collection'
        else:
            #print(prop, prop.fixed_type, dir(prop.fixed_type), prop.fixed_type.original_idname)
            return f'{prop.fixed_type.original_idname}_Collection' # f'list[{prop.fixed_type.original_idname}]'
    return 'None'


def codegen__types_py(types_filepath: str | Path | None = None, filter_module: str | None = None, types_alias: str = GLOBALS.ADDON_MODULE_SHORT) -> None:
    """Generates the Typing for PropertyGroup types.

    Args:
        types_filepath (str): path relative to the addon source where to write your types.py file. Defaults to '/types.py' (source root).
    """
    # Get PropertyGroup classes in the proper order.
    from .._register._register import BlenderTypes
    pg_classes = BlenderTypes.PropertyGroup.get_classes()
    prefs_cls = BlenderTypes.AddonPreferences.get_classes()[0]
    pg_classes.append(prefs_cls)

    if pg_classes == []:
        # SAD. No PropertyGroup classes to process... :-(
        return

    parent_classes = set()
    for pg_cls in pg_classes:
        cls_names_to_skip = {pg_cls.__name__, 'object', 'bpy_struct', 'AddonPreferences', 'PropertyGroup', 'BaseType', 'DrawExtension', 'BaseUI'}
        if pg_cls.__name__.startswith('_'):
            cls_names_to_skip.add(pg_cls.__name__[1:])
        if hasattr(pg_cls, 'original_cls'):
            cls_names_to_skip.add(pg_cls.original_cls.__name__)
        for parent_cls in pg_cls.mro():
            if parent_cls.__name__ in cls_names_to_skip:
                continue
            parent_classes.add(parent_cls)

    if parent_classes != set():
        pg_classes.extend(list(parent_classes))

    from ...auto_load import get_ordered_pg_classes_to_register
    pg_sorted_classes: list[PropertyGroup] = get_ordered_pg_classes_to_register(pg_classes)

    pg_classes: set[PropertyGroup] = set(pg_classes)
    # pg_names: set[str] = {pg.__name__ for pg in pg_sorted_classes}
    pg_class_names: set[str] = {pg.__name__ for pg in pg_sorted_classes}

    if filter_module is not None:
        if callable(filter_module):
            pg_sorted_classes = [
                cls for cls in pg_sorted_classes if filter_module(cls)
            ]
        elif isinstance(filter_module, str):
            pg_sorted_classes = [
                cls for cls in pg_sorted_classes if filter_module in cls.__module__
            ]

    # Search for PropertyGroup used as CollectionProperty inside other PropertyGroup class.
    classes_used_as_collection = []
    for pg in pg_sorted_classes:
        if not hasattr(pg, 'bl_rna'):
            continue
        for prop_idname, prop in pg.bl_rna.properties.items():
            if prop_idname in {'rna_type', 'name'}:
                continue
            if 'Collection' not in type(prop).__name__:
                continue
            classes_used_as_collection.append(prop.fixed_type.original_idname)


    # WRITE TO FILE. ---------------------------
    if types_filepath is None:
        types_filepath = GLOBALS.ADDON_SOURCE_PATH / GLOBALS.CodeGen.TYPES
    elif isinstance(types_filepath, str):
        types_filepath = Path(types_filepath)
    addon_module_name = GLOBALS.ADDON_MODULE

    with types_filepath.open('w') as f:
        f.write('""" File generated automatically by ackit (Addon Creator Kit). """\n')
        # f.write('import bpy\n')#from {addon_module_name}.addon_utils.prop import PGType\n\n')
        f.write(f'import numpy\n')
        f.write(f'import typing\n')
        f.write(f'from typing import List, Set, Tuple, Dict, Any\n\n')
        f.write(f'import bpy\nimport bpy_types\n')

        if GLOBALS.BLENDER_VERSION >= (4, 2, 0):
            f.write("import bl_ext\n")

        if filter_module is None:
            from .._register.reg_helpers.help_property import to_register_properties
            import_bpy_types = {'Context'}
            for bpy_type, props_wrappers in to_register_properties.items():
                import_bpy_types.add(bpy_type.__name__)
                for prop_wrapper in props_wrappers:
                    if isinstance(prop_wrapper.property, _PropertyDeferred):
                        prop_type = prop_type_to_py_type(prop_wrapper.property)
                        # print(prop_type, prop_type.__name__)
                        if hasattr(bpy.types, prop_type):
                            import_bpy_types.add(prop_type)

            f.write(f'from bpy.types import {", ".join(import_bpy_types)}\n\n')

        if len(classes_used_as_collection) != 0:
            f.write('\n""" Util classes to have CollectionProperty types typing: """')
            # Write the CollectionProperty classes we found with a nice template.
            for coll_cls_name in classes_used_as_collection:
                f.write(
                    coll_class_wrapper_template.substitute(
                        class_name=coll_cls_name,
                    )
                )

        # Just to store some PropertyGroup to use for the example code.
        example_pg_prop = None

        # For the Data Enumerator utility.
        root_pg_classes: list[RootPropertyGroup] = []

        # Write to file the property groups.
        f.write('\n""" Addon-Defined PropertyGroup: """')
        for pg in pg_sorted_classes:
            # print(pg, pg.bl_rna.properties)
            # is_root = pg.is_root
            is_root: bool = hasattr(pg, 'is_root') and pg.is_root

            if hasattr(pg, 'bl_rna'):
                f.write(
                    pg_class_wrapper_template.substitute(
                        class_name=pg.original_idname if hasattr(pg, 'original_idname') else pg.__name__,
                        comment=f'\n\t# Root PG, attached to bpy.types.{pg.bpy_type.__name__}' if is_root else '',
                        property_defs='\n'.join([
                            f'\t{prop_idname}: {prop_type_to_py_type(prop)}'
                                for prop_idname, prop in pg.bl_rna.properties.items() # pg.__annotations__.items()
                                if prop_idname not in {'rna_type'}
                                #if isinstance(prop, _PropertyDeferred) and prop_idname not in {'rna_type'}
                        ]),

                    )
                )
            elif pg in parent_classes:
                f.write(
                    pg_class_wrapper_template.substitute(
                        class_name=pg.__name__,
                        comment='',
                        property_defs=''

                    )
                )
            else:
                continue

            ori_pg = getattr(pg, 'original_cls', None)
            if ori_pg is None and pg in parent_classes:
                ori_pg = pg
            if ori_pg is not None:
                addon_type_pattern = f'{GLOBALS.ADDON_MODULE}\.[\w._]+'

                # Include methods.
                for method_name, method in ori_pg.__dict__.items():
                    if (inspect.isfunction(method) or inspect.ismethod(method)) and not method_name.startswith("__"):
                        method_signature = str(inspect.signature(method))
                        # print(">>>>>>>>>>>>>>>>>>>", method_signature)
                        matches: list[str] = re.findall(addon_type_pattern, method_signature)
                        # print("HELLO", ret_signature, matches)
                        for match in matches:
                            pg_cls_name = match.split('.')[-1]
                            if pg_cls_name in pg_class_names:
                                method_signature = method_signature.replace(match, pg_cls_name)

                        f.write(f"\tdef {method_name}{method_signature}:\n\t\tpass\n\n")

                        # if '->' in method_signature:
                        #     params, ret = method_signature.split(' -> ')
                        #     if ret.startswith(GLOBALS.ADDON_MODULE):
                        #         _type = ret.split('.')[-1]
                        #         if _type in pg_class_names:
                        #             ret = _type
                        # else:
                        #     params = method_signature
                        #     ret = 'None'
                        # f.write(f"\tdef {method_name}{params} -> {ret}:\n\t\tpass\n\n")

                def _fix_ret_annot(f_signature, ret_annot) -> str:
                    if ret_annot in pg_classes:
                        pg_cls_name = ret_annot.__name__
                        return str(f_signature).split('->')[0] + f"-> {pg_cls_name}"
                    elif f'{GLOBALS.ADDON_MODULE}.' in str(ret_annot): # isinstance(ret_annot, UnionType) and
                        ret_signature = str(ret_annot)
                        matches: list[str] = re.findall(addon_type_pattern, ret_signature)
                        # print("HELLO", ret_signature, matches)
                        for match in matches:
                            pg_cls_name = match.split('.')[-1]
                            ret_signature = ret_signature.replace(match, pg_cls_name)
                        return str(f_signature).split('->')[0] + f"-> {ret_signature}"
                    return f_signature

                # Include properties
                for prop_name, prop in ori_pg.__dict__.items():
                    if isinstance(prop, property):
                        if prop.fget:
                            fget_signature = inspect.signature(prop.fget)
                            if ret_annot := fget_signature.return_annotation:
                                fget_signature = _fix_ret_annot(fget_signature, ret_annot)
                                # print("ret annot:", ret_annot)
                            f.write(f"\t@property\n")
                            f.write(f"\tdef {prop_name}{fget_signature}: pass\n\n")
                        if prop.fset:
                            fset_signature = inspect.signature(prop.fset)
                            if ret_annot := fset_signature.return_annotation:
                                fset_signature = _fix_ret_annot(fset_signature, ret_annot)
                            f.write(f"\t@{prop_name}.setter\n")
                            f.write(f"\tdef {prop_name}{fset_signature}: pass\n\n")

            # If it's a root PropertyGroup, we need to add a get_path() class method
            # to it to get the corresponding data with typing!.
            if is_root:
                pg: RootPropertyGroup
                bpy_type_context, pg_data_idname = pg.data_path.split('.')
                f.write(
                    pg_class_get_data_template.substitute(
                        class_name=pg.original_idname if hasattr(pg, 'original_idname') else pg.__name__,
                        pg_data_idname=pg_data_idname,
                        bpy_type=pg.bpy_type.__name__,
                        bpy_type_context=bpy_type_context
                    )
                )

                root_pg_classes.append(pg)

        # Write the extended bpy type classes.
        # pack root PG types by its root bpy_type.
        # pg_types_per_bpy_type: dict[AnyType, list[RootPropertyGroup]] = defaultdict(list)
        # for root_pg_cls in root_pg_classes:
        #     pg_types_per_bpy_type[root_pg_cls.bpy_type].append(root_pg_cls)
        # for bpy_type, pg_types in pg_types_per_bpy_type.items():
        #     f.write(f'\n\nclass {bpy_type.__name__}:')
        #     for pg_type in pg_types:
        #         f.write(f'\n\t{pg_type.prop_name}: {pg_type.original_idname}')

        if filter_module is None:
            f.write("\n\n# ++++++++++++++++++++++++++++++++++++++++++++++++++\n")
            f.write('""" Extended bpy.types classes by the addon: """')
            for bpy_type, props_wrappers in to_register_properties.items():
                f.write(f'\n\nclass Extended{bpy_type.__name__}({bpy_type.__name__}):')
                for prop_wrapper in props_wrappers:
                    # print(prop_wrapper.property, prop_type_to_py_type(prop_wrapper.property))
                    f.write(f'\n\t{prop_wrapper.prop_name}: {prop_type_to_py_type(prop_wrapper.property)}')

            if to_register_properties:
                f.write('\n\nclass ExtendedTypes:')
                for bpy_type in to_register_properties.keys():
                    f.write(f'\n\t{bpy_type.__name__} = Extended{bpy_type.__name__}')

        # Write the Data enumerator.
        f.write("\n\n# ++++++++++++++++++++++++++++++++++++++++++++++++++\n")
        f.write('""" Root PropertyGroups (linked directly to any bpy.types): """\n')
        f.write('class RootPG:')
        f.write(prefs_getter_template.substitute(cls_name=f"{GLOBALS.ADDON_MODULE_UPPER}_AddonPreferences", package_name=GLOBALS.ADDON_MODULE))
        if len(root_pg_classes) == 0:
            pass
        else:
            skip_root_properties = {f'{GLOBALS.ADDON_MODULE_SHORT}_ui_panel_toggles'}
            for root_pg_cls in root_pg_classes:
                bpy_type_context, pg_data_idname = root_pg_cls.data_path.split('.')
                if pg_data_idname in skip_root_properties:
                    continue
                if bpy_type_context == 'scene':
                    bpy_type_context = 'SCN'
                elif bpy_type_context == 'window_manager':
                    bpy_type_context = 'WM'

                if example_pg_prop is None:
                    if not hasattr(pg, 'bl_rna'):
                        continue
                    for prop_idname in pg.bl_rna.properties.keys():
                        if prop_idname not in {'rna_type', 'name'}:
                            example_pg_prop = (pg, bpy_type_context, prop_idname)
                            break

                f.write(f'\n\t{bpy_type_context} = {root_pg_cls.original_idname}.get_data')

        f.write(f'\n\n# Alias:\n{types_alias}_types = RootPG')

        # Write example code.
        if filter_module is None:
            f.write("\n\n# ++++++++++++++++++++++++++++++++++++++++++++++++++\n")
            if example_pg_prop is not None:
                pg, bpy_type, prop_idname = example_pg_prop
                f.write(
                    example_typing_template.substitute(
                        addon_module=GLOBALS.ADDON_MODULE,
                        alias_name=types_alias,
                        pg_name=bpy_type, # pg.original_idname,
                        pg_name_lower=bpy_type.lower(),
                        prop_name=prop_idname
                    )
                )
