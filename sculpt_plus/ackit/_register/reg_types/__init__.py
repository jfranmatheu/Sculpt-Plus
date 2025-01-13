from ._base import BaseType

from .ops import OperatorTypes, OpsReturn
from .preferences import AddonPreferences
from .ui import InterfaceTypes, PanelFlags
from .property_group import PropertyGroup
from .gzs import GizmoTypes


class RegType:
    PREFS = AddonPreferences
    UI = InterfaceTypes
    OPS = OperatorTypes
    PROP_GROUP = PropertyGroup
    GZS = GizmoTypes
