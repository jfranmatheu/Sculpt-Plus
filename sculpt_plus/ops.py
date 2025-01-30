# /ops.py
# Code automatically generated!
from enum import Enum, auto

from .ackit._auto_code_gen.ops import OpTypeEnum

__all__ = ["OPS",]




class OPS(OpTypeEnum, Enum):
	IncreaseRemeshVoxelSize = auto()
	IncreaseRemeshVoxelDensity = auto()
	SetupWorkspace = auto()


