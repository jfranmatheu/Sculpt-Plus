import bpy
from bpy.types import Property, Brush, BrushCapabilitiesSculpt, BrushCapabilities, BrushCurvesSculptSettings, BrushTextureSlot
from bpy.types import (
    IntProperty, #IntVectorProperty,
    FloatProperty, #FloatVectorProperty,
    BoolProperty, #BoolVectorProperty,
    StringProperty,
    PointerProperty, CollectionProperty)

from typing import Dict, Tuple, List, Set, Union
# from os.path import dirname, join

# outfile: str = join(dirname(__file__), 'generated.py')
outfile = bpy.data.texts.new('generated.py')


sub_property_groups = ('brush_capabilities', 'mask_texture_slot', 'sculpt_capabilities', '')

exclude_pattern_starts = ('bl_', 'curves_', 'vertex', 'weight', 'use_paint', 'image_paint')
exclude_pattern_contain = ('gpencil', 'uv', 'overlay', 'grease_pencil')
exclude_set = {
    'users',
    'tag',
    'use_fake_user',
    'is_evaluated',
    'name_full',
    'use_extra_user',
    'is_library_indirect',
    'library',
    'is_embedded_data',
    'override_library',
    'asset_data',
    'library_weak_reference',
    'preview',
    'toolset_id'
}

brush_pg_ok = (
    BrushCapabilities, BrushCapabilitiesSculpt, BrushCurvesSculptSettings, BrushTextureSlot
)
sculpt_brush_types: Tuple[Tuple[type, str]] = (
    # (Brush, ''),
    # (BrushCapabilities, 'brush_capabilities'),
    (BrushCapabilitiesSculpt, 'brush_capabilities'),
    (BrushCurvesSculptSettings, 'curves_sculpt_settings'),
    (BrushTextureSlot, 'texture_slot')
)
exclude_prop_types = (PointerProperty, CollectionProperty)


blproptype_to_pyproptype = {
    'ENUM': 'str',
    'FLOAT': 'float',
    'BOOLEAN': 'bool',
    'STRING': 'str',
    'INT': 'int'
}


brush_properties: Dict[str, Property] = Brush.bl_rna.properties

code = """import bpy
from mathutils import Vector, Color

class BaseBrush:
"""
prop_attributes = []
prop_id_type_value = []
for prop_idname, prop in brush_properties.items():
    if prop_idname in exclude_set:
        continue
    if any([pattern in prop_idname for pattern in exclude_pattern_contain]):
        continue
    if prop_idname.startswith(exclude_pattern_starts):
        continue
    if isinstance(prop, CollectionProperty):
        continue
    if isinstance(prop, PointerProperty):
        if isinstance(prop.fixed_type, brush_pg_ok):
            print(prop_idname, prop)
            pass
        continue
    
    prop_type = blproptype_to_pyproptype[prop.type]
    prop_value = str(prop.default)

    if prop_type in {'float', 'int'} and prop.is_array:
        if 'COLOR' in prop.subtype:
            prop_type = 'Vector' # 'Color'
            prop_value = f'Vector({tuple(prop.default_array)})'
        else:
            prop_type = 'Vector'
            prop_value = f'Vector({tuple(prop.default_array)})'
    elif prop_type == 'str':
        def_string = 'NONE'
        prop_value = f'"{prop_value if prop_value else def_string}"'

    prop_attributes.append(f'"{prop_idname}"')
    prop_id_type_value.append((prop_idname, prop_type, prop_value))
    code += f'\t{prop_idname}: {prop_type}\n'


# SUB PROPS. CHANGE... Only texture is important here.
'''
for (pg_type, pg_idname) in sculpt_brush_types:
    pg_properties: Dict[str, Property] = pg_type.bl_rna.properties
    for prop_idname, prop in pg_properties.items():
        if prop_idname.startswith('_'):
            continue
        if prop_idname in exclude_set:
            continue
        if any([pattern in prop_idname for pattern in exclude_pattern_contain]):
            continue
        if prop_idname.startswith(exclude_pattern_starts):
            continue
        if isinstance(prop, CollectionProperty):
            continue
        if isinstance(prop, PointerProperty):
            if isinstance(prop.fixed_type, brush_pg_ok):
                print(prop_idname, prop)
                pass
            continue
        
        prop_type = blproptype_to_pyproptype[prop.type]
        prop_value = str(prop.default)

        if prop_type in {'float', 'int'} and prop.is_array:
            if 'COLOR' in prop.subtype:
                prop_type = 'Vector' # 'Color'
                prop_value = f'Vector({tuple(prop.default_array)})'
            else:
                prop_type = 'Vector'
                prop_value = f'Vector({tuple(prop.default_array)})'
        elif prop_type == 'str':
            prop_value = f'"{prop_value}"'

        prop_attributes.append(f'"{prop_idname}"')
        prop_id_type_value.append((prop_idname, prop_type, prop_value))
        code += f'\t{prop_idname}: {prop_type}\n'
'''

code += '\n'
code += '\t_attributes = ('
code += ', '.join(prop_attributes)
code += ')'

code += '\n'
code += "\tdef __init__(self):\n"
for (prop_idname, prop_type, prop_value) in prop_id_type_value:
    code += f'\t\tself._{prop_idname}: {prop_type} = {prop_value}\n'

code += '\n'
for (prop_idname, prop_type, prop_value) in prop_id_type_value:
    code += f"""
\t@property
\tdef {prop_idname}(self) -> {prop_type}:
\t\treturn self._{prop_idname}"""
    code += f"""
\t@{prop_idname}.setter
\tdef {prop_idname}(self, value: {prop_type}) -> None:
\t\tself._{prop_idname}: {prop_type} = value"""


#with open(outfile, 'w') as f:
#    f.write(code)

outfile.from_string(code)
