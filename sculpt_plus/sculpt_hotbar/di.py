import bpy
from blf import(enable as text_enable, disable as text_disable,SHADOW, shadow as text_shadow, shadow_offset as text_shadow_offset,color as text_color, position as text_position, size as text_size,dimensions as text_dim, draw as text_draw, ROTATION, rotation as text_rotation,clipping as text_clipping, CLIPPING, WORD_WRAP)
from mathutils import Vector
p='pos';co='color';T='TRIS';TF='TRI_FAN';texidx='texCoord';i='image';A='ALPHA';LL='LINE_LOOP';L='LINES'
from gpu.shader import from_builtin as get_builtin_shader
sh_unif = get_builtin_shader('2D_UNIFORM_COLOR')
sh_img = get_builtin_shader('2D_IMAGE')
from gpu.texture import from_image as get_tex
from gpu_extras.batch import batch_for_shader as bat
from gpu.types import Buffer, GPUTexture as TEX, GPUShader as SH, GPUShaderCreateInfo as CreateShader
from bgl import *
from bpy.types import UILayout
from sculpt_plus.lib import BrushIcon
from gpu import *
sh_img_a=CreateShader();sh_img_a=SH("""
uniform mat4 ModelViewProjectionMatrix;in vec2 texCoord;in vec2 pos;out vec2 texCoord_interp;void main(){gl_Position=ModelViewProjectionMatrix * vec4(pos.xy, 0.0f, 1.0f); gl_Position.z=1.0; texCoord_interp=texCoord;}
""","""
in vec2 texCoord_interp;out vec4 fragColor;uniform vec4 color;uniform sampler2D image;void main(){fragColor=texture(image, texCoord_interp);fragColor.a*=color.a;if(fragColor.a>.1f){fragColor.rgb=color.rgb;}}
""")
font_info = {
    'id': 0
}
def set_font(id):
    font_info['id'] = id
def DiIma(_p,_s,_i,s=sh_img):
    t=get_tex(_i) if not isinstance(_i,TEX) else _i
    b=bat(s, TF,{p:(
    _p,(_p.x+_s.x,_p.y),
    _p+_s,(_p.x,_p.y+_s.y)),
    texidx:((0,0),(1,0),(1,1),(0,1)),},)
    s.bind()
    #s.uniform_float(co,(.9,.9,.9,1))
    s.uniform_sampler(i,t)
    state.blend_set(A);b.draw(s);state.blend_set('NONE')
def DiImagl(_p,_s,_i,s=sh_img):
    b=bat(s, TF,{p:(
    _p,(_p.x+_s.x,_p.y),
    _p+_s,(_p.x,_p.y+_s.y)),
    texidx:((0,0),(1,0),(1,1),(0,1)),},)
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D,_i)
    s.bind()
    s.uniform_int(i, 0)
    b.draw(s)
def DiImaco(_p,_s,_i,_co,s=sh_img_a):
    t=get_tex(_i) if not isinstance(_i,TEX) else _i
    b=bat(s, TF,{p:(
    _p,(_p.x+_s.x,_p.y),
    _p+_s,(_p.x,_p.y+_s.y)),
    texidx:((0,0),(1,0),(1,1),(0,1)),},)
    s.bind()
    s.uniform_float(co,_co)
    s.uniform_sampler(i,t)
    state.blend_set(A);b.draw(s);state.blend_set('NONE')
def DiBr(_p,_s,_b):
    ico=BrushIcon.from_brush(_b)
    if ico:DiIma(_p,_s,ico);DiIma(_p,_s,ico)
def DiLine(_a,_b,_lt,_co,s=sh_unif):
    state.blend_set(A)
    b=bat(s,L,{p:(_a,_b)})
    state.line_width_set(_lt)
    s.bind()
    s.uniform_float(co,_co)
    b.draw(s)
    state.line_width_set(1.0)
    state.blend_set('NONE')
