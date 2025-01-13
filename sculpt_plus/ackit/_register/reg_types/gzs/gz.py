from .._base import BaseType

from bpy.types import Gizmo as BlGizmo


class Gizmo(BaseType):
    @classmethod
    def tag_register(deco_cls, **kwargs: dict) -> "Gizmo":
        return super().tag_register(
            BlGizmo,
            "GT",
            **kwargs,
        )
