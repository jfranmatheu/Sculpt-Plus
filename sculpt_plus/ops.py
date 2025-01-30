# /ops.py
# Code automatically generated!
from enum import Enum, auto

from .ackit._auto_code_gen.ops import OpTypeEnum

__all__ = ["OPS",]




class OPS(OpTypeEnum, Enum):
	GestureSizeStrength = auto()
	MultiresChangeLevel = auto()
	MultiresApply = auto()
	ImportTexture = auto()
	UnasignTexture = auto()
	SelectTool_FaceSetEdit = auto()
	ExpandToolbar = auto()
	IncreaseRemeshVoxelSize = auto()
	IncreaseRemeshVoxelDensity = auto()
	SetupWorkspace = auto()


def gesture_size_strength(exec_context: str = 'INVOKE_DEFAULT', undo: bool = True) -> None: OPS.GestureSizeStrength(exec_context, undo)
def multires_change_level(exec_context: str = 'INVOKE_DEFAULT', undo: bool = True) -> None: OPS.MultiresChangeLevel(exec_context, undo)
def multires_apply(exec_context: str = 'INVOKE_DEFAULT', undo: bool = True) -> None: OPS.MultiresApply(exec_context, undo)
def import_texture(exec_context: str = 'INVOKE_DEFAULT', undo: bool = True) -> None: OPS.ImportTexture(exec_context, undo)
def unasign_texture(exec_context: str = 'INVOKE_DEFAULT', undo: bool = True) -> None: OPS.UnasignTexture(exec_context, undo)
def select_tool_face_set_edit(exec_context: str = 'INVOKE_DEFAULT', undo: bool = True) -> None: OPS.SelectTool_FaceSetEdit(exec_context, undo)
def expand_toolbar(exec_context: str = 'INVOKE_DEFAULT', undo: bool = True) -> None: OPS.ExpandToolbar(exec_context, undo)
def increase_remesh_voxel_size(exec_context: str = 'INVOKE_DEFAULT', undo: bool = True) -> None: OPS.IncreaseRemeshVoxelSize(exec_context, undo)
def increase_remesh_voxel_density(exec_context: str = 'INVOKE_DEFAULT', undo: bool = True) -> None: OPS.IncreaseRemeshVoxelDensity(exec_context, undo)
def setup_workspace(exec_context: str = 'INVOKE_DEFAULT', undo: bool = True) -> None: OPS.SetupWorkspace(exec_context, undo)


''' Usage example:

from addon_module import ops as addon_module_ops
addon_module_ops.OPS.GestureSizeStrength()

OR...

from addon_module.ops import Ops
OPS.GestureSizeStrength()  # directly run execute the operator.
OPS.GestureSizeStrength.operator.run_invoke()  # access to the operator class and run invoke the operator.
'''