from os.path import dirname
from pathlib import Path
from typing import Dict, List, Tuple, Set
from string import Template
from uuid import uuid4

# Flags.
HARDCODE_SHADER_SOURCE = True
USE_IDS_FOR_SHADER_NAMES = True
ALL_IN_ONE = True

# Get some useful directory paths for the code generation.
PROJECT_DIR = Path(dirname(__file__))
SRC_DIR = PROJECT_DIR / 'sculpt_plus'
LIB_DIR = SRC_DIR / 'lib'
SHADERS_DIR = LIB_DIR / 'shaders'
SHADERS_FRAG_DIR = SHADERS_DIR / 'frag'
SHADERS_VERT_DIR = SHADERS_DIR / 'vert'
GPU_DIR = SRC_DIR / 'core/gpu'

# Get list of shaders from frag and vert directories.
vert_shaders_paths = [
    f for f in SHADERS_VERT_DIR.iterdir() if f.suffix == '.vert'
]
frag_shader_paths = [
    f for f in SHADERS_FRAG_DIR.iterdir() if f.suffix == '.frag'
]

# Read shader files and store them in a dict.
vert_shaders_source: Dict[str, str] = {}
frag_shaders_source: Dict[str, str] = {}
for shader_path in vert_shaders_paths:
    with shader_path.open('r') as f:
        shader_code = f.read()
    vert_shaders_source[shader_path.stem.upper()] = shader_code
for shader_path in frag_shader_paths:
    with shader_path.open('r') as f:
        shader_code = f.read()
    frag_shaders_source[shader_path.stem.upper()] = shader_code

# Read shader files and store them in a dict, but remove lines that starts with 'VERT_ID' and store the id in a variable.
shader_relationship: Dict[str, str] = dict()

def get_vert_id_from_frag_source(shader_code: str) -> str:
    vert_id = None
    for line in shader_code.splitlines():
        if line.startswith('// VERT_ID'):
            vert_id: str = line.split()[2]
            break
    return vert_id

def get_geom_id_from_frag_source(shader_code: str) -> str:
    geom_id = None
    for line in shader_code.splitlines():
        if line.startswith('// GEOM_ID'):
            geom_id: str = line.split()[2]
            break
    return geom_id

vert_names = set(vert_shaders_source.keys())
for frag_name, frag_source in frag_shaders_source.items():
    if frag_name in vert_names:
        # Frag name matches vert name.
        shader_relationship[frag_name] = frag_name
        continue
    vert_name: str = get_vert_id_from_frag_source(frag_source)
    if vert_name is not None:
        shader_relationship[frag_name] = vert_name

# Write enum classes for each shader name with its file path or source.
shader_types = ('vert', 'frag')
shaders_data = (vert_shaders_source, frag_shaders_source)

