from enum import Enum

from sculpt_plus.core.gpu.types import GPU_SHADER_CREATE_INFO
from .gpu_shader_2D_widget_info import *


class ShaderInfo(Enum):
    WIDGET_BASE = 0
    WIDGET_BASE_INST = 1
    WIDGET_SHADOW = 2

    def __call__(self):
        return GPU_SHADER_CREATE_INFO.get(self.name)
