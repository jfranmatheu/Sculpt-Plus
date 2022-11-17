__all__ = [
    'BuiltIn_Img_Geo',
    'Img_Geo'
]


def BuiltIn_Img_Idx():return ((0, 0), (1, 0), (1, 1), (0, 1))
def BuiltIn_Img_Coo(x,y,w,h):return ((x,y),(x+w,y),(x+w,y+h),(x,y+h))
def BuiltIn_Img_Geo(*args):return {"pos" : BuiltIn_Img_Coo(*args[0], *args[1]), "texCoord" : BuiltIn_Img_Idx()}

def Img_Idx(): return ((0, 1), (0, 0), (1, 0), (1, 1))
def Img_Coo(x,y,w,h): return [[x,y+h],[x,y],[x+w,y],[x+w,y+h]]
def Img_Geo(*args):return {"pos" : Img_Coo(*args[0], *args[1]), "texco" : Img_Idx()}
