from bpy.types import Brush
from bpy.props import StringProperty, BoolProperty

def register():
    Brush.cat_id = StringProperty(default='')
    Brush.fav = BoolProperty(default=False)

def unregister():
    del Brush.cat_id
    del Brush.fav
