from re import findall
from typing import Sequence
import uuid
import builtins

from gpu.types import GPUShader as BlShader, GPUBatch as BlBatch
from gpu_extras.batch import batch_for_shader as bat

from .frag import Frag
from .vert import Vert
from .geom import ShaderGeom
from .types import ShaderType


pool = {}

def get_enum_value(type, input):
    if isinstance(input, type): return input()
    enum_item = type.get(input)
    if enum_item: return enum_item()

def get_enum(type, input: str):
    if isinstance(input, type): return input
    return type.get(input, None)

def get_type(type_str: str):
    if 'vec' in type_str:
        # Otherwise, some tuple or list (or vector-like c:).
        return True, float
    else:
        return False, getattr(builtins, type, None)
    
def get_default_value(type):
    if type == bool:
        return False
    elif type == int:
        return 0
    elif type == float:
        return 0.0
    elif type in (set, list, tuple):
        return []
    return None


class ShaderAttribute:
    def __init__(self, shader: 'Shader', source: str, type: str, name: str) -> None:
        self.shader = shader
        self.source = source
        self.is_vector, self.type = get_type(type)
        self.name = name
        self.default = get_default_value(self.type)
        self.value = self.default
        
    def update(self, value):
        if not isinstance(value, self.type):
            return
        self.value = value
        


class Shader:
    def __init__(self, type: ShaderType or str, vert: Vert or str, frag: Frag or str, geom: ShaderGeom or str, id: str = '') -> 'Shader':
        self.id = id if id else uuid.uuid4().hex
        
        if self.id in pool:
            pool[self.id].append(self)
        else:
            pool[self.id] = [self]

        self.type = get_enum(ShaderType, type)
        self.vert = get_enum(Vert,  vert)
        self.frag = get_enum(Frag,  frag)
        self.geom = get_enum(ShaderGeom, geom)

        self._shader = BlShader(self.vert(), self.frag())
        self._batch  = None

        self.indices    = None
        self.inputs     = {} # type : [keys...], ...
        self.uniforms   = {} # type : [keys...], ...
        self.keys       = {} # key : value, ...

        def init_props(re) -> dict:
            types = {float, int, bool}
            props = {t: set() for t in types}

            for match in re:
                split = match.split(' ')
                type  = split[1]
                id    = split[2]

                if 'vec' in type:
                    # Otherwise, some tuple or list (or vector-like c:).
                    type = float
                else:
                    type = getattr(builtins, type, None)
                    if not type:
                        continue

                props[type].add(id)
                self.keys[id] = get_default_value(type)

            return props

        self.inputs     = init_props( findall(r"in\s\w+\s\w+",      self.vert) )
        self.uniforms   = init_props( findall(r"uniform\s\w+\s\w+", self.frag) )

    @property
    def shader(self) -> BlShader:
        return self._shader

    @property
    def batch(self) -> BlBatch | None:
        return self._batch

    def instance(self) -> 'Shader':
        return Shader(self.type, self.vert, self.frag, self.geom, self.id)

    def bind(self) -> 'Shader':
        self._shader.bind()
        return self

    def set_bool(self, a, b) -> 'Shader':
        self._shader.uniform_bool(a, b)
        return self

    def set_int(self, a, b) -> 'Shader':
        self._shader.uniform_int(a, b)
        return self

    def set_float(self, a, b) -> 'Shader':
        self._shader.uniform_float(a, b)
        return self

    def set_floats(self, **kwargs) -> 'Shader':
        for a, b in kwargs.items():
            self.set_float(a, b)
        return self

    def set_vector(self, location: int, buffer: Sequence, length: int, count: int) -> 'Shader':
        self._shader.uniform_vector_float(location, buffer, length, count)
        return self

    def dimm(self, inputs: dict, uniforms: dict) -> 'Shader':
        bat(self.type, self.shader, inputs+uniforms)
        
    def update_inputs(self, inputs: dict = {}):
        pass
    
    def update_uniforms(self, uniforms: dict = {}):
        pass
