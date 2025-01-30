from gpu.types import GPUShader, GPUBatch
from gpu_extras.batch import batch_for_shader as batsh
from typing import Dict, Tuple, Any, Union
from mathutils import Vector


class ShaderType:
    VERTEX = 0
    FRAGMENT = 1
    GEOMETRY = 2

class PrimitiveType:
    POINT = 'POINTS'
    LINE = ('LINES', 'LINE_STRIP', 'LINE_LOOP')
    TRIANGLE = 'TRI'
    RECT = 'TRI'
    SHAPE = (TRIANGLE, RECT)
    IMG = 'TRI_FAN' # NOTE: Deprecated. Use 'TRI' instead.

class Shader:
    sh: GPUShader
    # sh_type: ShaderType
    geo_type: PrimitiveType

    def __init__(self):
        self.batsh: GPUBatch = None
        self.init_props()

    def set_rect(self, pos: Vector, size: Vector) -> None:
        self.set_coords(
            
        )

    def set_custom_shape(self, pos: Vector, size: Vector, custom_shape: Tuple[Vector]) -> None:
        self.set_coords(
            
        )
        self.set_indices(

        )

    def set_point(self, pos: Vector, scale: float) -> None:
        self.point_scale: float = scale

    def init_props(self):
        ''' Init shader props. '''
        pass

    def get_inputs(self) -> Dict[str, Any]:
        ''' Get shader inputs. '''
        return {}

    def get_indices(self) -> Union[Tuple[Tuple[int]], None]:
        ''' Get shader indices. '''
        if self.geo_type in {'RECT'}:
            return 
        return None
