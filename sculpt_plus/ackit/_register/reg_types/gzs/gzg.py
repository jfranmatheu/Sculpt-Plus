from .._base import BaseType

from bpy.types import GizmoGroup as BlGizmoGroup


class GizmoGroup(BaseType):
    @classmethod
    def tag_register(deco_cls, **kwargs: dict) -> "GizmoGroup":
        return super().tag_register(
            BlGizmoGroup,
            "GGT",
            **kwargs,
        )
