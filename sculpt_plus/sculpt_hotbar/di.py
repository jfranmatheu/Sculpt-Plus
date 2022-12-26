import bpy
from blf import(enable as text_enable, disable as text_disable,SHADOW, shadow as text_shadow, shadow_offset as text_shadow_offset,color as text_color, position as text_position, size as text_size,dimensions as text_dim, draw as text_draw, ROTATION, rotation as text_rotation,clipping as text_clipping, CLIPPING, WORD_WRAP)
from mathutils import Vector
p='pos';op='op';co='color';hl='hl';T='TRIS';TF='TRI_FAN';texidx='texCoord';i='image';A='ALPHA';LL='LINE_LOOP';L='LINES';P='POINTS'
from gpu.shader import from_builtin as get_builtin_shader
sh_unif = get_builtin_shader('2D_UNIFORM_COLOR')
sh_img = get_builtin_shader('2D_IMAGE')
from gpu.texture import from_image as get_tex
from gpu_extras.batch import batch_for_shader as bat
from gpu_extras.presets import draw_circle_2d
from gpu.types import Buffer, GPUTexture as TEX, GPUShader as SH, GPUShaderCreateInfo as CreateShader
from bgl import *
from bpy.types import UILayout
from sculpt_plus.lib import BrushIcon
from sculpt_plus.utils.gpu import get_brush_tex, get_ui_image_tex
from gpu import *
sh_img_co=CreateShader();sh_img_co=SH("""
uniform mat4 ModelViewProjectionMatrix;in vec2 texCoord;in vec2 pos;out vec2 texCoord_interp;void main(){gl_Position=ModelViewProjectionMatrix * vec4(pos.xy, 0.0f, 1.0f); gl_Position.z=1.0; texCoord_interp=texCoord;}
""","""
in vec2 texCoord_interp;out vec4 fragColor;uniform vec4 color;uniform sampler2D image;void main(){fragColor=texture(image, texCoord_interp);if(fragColor.a<.01f){discard;}fragColor.a*=color.a;fragColor.rgb=color.rgb;}
""")
sh_img_a_op_gam_hl=CreateShader();sh_img_a_op_gam_hl=SH("""
uniform mat4 ModelViewProjectionMatrix;in vec2 texCoord;in vec2 pos;out vec2 texCoord_interp;void main(){gl_Position=ModelViewProjectionMatrix * vec4(pos.xy, 0.0f, 1.0f); gl_Position.z=1.0; texCoord_interp=texCoord;}
""","""
in vec2 texCoord_interp;out vec4 fragColor;uniform float op;uniform float hl;uniform sampler2D image;void main(){fragColor=texture(image, texCoord_interp);if(fragColor.a<.01f){discard;}fragColor.a*=op;fragColor.rgb=pow(fragColor.rgb, vec3(2.2-hl));}
""")
sh_estrellita=CreateShader();sh_estrellita=SH("""
uniform mat4 ModelViewProjectionMatrix;uniform float size;in vec2 pos;void main(){gl_Position = ModelViewProjectionMatrix * vec4(pos, 1.0, 1.0);gl_PointSize = size;}
""","""
out vec4 fragColor;

// signed distance to a n-star polygon with external angle en
float sdStar(in vec2 p, in float r, in int n, in float m) // m=[2,n]
{
  // these 4 lines can be precomputed for a given shape
  float an = 3.141593/float(n);
  float en = 3.141593/m;
  vec2  acs = vec2(cos(an),sin(an));
  vec2  ecs = vec2(cos(en),sin(en)); // ecs=vec2(0,1) and simplify, for regular polygon,

  // reduce to first sector
  float bn = mod(atan(p.x,p.y),2.0*an) - an;
  p = length(p)*vec2(cos(bn),abs(sin(bn)));

  // line sdf
  p -= r*acs;
  p += ecs*clamp( -dot(p,ecs), 0.0, r*acs.y/ecs.y);
  return length(p)*sign(p.x);
}

void main()
{
  //fragColor = vec4(1.0,1.0,1.0,1.0);
  //return;
  vec2 cxy = 2.0 * gl_PointCoord.xy - 1.0;

  float n = 4.0;  // n, number of sides
  float w = 2.5;  // angle divisor, between 2 and n

  // sdf
  float d = sdStar( cxy, .9, int(n), w );
  
  // colorize
  vec3 col = (d>0.0) ? vec3(0.0,0.0,0.0) : vec3(.9,0.85,0.45);
  float opa = (d>0.0) ? 0.0 : 1.0;
  col = mix( col, vec3(1.0), 1.0-smoothstep(0.0,0.015,abs(d)) );
  opa = mix( opa, 0.0, 1.0-smoothstep(0.0,0.2,abs(d)) );

  fragColor = vec4(pow(col, vec3(2.2)),opa);
}
""")
sh_silueta=CreateShader();sh_silueta=SH("""
uniform mat4 ModelViewProjectionMatrix;in vec2 texCoord;in vec2 pos;out vec2 texCoord_interp;void main(){gl_Position=ModelViewProjectionMatrix * vec4(pos.xy, 0.0f, 1.0f); gl_Position.z=1.0; texCoord_interp=texCoord;}
""","""
in vec2 texCoord_interp;
out vec4 fragColor;

uniform sampler2D i;
uniform float alpha;
uniform vec3 co;
uniform vec3 bco;
uniform float use_transp;

void main()
{
    fragColor = texture(i, texCoord_interp);

    if (use_transp == 1.0) {
        if (fragColor.a < .1) {
            discard;
        }
    }

    //float f = (fragColor.r + fragColor.g + fragColor.b) / 3.0;
    if (fragColor.a > 0.6) {
        fragColor.rgb = co;
    }
    else if (fragColor.a < 0.4) {
        fragColor.rgb = bco;
    }
    else {
        
        fragColor.rgb = mix(bco, co, fragColor.a);
    } 
    
    fragColor.a = alpha;
}
""")
font_info = {
    'id': 0
}
def set_font(id):
    font_info['id'] = id
