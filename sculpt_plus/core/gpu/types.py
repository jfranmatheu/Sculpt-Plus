from gpu.types import (
    GPUShaderCreateInfo,
    GPUStageInterfaceInfo,
    GPUShader
)
from gpu.shader import create_from_info

from sculpt_plus.path import SculptPlusPaths


class GPU_SHADER:
    ''' Wrapper for GPUShader type. '''
    idname: str
    gpu_shader: GPUShader
    _instances = {}

    @classmethod
    def get(cls, idname: str) -> 'GPU_SHADER':
        if idname not in cls._instances:
            cls._instances[idname] = cls.from_info(idname)
        return cls._instances[idname]

    @classmethod
    def push(cls, gpu_shader: 'GPU_SHADER') -> None:
        cls._instances[gpu_shader.idname] = gpu_shader

    @classmethod
    def from_info(cls, shader_info: str or 'GPU_SHADER_CREATE_INFO') -> 'GPU_SHADER':
        return cls(
            shader_info if isinstance(shader_info, str) else shader_info.idname,
            GPU_SHADER_CREATE_INFO.create_shader(shader_info))

    def __init__(self, idname: str, gpu_shader: GPUShader):
        self.idname = idname
        self.gpu_shader = gpu_shader
        GPU_SHADER.push(self)

    @property
    def name(self) -> str:
        return self.gpu_shader.name


class GPU_SHADER_INTERFACE_INFO:
    ''' Wrapper for GPUShaderInterfaceInfo type. '''
    _instances = {}

    @classmethod
    def get(cls, idname: str) -> 'GPU_SHADER_INTERFACE_INFO':
        return cls._instances[idname]

    @classmethod
    def push(cls, interface: 'GPU_SHADER_INTERFACE_INFO') -> None:
        cls._instances[interface.idname] = interface.shader_interface

    def __init__(self, idname: str) -> None:
        self.idname = idname
        self.shader_interface = GPUStageInterfaceInfo(idname)
        GPU_SHADER_INTERFACE_INFO.push(self)

    def flat(self, type: str, name: str) -> 'GPU_SHADER_INTERFACE_INFO':
        self.shader_interface.flat(type, name)
        return self
    
    def no_perspective(self, type: str, name: str) -> 'GPU_SHADER_INTERFACE_INFO':
        self.shader_interface.no_perspective(type, name)
        return self

    def smooth(self, type: str, name: str) -> 'GPU_SHADER_INTERFACE_INFO':
        self.shader_interface.smooth(type, name)
        return self


def record_action(method):
    def inner(ref, *args, **kwargs):
        if ref.use_record:
            ref.record_def(method, *args, **kwargs)
        return method(ref, *args, **kwargs)
    return inner


