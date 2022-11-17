# Dibu functions in cammel-case. Rest in snake-case.
from mathutils import Vector

from bac_core.utils.math import eval_bezcurve

__all__ = [
    'Rct_Geo',
    'RctBotLeft_Geo',
    'RctCent_Geo',
    'RctTopLeft_Geo',
    
    'RctBotLeft_Rnd_Geo',
    'Rct_Rnd_Geo',
]

def rect_coords_vbo(x, y, w, h):return (x,y,x+w,y,x,y+h,x+w,y+h)
rect_indices_vbo =( (0, 1, 2),
                    (2, 1, 3) )

#---

#3 #2
#0 #1
def Rct_Idx(): return (( 0, 1, 2 ),( 2, 1, 3 ))
#0 #2
#1 #3
def RctTopLeft_Idx(): return (( 0, 1, 2 ),( 2, 3, 0 ))

def Rct_Rnd_Idx(): return ((0,1,2),(0,2,3),(0,3,4),(0,4,5),(0,5,6),(0,6,7),(0,7,8),(0,8,9),(0,9,10),(0,10,11),(0,11,12),(0,12,1))

#---

def RctBotLeft_Coo(x, y, w, h):return [(x,y),(x+w,y),(x,y+h),(x+w,y+h)]
def RctBotLeft_Geo(_o, _tam): return {"pos": RctBotLeft_Coo(*_o, *_tam)}, Rct_Idx()

def RctCent_Coo(x, y, w, h):return [(x-w,y-h),(x+w,y-h),(x-w,y+h),(x+w,y+h)]
def RctCent_Geo(_o, _tam): return {"pos": RctCent_Coo(*_o, *_tam)}, Rct_Idx()

def RctTopLeft_Coo(x, y, w, h):return [(x,y),(x,y-h),(x+w,y-h),(x+w,y)]
def RctTopLeft_Geo(_o, _tam): return {"pos": RctTopLeft_Coo(*_o, *_tam)}, RctTopLeft_Idx()

def Rct_Coo(x, y, w, h, u, v): return RctBotLeft_Coo(x-w*min(max(u, 0), 1), y-h*min(max(v, 0), 1), w, h)
def Rct_Geo(_o, _tam, _piv): return {"pos": Rct_Coo(*_o, *_tam, *_piv)}, Rct_Idx()