def DiCircle(_p,_lt,_r,_seg,_co):
    state.blend_set(A)
    state.line_width_set(_lt)
    draw_circle_2d(_p,_co,_r,segments=_seg)
    state.line_width_set(1.0)
    state.blend_set('NONE')
def DiSilueta(_p,_s,_i,_co,_bco,_op,_use_alpha: float = 1.0, s=sh_silueta):
    if _i is None:
        return
    t=get_tex(_i) if not isinstance(_i,TEX) else _i
    b=bat(s, TF,{p:(
    _p,(_p.x+_s.x,_p.y),
    _p+_s,(_p.x,_p.y+_s.y)),
    texidx:((0,0),(1,0),(1,1),(0,1)),},)
    s.bind()
    s.uniform_float('co',_co)
    s.uniform_float('bco',_bco)
    s.uniform_float('alpha',_op)
    s.uniform_float('use_transp',_use_alpha)
    s.uniform_sampler(i,t)
    state.blend_set(A);b.draw(s);state.blend_set('NONE')
def DiLiveSilueta(_ctx,_p,_s,_co,_bco,_op):
    i=_ctx
    DiSilueta(_p,_s,i,_co,_bco,_op,1.0)
def DiIma(_p,_s,_i,s=sh_img):
    if _i is None:
        return
    t=get_tex(_i) if not isinstance(_i,TEX) else _i
    b=bat(s, T,{p:(
    (_p.x,_p.y+_s.y),_p,
    (_p.x+_s.x,_p.y),_p+_s),
    texidx:((0,1),(0,0),(1,0),(1,1)),},
    indices=((0,1,2),(2,3,0)))
    s.bind()
    #s.uniform_float(co,(.9,.9,.9,1))
    s.uniform_sampler(i,t)
    state.blend_set(A);b.draw(s);state.blend_set('NONE')
def DiImagl(_p,_s,_i,s=sh_img):
    if _i is None:
        return
    b=bat(s, TF,{p:(
    _p,(_p.x+_s.x,_p.y),
    _p+_s,(_p.x,_p.y+_s.y)),
    texidx:((0,0),(1,0),(1,1),(0,1)),},)
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D,_i)
    s.bind()
    s.uniform_int(i, 0)
    b.draw(s)
def DiImaco(_p,_s,_i,_co,s=sh_img_co):
    if _i is None:
        return
    t=get_tex(_i) if not isinstance(_i,TEX) else _i
    b=bat(s, T,{p:(
    (_p.x,_p.y+_s.y),_p,
    (_p.x+_s.x,_p.y),_p+_s),
    texidx:((0,1),(0,0),(1,0),(1,1)),},
    indices=((0,1,2),(2,3,0)))
    s.bind()
    s.uniform_float(co,_co)
    s.uniform_sampler(i,t)
    state.blend_set(A);b.draw(s);state.blend_set('NONE')