class GPU_SHADER_CREATE_INFO:
    ''' Wrapper for GPUShaderCreateInfo type. '''
    _instances = {}

    @classmethod
    def create_shader(cls, idname: str or 'GPU_SHADER_CREATE_INFO') -> GPUShader:
        shader_create_info = idname if isinstance(idname, GPU_SHADER_CREATE_INFO) else cls.get(idname)
        return create_from_info(shader_create_info.shader_info)

    @classmethod
    def get(cls, idname: str) -> 'GPU_SHADER_CREATE_INFO':
        return cls._instances[idname]

    @classmethod
    def push(cls, info: 'GPU_SHADER_CREATE_INFO') -> None:
        cls._instances[info.idname] = info

    def compile(self) -> GPU_SHADER:
        ''' Create shader from this shader info object, as well as compile it. '''
        return GPU_SHADER.from_info(self)

    def record_def(self, method: callable, *args, **kwargs) -> None:
        self.record_history.append((method.__name__, args, kwargs))

    def __init__(self, idname: str, record: bool = False, based_on: str = None) -> None:
        self.idname = idname
        self.use_record = record
        if record:
            # List of Tuples with fuction idname and arguments.
            self.record_history = []
        self.shader_info = GPUShaderCreateInfo()
        if based_on is not None:
            base_shader_info = GPU_SHADER_CREATE_INFO.get(based_on)
            for (method_name, args, kwargs) in base_shader_info.record_history:
                getattr(self, method_name)(*args, **kwargs)
        GPU_SHADER_CREATE_INFO.push(self)

    @record_action
    def define(self, name: str, value: str = '') -> 'GPU_SHADER_CREATE_INFO':
        """Add a preprocessing define directive. In GLSL it would be something like:

            #define name value

            :arg name: Token name.
            :type name: str
            :arg value: Text that replaces token occurrences.
            :type value: str
        """
        self.shader_info.define(name, value)
        return self

    @record_action
    def fragment_out(self, attr_index: int, type: str, name: str, blend: str = 'NONE') -> 'GPU_SHADER_CREATE_INFO':
        """ Specify a fragment output corresponding to a framebuffer target slot. """
        self.shader_info.fragment_out(attr_index, type, name, blend=blend)
        return self

    @record_action
    def fragment_source(self, source: str) -> 'GPU_SHADER_CREATE_INFO':
        """ Fragment shader source code written in GLSL. """
        if source.endswith('.frag'):
            source = SculptPlusPaths.LIB_SHADERS_FRAG.read(source)
        elif source.endswith('.glsl'):
            source = SculptPlusPaths.LIB_SHADERS_BUILTIN.read(source)
        self.shader_info.fragment_source(source)
        return self

    @record_action
    def push_constant(self, type: str, name: str, size=0) -> 'GPU_SHADER_CREATE_INFO':
        """ Specify a global access constant. """
        self.shader_info.push_constant(type, name, size)
        return self

    @record_action
    def sampler(self, index: int, type: str, name: str) -> 'GPU_SHADER_CREATE_INFO':
        """ Specify an image texture sampler. """
        self.shader_info.sampler(index, type, name)
        return self

    @record_action
    def typedef_source(self, source: str) -> 'GPU_SHADER_CREATE_INFO':
        """ Source code included before resource declaration. Useful for defining structs used by Uniform Buffers.
            Example:

            "struct MyType {int foo; float bar;};"

            :arg source: The source code defining types.
            :type source: str """
        self.shader_info.typedef_source(source)
        return self

    @record_action
    def uniform_buf(self, index: int, type: str, name: str) -> 'GPU_SHADER_CREATE_INFO':
        """ Specify a uniform variable whose type can be one of those declared in typedef_source. """
        self.shader_info.uniform_buf(index, type, name)
        return self

    @record_action
    def vertex_in(self, index: int, type: str, name: str) -> 'GPU_SHADER_CREATE_INFO':
        """ Add a vertex shader input attribute. """
        self.shader_info.vertex_in(index, type, name)
        return self

    @record_action
    def vertex_out(self, interface: GPUStageInterfaceInfo or GPU_SHADER_INTERFACE_INFO) -> 'GPU_SHADER_CREATE_INFO':
        """ Add a vertex shader output interface block. """
        if isinstance(interface, str):
            interface = GPU_SHADER_INTERFACE_INFO.get(interface)
        self.shader_info.vertex_out(interface)
        return self

    @record_action
    def vertex_source(self, source: str) -> 'GPU_SHADER_CREATE_INFO':
        """ Vertex shader source code written in GLSL.
            Example:

            "void main {gl_Position = vec4(pos, 1.0);}" """
        if source.endswith('.vert'):
            source = SculptPlusPaths.LIB_SHADERS_VERT.read(source)
        elif source.endswith('.glsl'):
            source = SculptPlusPaths.LIB_SHADERS_BUILTIN.read(source)
        self.shader_info.vertex_source(source)
        return self


class Type:
    # Types supported natively across all GPU back-ends. */
    FLOAT = 'FLOAT'
    INT = 'INT'
    UINT = 'UINT'
    VEC2 = 'VEC2'
    VEC3 = 'VEC3'
    VEC4 = 'VEC4'
    MAT3 = 'MAT3'
    MAT4 = 'MAT4'
    UVEC2 = 'UVEC2'
    UVEC3 = 'UVEC3'
    UVEC4 = 'UVEC4'
    IVEC2 = 'IVEC2'
    IVEC3 = 'IVEC3'
    IVEC4 = 'IVEC4'
    BOOL = 'BOOL'
    ''' Additionally supported types to enable data optimization and native
    * support in some GPU back-ends.
    * NOTE: These types must be representable in all APIs. E.g. `VEC3_101010I2` is aliased as vec3
    * in the GL back-end, as implicit type conversions from packed normal attribute data to vec3 is
    * supported. UCHAR/CHAR types are natively supported in Metal and can be used to avoid
    * additional data conversions for `GPU_COMP_U8` vertex attributes. '''
    VEC3_101010I2 = 'VEC3_101010I2'
    UCHAR = 'UCHAR'
    UCHAR2 = 'UCHAR2'
    UCHAR3 = 'UCHAR3'
    UCHAR4 = 'UCHAR4'
    CHAR = 'CHAR'
    CHAR2 = 'CHAR2'
    CHAR3 = 'CHAR3'
    CHAR4 = 'CHAR4'
