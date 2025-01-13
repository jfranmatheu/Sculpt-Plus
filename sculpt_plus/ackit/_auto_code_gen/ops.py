'''
    OPS.PY GENERATION
'''

import bpy
from bpy.ops import _BPyOpsSubModOp

from collections import defaultdict
from string import Template
from pathlib import Path

from ..globals import GLOBALS

# ----------------------------------------------------------------
# IMPORT CODE.

from .._register.reg_types.ops import Operator
from .._register import BlenderTypes


ot_original_name_relation: dict[str, Operator] = {}



class OpTypeEnum:
    @property
    def operator(self) -> Operator:
        return ot_original_name_relation[self.name]

    def run(self, **operator_properties: dict) -> None:
        self.operator.run(**operator_properties)

    def run_invoke(self, **operator_properties: dict) -> None:
        self.operator.run_invoke(**operator_properties)

    def draw_in_layout(self, layout, label: str | None = None, op_props: dict | None = None, **draw_kwargs):
        return self.operator.draw_in_layout(layout, label, op_props=op_props, **draw_kwargs)

    def __call__(self, *args, **kwargs) -> None:
        return self.operator.run_invoke(*args, **kwargs)


def register():
    for cls in BlenderTypes.Operator.get_classes():
        ot_original_name_relation[cls.original_name] = cls

def unregister():
    ot_original_name_relation.clear()



# ----------------------------------------------------------------


def codegen__ops_py(ops_py_filepath: Path = None, filter_module: callable = None) -> None:
    from .._register import BlenderTypes
    
    if ops_py_filepath is None:
        ops_submodule = GLOBALS.ADDON_SOURCE_PATH / 'ops'
        if ops_submodule.exists() and ops_submodule.is_dir():
            ops_py_filepath = ops_submodule / '__init__.py'
        else:  
            ops_py_filepath = GLOBALS.ADDON_SOURCE_PATH / GLOBALS.CodeGen.OPS

    def prop_type_to_py_type(prop) -> tuple:
        # bpy_prop_name = prop.function.__name__
        # default = prop.keywords.get('default', None)
        # is_vector = 'Vector' in bpy_prop_name
        value = prop.default
        ptype = prop.type
        is_vector = 'VECTOR' in ptype
        type_str = 'None'
        if 'FLOAT' in ptype:
            type_str = 'float'
            if value is None: value = 0.0
        elif 'INT' in ptype:
            type_str = 'int'
            if value is None: value = 0
        elif 'BOOL' in ptype:
            type_str = 'bool'
            if value is None: value = False
        if is_vector:
            value = prop.default_array
            if value is not None:
                value = tuple(value)
                size = len(value)
            else:
                size = prop.keywords.get('size', 3)
                value = tuple([value]*size)
            type_str = 'tuple[%s]' % (', '.join([type_str for i in range(size)])[:-2])
        elif ptype == 'STRING':
            type_str = 'str'
            value = f"'{value}'"
        elif ptype == 'ENUM':
            type_str = 'str'
            if value is None: value = '""'
            value = f"'{value}'"
        return type_str, value
        if 'Pointer' in bpy_prop_name:
            # print(prop.type, prop.fixed_type.name)
            return 'bpy.types.' + prop.fixed_type.name
        if 'Collection' in bpy_prop_name:
            #print(prop, prop.fixed_type, dir(prop.fixed_type), prop.fixed_type.original_idname)
            return f'list' # [{prop.fixed_type.original_idname}]'
        return 'None'

    example_op = None
    #properties_per_ot = defaultdict(list)
    with ops_py_filepath.open('w', encoding='utf-8') as f:
        f.write("# /ops.py\n# Code automatically generated!\n")
        f.write('from enum import Enum, auto\n\n')
        f.write(f'from {__package__}.ops import OpTypeEnum\n\n')
        f.write('__all__ = ["OPS",]\n\n\n')

        f.write('\n\nclass OPS(OpTypeEnum, Enum):\n')
        #for subtype_name, code in code_per_ops_subtype.items():
        #    f.write(f'\tclass {subtype_name}(OpTypeEnum, Enum):\n')
        #    f.write(code)

        op_classes = BlenderTypes.Operator.get_classes()

        if filter_module is not None:
            if callable(filter_module):
                op_classes = [
                    cls for cls in op_classes if filter_module(cls)
                ]
            elif isinstance(filter_module, str):
                op_classes = [
                    cls for cls in op_classes if filter_module in cls.__module__
                ]

        if len(op_classes) == 0:
            f.write('\tpass')
            return

        for ot_cls in op_classes:
            ori_name: str = ot_cls.original_name
            f.write(f'\t{ori_name} = auto()\n')
            if example_op is None:
                example_op = f'OPS.{ori_name}'


        # WRITE OPERATOR CALLS WITH TYPING FOR PROPERTIES.
        f.write('\n\n')

        def stringify_op_prop(prop_name, prop):
            type_str, value = prop_type_to_py_type(prop)
            return f"{prop_name}: {type_str} = {value}"

        for ot_cls in op_classes:
            bl_op: _BPyOpsSubModOp = eval('bpy.ops.' + ot_cls.bl_idname).get_rna_type()
            # print(ot_cls, type(ot_cls), dir(ot_cls), ot_cls.as_keywords(ot_cls.bl_rna), ot_cls.bl_rna)
            ori_name: str = ot_cls.original_name

            op_props = [
                (prop_name, *prop_type_to_py_type(prop))
                for prop_name, prop in bl_op.properties.items() if prop_name not in {'rna_type'} and not prop.is_hidden and not prop.is_readonly and not prop.is_runtime
            ]

            f.write(f"def {ot_cls.bl_idname.split('.')[1]}(exec_context: str = 'INVOKE_DEFAULT', undo: bool = True{''.join([f', {pt[0]}: {pt[1]} = {pt[2]}' for pt in op_props])}) -> None: OPS.{ori_name}(exec_context, undo{''.join([f', {pt[0]}={pt[0]}' for pt in op_props])})\n")


        f.write(f"""\n\n''' Usage example:

from addon_module import ops as addon_module_ops
addon_module_ops.{example_op}()

OR...

from addon_module.ops import Ops
{example_op}()  # directly run execute the operator.
{example_op}.operator.run_invoke()  # access to the operator class and run invoke the operator.
'''""")