def DiImaOpGamHl(_p,_s,_i,_op:float=1.0,_hl:int=0,s=sh_img_a_op_gam_hl):
    if _i is None:
        return
    t=get_tex(_i) if not isinstance(_i,TEX) else _i
    b=bat(s, T,{p:(
    (_p.x,_p.y+_s.y),_p,
    (_p.x+_s.x,_p.y),_p+_s),
    texidx:((0,1),(0,0),(1,0),(1,1)),},
    indices=((0,1,2),(2,3,0)))
    s.bind()
    s.uniform_float(op,_op)
    s.uniform_float(hl,_hl)
    s.uniform_sampler(i,t)
    state.blend_set(A);b.draw(s);state.blend_set('NONE')
def DiBr(_p,_s,_b,_act=False,_op=1):
    DiImaOpGamHl(_p,_s,get_brush_tex(_b),_op=_op,_hl=int(_act))
    #ico=BrushIcon.from_brush(_b)
    #if ico:DiIma(_p,_s,ico)#;DiIma(_p,_s,ico)
def DiIco(_p,_s,_i):
    DiIma(_p,_s,get_ui_image_tex(_i))
def DiIcoCol(_p,_s,_i,_co):
    DiImaco(_p,_s,get_ui_image_tex(_i),_co)
def DiIcoOpGamHl(_p,_s,_i,_op=1.0,_hl=0):
    DiImaOpGamHl(_p,_s,get_ui_image_tex(_i),_op,_hl)
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
def DiTri(_p,_co,s=sh_unif):
    b=bat(s,T,{p:_p},indices=((0,1,2),))
    s.bind()
    s.uniform_float(co,_co)
    state.blend_set(A)
    #glEnable(GL_BLEND)
    b.draw(s)
    state.blend_set('NONE')
    #glDisable(GL_BLEND)
def DiTriCorner(_corner_origin,_cateto_length,_corner_idname,_co,s=sh_unif):
    if _corner_idname == 'TOP_LEFT':
        _p = (
            _corner_origin,
            _corner_origin-Vector((0, _cateto_length)),
            _corner_origin+Vector((_cateto_length, 0))
        )
    elif _corner_idname == 'BOT_LEFT':
        _p = (
            _corner_origin,
            _corner_origin+Vector((0, _cateto_length)),
            _corner_origin+Vector((_cateto_length, 0))
        )
    elif _corner_idname == 'TOP_RIGHT':
        _p = (
            _corner_origin,
            _corner_origin-Vector((0, _cateto_length)),
            _corner_origin-Vector((_cateto_length, 0))
        )
    elif _corner_idname == 'BOT_RIGHT':
        _p = (
            _corner_origin,
            _corner_origin+Vector((0, _cateto_length)),
            _corner_origin-Vector((_cateto_length, 0))
        )
    DiTri(_p,_co,s)
def DiStar(_p,_size,s=sh_estrellita):
    b=bat(s,P,{p:[_p]})
    state.blend_set(A)
    state.point_size_set(_size)
    b.draw(s)
    state.point_size_set(1.0)
    state.blend_set('NONE')
def DiText(_p, _text, _size, _scale,  _co=(.92, .92, .92, 1.0), pivot=None, shadow_props: dict = None, draw_rect_props: dict = None, id:int=None, rotation:float=None):
    id=font_info['id'] if id is None else id
    text_color(id, *_co)
    text_size(id, max(7.5, _size), int(72*_scale))
    if rotation is not None:
        text_enable(id, ROTATION)
        text_rotation(id, rotation)
    if shadow_props is not None:
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
    if draw_rect_props is not None:
        dim = dim if dim else text_dim(id, _text)
        color = draw_rect_props.get('color', (.1, .1, .1, .8))
        margin: float = draw_rect_props.get('margin', 3) * _scale
        _p = Vector(_p) - Vector((margin, margin))
        s = Vector((dim)) + Vector((margin, margin)) * 2.0
        DiRct(_p, s, color)
        DiCage(_p, s, 2.2, draw_rect_props.get('outline_color', Vector(color)*.9))
    text_draw(id, _text)
    if shadow_props is not None:
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
def get_rect_center(p,s):
    return p+s*.5