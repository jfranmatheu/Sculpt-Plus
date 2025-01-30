# /ops.py
# Code automatically generated!
from enum import Enum, auto

from .ackit._auto_code_gen.ops import OpTypeEnum

__all__ = ["OPS",]




class OPS(OpTypeEnum, Enum):
	IncreaseRemeshVoxelSize = auto()
	IncreaseRemeshVoxelDensity = auto()
	SetupWorkspace = auto()


def increase_remesh_voxel_size(exec_context: str = 'INVOKE_DEFAULT', undo: bool = True) -> None: OPS.IncreaseRemeshVoxelSize(exec_context, undo)
def increase_remesh_voxel_density(exec_context: str = 'INVOKE_DEFAULT', undo: bool = True) -> None: OPS.IncreaseRemeshVoxelDensity(exec_context, undo)
def setup_workspace(exec_context: str = 'INVOKE_DEFAULT', undo: bool = True) -> None: OPS.SetupWorkspace(exec_context, undo)


''' Usage example:

from addon_module import ops as addon_module_ops
addon_module_ops.OPS.IncreaseRemeshVoxelSize()

OR...

from addon_module.ops import Ops
OPS.IncreaseRemeshVoxelSize()  # directly run execute the operator.
OPS.IncreaseRemeshVoxelSize.operator.run_invoke()  # access to the operator class and run invoke the operator.
'''