from math import pi, sin, asin, cos, radians, atan2, hypot, acos, sqrt
from mathutils import Vector


class Rect():
    def __init__(self, corner, opposite_corner, _type: str='BOTTOM_LEFT'):
        if _type == 'TOP_LEFT':
            self.xi = corner[0]
            self.xf = opposite_corner[0]
            self.yf = corner[1]
            self.yi = opposite_corner[1]
        else:
            self.xi, self.yi = corner
            self.xf, self.yf = opposite_corner

def vector(*args) -> Vector:
    return Vector(args)

def vector2(x, y) -> Vector:
    return Vector((x, y))

def vector3(x, y, z) -> Vector:
    return Vector((x, y, z))

def map_value(val, src, dst):
    """
    Scale the given value from the scale of src to the scale of dst.
    """
    return ((val - src[0]) / (src[1]-src[0])) * (dst[1]-dst[0]) + dst[0]

def mix(x, y, a):
    return x*(1-a)+y*a

def dotproduct(v1, v2):
    return sum((a*b) for a, b in zip(v1, v2))

def length(v):
    return sqrt(dotproduct(v, v))

def angle_between(v1, v2):
    return acos(dotproduct(v1, v2) / (length(v1) * length(v2)))

def distance_between(_p1, _p2):
    return hypot(_p1[0] - _p2[0], _p1[1] - _p2[1])
    #return math.sqrt((_p1[1] - _p1[0])**2 + (_p2[1] - _p2[0])**2)

def direction_from_to(_p1, _p2, _norm=True):
    if _norm:
        return (_p1 - _p2).normalized()
    else:
        return _p1 - _p2

def rotate_point_around_point(o, p, angle):
    qx = o.x + cos(angle) * (p.x - o.x) - sin(angle) * (p.y - o.y)
    qy = o.y + sin(angle) * (p.x - o.x) + cos(angle) * (p.y - o.y)
    return Vector((qx, qy))

def point_inside_circle(_p, _c, _r):
    return distance_between(_p, _c) < _r

def point_inside_rect(_p, _pos, _size):
    return ((_pos[0] + _size[0]) > _p[0] > _pos[0]) and ((_pos[1] + _size[1]) > _p[1] > _pos[1])

def point_inside_bounds(_p, _a, _b):
    return (_b.x > _p.x > _a.x) and (_b.y > _p.y > _a.y)

def point_inside_ring(_p, _c, _r1, _r2):
    d = distance_between(_p, _c)
    return d > _r1 and d < _r2

def clamp(value, _min, _max):
    return min(max(value, _min), _max)

def eval_bezcurve(p0, p1, p2, t = .5): return (1-t)**2 * p0 + 2*t * (1-t) * p1 + t**2 * p2

def smoothstep(edge0, edge1, x):
    # Scale, bias and saturate x to 0..1 range
    x = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    # Evaluate polynomial
    return x * x * (3 - 2 * x)

def linear_interpol(x1: float, x2: float, y1: float, y2: float, x: float) -> float:
    """Perform linear interpolation for x between (x1,y1) and (x2,y2) """
    return ((y2 - y1) * x + x2 * y1 - x1 * y2) / (x2 - x1)

def lerp_point(t, times, points):
    dx = points[1][0] - points[0][0]
    dy = points[1][1] - points[0][1]
    dt = (t-times[0]) / (times[1]-times[0])
    return dt*dx + points[0][0], dt*dy + points[0][1]

# Precise method, which guarantees v = v1 when t = 1.
def lerp(v0: float, v1: float, t: float) -> float:
    return (1 - t) * v0 + t * v1

def lerp_smooth(v0: float, v1: float, t: float) -> float:
    return t*t*t*(t*(6.0*t-15.0)+10.0)

def ease_quad_in_out(v0: float, v1: float, t: float):
    a = -(t * (t - 2)) # quad ease in out
    return v1 * a + v0 * (1 - a) # ease generic

def ParametricBlend(t):
    sqt = t * t
    return sqt / (2.0 * (sqt - t) + 1.0)

def lerp_in(v0: float, v1: float, t: float) -> float:
    return sin(t*pi*0.5)

def lerp_out(v0: float, v1: float, t: float) -> float:
    return t*t

def ease_quadratic_out(t, start, change, duration):
    t /= duration
    return -change * t*(t-2) + start

def ease_sine_in(t, b, c, d=1.0):
    return -c * cos(t/d * (pi/2)) + c + b

# tuple as ((1, 2), (2, 4)) to represent rectangles.
# rectangle is defined by two points in the upper left ((x1|y1)) and lower right corner ((x2|y2))
def rect_contains_rect(r2, r1):
    return r1.x1 < r2.x1 < r2.x2 < r1.x2 and r1.y1 < r2.y1 < r2.y2 < r1.y2

def node_inside_bounds(node, Xi, Xf, Yi, Yf):
    n0, n1 = node.get_opposite_corners()
    return n0.x > Xi and n1.x < Xf and n0.y > Yi and n1.y < Yf

'''
    Note that a rectangle can be represented by two coordinates, top left and bottom right. So mainly we are given following four coordinates.
    l1: Top Left coordinate of first rectangle.
    r1: Bottom Right coordinate of first rectangle.
    l2: Top Left coordinate of second rectangle.
    r2: Bottom Right coordinate of second rectangle.
'''
def node_overlaps_rect(node, l2, r2):
    l1, r1 = node.get_opposite_corners()
    # If one rectangle is on left side of other 
    if(l1.x >= r2.x or l2.x >= r1.x): 
        return False

    # If one rectangle is above other 
    if(l1.y <= r2.y or l2.y <= r1.y): 
        return False

    return True

# Reference for both is Left-Bottom.
def rect_overlaps_rect(R1, R2):
    if (R1[0]>=R2[2]) or (R1[2]<=R2[0]) or (R1[3]<=R2[1]) or (R1[1]>=R2[3]):
        return False
    return True

def point_inside_node(_p, _pos, _size):
    return _pos[0] < _p[0] < (_pos[0] + _size[0]) and (_pos[1] - _size[1]) < _p[1] < _pos[1]
