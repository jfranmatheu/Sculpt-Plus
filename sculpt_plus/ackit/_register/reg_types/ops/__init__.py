from .operator import Operator, OpsReturn
from .invoke import InvokeSearchMenu, InvokePropsDialog


class OperatorTypes:
    ACTION = Operator
    DRAW_MODAL = None # TODO: support draw modal operators.
    SEARCH_MENU = InvokeSearchMenu
    INVOKE_PROPS_DIALOG = InvokePropsDialog