def DiCage(_p,_s,_lt,_co,s=sh_unif):
    state.blend_set(A)
    b=bat(s,LL,{p:(
    _p,(_p.x+_s.x,_p.y),
    _p+_s, (_p.x,_p.y+_s.y),)})
    state.line_width_set(_lt)
    s.bind()
    s.uniform_float(co,_co)
    b.draw(s)
    state.line_width_set(1.0)
    state.blend_set('NONE')
def DiRct(_p,_s,_co,s=sh_unif):
    state.blend_set(A)
    b=bat(s,T,{p:(
    _p,(_p.x+_s.x,_p.y),
    (_p.x,_p.y+_s.y),_p+_s)},
    indices=((0,1,2),(2,1,3)))
    s.bind()
    s.uniform_float(co,_co)
    b.draw(s)
    state.blend_set('NONE')
def DiArrowSolid(_o,_s,_co,_invert=False,s=sh_unif):
    hh=Vector((0,_s.x/2))
    hw=Vector((_s.x/2,0))
    '''
    if _invert:
        _o -= hw*2
        DiRct(_o-hh,_s*.5,_co)
    else:
        DiRct(_o-hh,_s*.5,_co)
    '''
    if _invert:b=bat(s,T,{p:(_o+hh*2,_o-hh*2,_o-hw*2)},indices=((0,1,2),))
    else:b=bat(s,T,{p:(_o+hh*2,_o-hh*2,_o+hw*2)},indices=((0,1,2),))
    s.bind()
    s.uniform_float(co,_co)
    state.blend_set(A)
    glEnable(GL_BLEND)
    b.draw(s)
    state.blend_set('NONE')
    glDisable(GL_BLEND)
def DiText(_p, _text, _size, _scale,  _co=(.92, .92, .92, 1.0), pivot=None, shadow_props: dict = None, draw_rect_props: dict = None, id:int=None, rotation:float=None):
    id=font_info['id'] if id is None else id
    text_color(id, *_co)
    text_size(id, max(7.5, _size), int(72*_scale))
    if rotation is not None:
        text_enable(id, ROTATION)
        text_rotation(id, rotation)
    if shadow_props:
        offset = shadow_props.get('offset', (1, -1))
        color = shadow_props.get('color', (.1, .1, .1, .8))
        blur = shadow_props.get('blur', 3)
        text_enable(id, SHADOW)
        text_shadow(id, blur, *color)
        text_shadow_offset(id, *offset)
    if not pivot:
        dim = None

    else:
        dim = text_dim(id, _text)
        _p = (_p.x - dim[0] * pivot[0], # X
              _p.y - dim[1] * pivot[1]) # Y
    text_position(id, *_p, 0)
    if draw_rect_props:
        dim = dim if dim else text_dim(id, _text)
        color = draw_rect_props.get('color', (.1, .1, .1, .8))
        margin: float = draw_rect_props.get('margin', 3) * _scale
        _p = Vector(_p) - Vector((margin, margin))
        s = Vector((dim)) + Vector((margin, margin)) * 2.0
        DiRct(_p, s, color)
        DiCage(_p, s, 2.2, Vector(color)*.9)
    text_draw(id, _text)
    if shadow_props:
        text_disable(id, SHADOW)
    if rotation is not None:
        text_disable(id, ROTATION)
def get_rect_from_text(_p, _text, _size, _scale, _pivot=(0, 0), _margin:float = 0):
    id=font_info['id']
    text_size(id, _size, int(72*_scale))
    dim = text_dim(id, _text)
    p = (_p.x - dim[0] * _pivot[0], # X
            _p.y - dim[1] * _pivot[1]) # Y
    margin = Vector((_margin, _margin)) * _scale
    p = Vector(p) - margin
    s = Vector(dim) + margin * 2.0
    return p, s
def get_text_dim(_text, _size, _scale):
    id=font_info['id']
    text_size(id, _size, int(72*_scale))
    return text_dim(id, _text)