if ALL_IN_ONE:
    #####################################################################################
    #####################################################################################
    #####################################################################################
    vert_shaders_ids: Dict[str, str] = {name: uuid4().hex for name in vert_shaders_source.keys()}
    frag_shaders_ids: Dict[str, str] = {name: uuid4().hex for name in frag_shaders_source.keys()}

    shaders_ids = (vert_shaders_ids, frag_shaders_ids)

    output_path = SHADERS_DIR / 'shaders.py' #  GPU_DIR / 'shaders.py'

    with output_path.open('w') as file:
        def write(string: str, indent: int = 0):
            if indent > 0:
                file.write(' ' * (indent * 4))
            file.write(string + '\n')

        def write_block(lines: str, indent: int = 0):
            # Apply indent to every line, then write to file.
            for line in lines.splitlines():
                write(line, indent)

        write(
            """class ShType:
    POINT       = 'POINTS'
    LINE        = 'LINES'
    IMG         = 'TRI_FAN'
    TRI         = 'TRIS'
    RCT         = 'TRIS'
    SHAPE       = 'TRIS' """)

        shader_geom_id: Dict[str, str] = {}
        for frag_name, frag_source in frag_shaders_source.items():
            geom_id: str = get_geom_id_from_frag_source(frag_source)
            if geom_id is not None:
                shader_geom_id[frag_name] = geom_id

        # Wite vert shader and frag shader enum.
        # file.write('from enum import Enum\n')
        for shader_type, shader_data, shader_ids in zip(shader_types, shaders_data, shaders_ids):
            prefix: str = shader_type[0].upper()
            write(f"class {prefix}SH:")
            for name, source in shader_data.items():
                filtered_source = ''
                in_multi_line_comment = False
                for line in source.splitlines():
                    if in_multi_line_comment:
                        if '*/' in line:
                            in_multi_line_comment = False
                        continue
                    if '/*' in line:
                        in_multi_line_comment = True
                        continue
                    if not line or line in {'\n', ' ', '\t'}:
                        continue
                    if line.replace(' ', '').startswith('//'):
                        continue
                    line_split = line.split()
                    if line_split and line_split[0] in {'uniform', 'const', 'in', 'out', 'flat'}:
                        filtered_source += line
                    else:
                        filtered_source += (line + "\n")
                write_block(f'{prefix}{shader_ids[name]} = """{filtered_source}"""\n', indent=1)

        # Write gpu shader enum.
        write('from bpy.types import Image')
        write('from gpu_extras.batch import batch_for_shader as batsh')
        write('from gpu.types import GPUShader as gpush')
        write(f"class SH:")
        for frag_name, vert_name in shader_relationship.items():
            frag_id = shader_id = frag_shaders_ids[frag_name]
            vert_id = vert_shaders_ids[vert_name]
            write(f'GPUSH{shader_id} = gpush(VSH.V{vert_id},FSH.F{frag_id})', indent=1)

        # Write class for each shader.

        def get_pytype_from_shtype(u_type: str) -> Tuple[str, str]:
            if u_type == 'float':
                return 'float', 'float'
            if u_type.startswith('vec'):
                return 'tuple', 'float'
            if u_type == 'sampler2D':
                return 'Image', 'sampler'
            if u_type == 'int':
                return 'int', 'int'
            if u_type == 'bool':
                return 'bool', 'bool'
            return None, None

        for frag_name, vert_name in shader_relationship.items():
            frag_id = shader_id = frag_shaders_ids[frag_name]
            vert_id = vert_shaders_ids[vert_name]
            geom_id = shader_geom_id[frag_name]
            write(f'class SH{shader_id}():')
            write(f'sh=SH.GPUSH{shader_id}', indent=1)
            write(f'sh_type=ShType.{geom_id}', indent=1)
            write(f'sh_geom=ShGeom.{geom_id}', indent=1)

            # Find all uniforms in the shader source.
            frag_source = frag_shaders_source[frag_name]
            vert_source = vert_shaders_source[vert_name]

            """
            def init_props(self):
            ''' Init shader props. '''
                pass

            def get_inputs(self) -> Dict[str, Any]:
                ''' Get shader inputs. '''
                return {}

            def get_indices(self) -> Union[Tuple[Tuple[int]], None]:
                ''' Get shader indices. '''
                return None
            """

            # Write init_props.
            write('def init_props(self):', indent=1)

            uniforms: List[Tuple[str, str, str]] = []
            write('# Uniforms.', indent=2)
            for line in frag_source.splitlines():
                if line.startswith('uniform'):
                    split = line.split()
                    u_type: str = split[1]
                    if u_type in {'sampler1DArray'}:
                        # Exclude.
                        continue
                    u_name: str = split[2][:-1]
                    # value: str = split[3]
                    py_type, u_func_suffix = get_pytype_from_shtype(u_type)
                    uniforms.append((u_name, py_type, u_func_suffix))
                    write(f'self._{u_name}: {py_type}', indent=2)

            inputs: List[Tuple[str, str]] = []
            write('# Inputs.', indent=2)
            batsh_inputs_dict = '{'
            use_in_uv: bool = False
            use_in_color: bool = False
            for line in vert_source.splitlines():
                if line.startswith('in'):
                    split = line.split()
                    type: str = split[1]
                    py_type, u_func_suffix = get_pytype_from_shtype(type)
                    if py_type is None:
                        # TODO. check this.
                        continue
                    name: str = split[2][:-1]
                    if name in {'col', 'color'}:
                        use_in_color = True
                    if name in {'texco', 'texco_interp'}:
                        use_in_uv = True
                        write(f'self._{name}: {py_type} = ((0,0),(1,0),(1,1),(0,1))', indent=2)
                    else:
                        write(f'self._{name}: {py_type}', indent=2)
                    batsh_inputs_dict += f'"{name}":self.{name},'
                    inputs.append((name, py_type))
            batsh_inputs_dict += '}'

            if geom_id in {'POINT'}:
                write('self.point_scale: float = 1.0', indent=2)
            elif geom_id in {'LINE'}:
                write('self.line_scale: float = 1.0', indent=2)
            elif geom_id in {'RECT', 'SHAPE'}:
                if geom_id == 'RECT':
                    write('def get_indices(self) -> Union[Tuple[Tuple[int]]], None]: return (( 0, 1, 2 ),( 2, 1, 3 ))', indent=1)
                else:
                    write('self.indices: tuple = (( 0, 1, 2 ),( 2, 1, 3 ))', indent=2)
                    write('def set_indices(self, indices) -> Union[Tuple[Tuple[int]]], None]: self.indices = indices', indent=1)
                    write('def get_indices(self) -> Union[Tuple[Tuple[int]]], None]: return self.indices', indent=1)

            write('# Shader Flags.', indent=1)
            write('use_uv: bool = %s' % ('True' if use_in_uv else 'False'), indent=1)
            write('use_vertex_color: bool = %s' % ('True' if use_in_color else 'False'), indent=1)
            write('# Shader specific props.', indent=1)

            write('def get_inputs(self) -> Dict[str, Any]:', indent=1)
            write(batsh_inputs_dict, indent=2)

            # Write input properties.
            for (name, type) in inputs:
                write('@property', indent=1)
                write(f'def {name}(self) -> {type}:', indent=1)
                write(f'return self._{name}', indent=2)
                write(f'@{name}.setter', indent=1)
                write(f'def {name}(self, value: {type}) -> None:', indent=1)
                write(f'self._{name}: {type} = value # Cached input value.', indent=2)
                if name in {'pos', 'position', 'p'}:
                    write(f'def set_coords(self, coords: tuple or list) -> None:', indent=1)
                    write(f'self.{name}: {type} = coords # Update pos coordinates.', indent=2)
                if name in {'texco', 'texco_interp', 'uv'}:
                    write(f'def set_uv(self, uv: tuple or list) -> None:', indent=1)
                    write(f'self.{name}: {type} = uv # Update uv indices.', indent=2)

            # Write uniform properties.
            for (name, type, func_suffix) in uniforms:
                write('@property', indent=1)
                write(f'def {name}(self) -> {type}:', indent=1)
                write(f'return self._{name}', indent=2)
                write(f'@{name}.setter', indent=1)
                write(f'def {name}(self, value: {type}) -> None:', indent=1)
                write(f'self._{name}: {type} = value # Cached uniform value.', indent=2)
                write(f'self.sh.uniform_{func_suffix}("{name}", value)', indent=2)

            



else:
    # SPLIT CODE.
    #####################################################################################
    #####################################################################################
    #####################################################################################
    shader_dirs = (SHADERS_VERT_DIR, SHADERS_FRAG_DIR)

    for shader_type, shader_data, dir_path in zip(shader_types, shaders_data, shader_dirs):
        output_path = dir_path / '__init__.py'
        with output_path.open('w') as file:
            file.write('from enum import Enum\n')
            if not HARDCODE_SHADER_SOURCE:
                file.write('from os.path import dirname\n')
                file.write('from pathlib import Path\n')
                file.write('folder = Path(dirname(__file__))\n')
                file.write('def rf(fp) -> str:\n\twith fp.open("w") as f:return f.read()\n')
            file.write(f"class {shader_type.capitalize()}Shader(Enum):\n")
            for name, source in shader_data.items():
                if HARDCODE_SHADER_SOURCE:
                    file.write(f'\t{name} = {source}\n')
                else:
                    file.write(f'\t{name} = rf(folder / "{name.lower()}.{shader_type}")\n')
