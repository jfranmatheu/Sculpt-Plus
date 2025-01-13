# INTERNAL SUBMODULE
# MODIFY IT ONLY IF YOU KNOW WHAT YOU ARE DOING
from ._register import BlenderTypes
from .reg_helpers import RegHelper
from .reg_decorators import RegDeco
from .reg_types import RegType, PanelFlags
from .property_types import PropertyTypes as Property


class ACK:
    Deco = RegDeco
    Helper = RegHelper
    Type = RegType
    Prop = Property

    class Flag:
        Panel = PanelFlags # Decorator.
        # Modal = ModalFlags # Decorator.


def clear_register_cache():
    from ._register import clear_cache
    clear_cache()
    # from .reg_types._base import BaseType
    # BaseType.clear_cache()
