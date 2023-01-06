# from sculpt_plus.core.gpu.types import GPU_SHADER_CREATE_INFO, GPUShader
from sculpt_plus.core.gpu.types import GPU_SHADER as GPUShader
from sculpt_plus.utils.enum import CallEnumName
from enum import auto, unique


@unique
class Shaders(CallEnumName):
    @staticmethod
    def action(key: str) -> GPUShader:
        return GPUShader.get(key)

    WIDGET_BASE=auto()
    WIDGET_SHADOW=auto()
