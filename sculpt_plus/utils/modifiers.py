from typing import Union

from bpy.types import Modifier


def get_modifier_by_type(object, modifier_type: str) -> Union[Modifier, None]:
    for modifier in object.modifiers:
        if modifier.type == modifier_type:
            return modifier
    return None
