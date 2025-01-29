from enum import Enum

import bpy


class Notify(Enum):
    INFO = 'INFO'
    ERROR = 'CANCEL'
    WARNING = 'ERROR'

    def __call__(self, title: str, message: str):
        def draw(self, context):
            col = self.layout.column(align=True)
            for line in message.split('\n'):
                col.label(text=line)

        bpy.context.window_manager.popup_menu(draw, title=title, icon=self.value)
