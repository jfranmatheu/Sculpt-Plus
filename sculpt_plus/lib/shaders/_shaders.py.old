class ShType:
    POINT       = 'POINTS'
    LINE        = 'LINES'
    IMG         = 'TRI_FAN'
    TRI         = 'TRIS'
    RCT         = 'TRIS'
    SHAPE       = 'TRIS' 
class VSH:
    V1b4d5bcd0bb8450f8da2d7e0d9049934 = """uniform mat4 ModelViewProjectionMatrix;uniform vec4 rect;uniform int cornerLen;uniform float scale;in vec2 pos;out vec2 uv;void main()
    {
      int corner_id = (gl_VertexID / cornerLen) % 4;
      vec2 final_pos = pos * scale;
      if (corner_id == 0) {
        uv = pos + vec2(1.0, 1.0);
      }
      else if (corner_id == 2) {
        uv = pos + vec2(-1.0, -1.0);
      }
      gl_Position = (ModelViewProjectionMatrix * vec4(final_pos, 0.0, 1.0));
    }
    """
    V269e45bede5f44d1b83bfb27e4909e84 = """uniform mat4 ModelViewProjectionMatrix;in vec2 pos;void main()
    {
        gl_Position = ModelViewProjectionMatrix * vec4(pos, 1.0, 1.0);
    }
    """
    V626e4c8b3bcc4352a9afc948043d5080 = """uniform mat4 ModelViewProjectionMatrix;in vec2 texco;in vec2 pos;out vec2 texco_interp;void main()
    {
     gl_Position = ModelViewProjectionMatrix * vec4(pos, 1.0, 1.0);
     texco_interp = texco;
    }
    """
    V14959ef82915463ba04faf325903143d = """uniform mat4 ModelViewProjectionMatrix;uniform vec2 ViewportSize = vec2(-1, -1);uniform float outline_scale = 1.0;const float line_falloff = 1.0;const float circle_scale = sqrt(2.0 / 3.1416);const float square_scale = sqrt(0.5);const float diagonal_scale = sqrt(0.5);in vec2 pos;in float size;in vec4 color;in vec4 outlineColor;in int flags;flat out vec4 finalColor;flat out vec4 finalOutlineColor;flat out int finalFlags;flat out vec4 radii;flat out vec4 thresholds;bool test(int bit)
    {
      return (flags & bit) != 0;
    }
    vec2 line_thresholds(float width)
    {
      return vec2(max(0, width - line_falloff), width);
    }
    void main()
    {
      gl_Position = ModelViewProjectionMatrix * vec4(pos, 0.0, 1.0);
      finalColor = color;
      finalOutlineColor = outlineColor;
      finalFlags = flags;
      if (!test(0xF)) {
        finalFlags |= 1;
      }
      thresholds.xy = line_thresholds(line_width * outline_scale);
      float ext_radius = round(0.5 * size) + thresholds.x;
      gl_PointSize = ceil(ext_radius + thresholds.y) * 2 + 1;
      radii[1] = ext_radius * circle_scale;
      radii[3] = -line_falloff;
    """
    V343867d12c2e49e487a3dd93eb4ed766 = """uniform mat4 ModelViewProjectionMatrix;uniform float size;in vec2 pos;void main()
    {
        gl_Position = ModelViewProjectionMatrix * vec4(pos, 1.0, 1.0);
        gl_PointSize = size;
    }
    """
    Va1722d49e3d9438c9a879781e43e1e92 = """uniform mat4 ModelViewProjectionMatrix;uniform float size;in vec2 pos;out vec2 radii;void main()
    {
      gl_Position = ModelViewProjectionMatrix * vec4(pos, 0.0, 1.0);
      gl_PointSize = size;
      float radius = 0.5 * size;
      radii[0] = radius;
      radii[1] = radius - 1.0;
      radii /= size;
    }
    """
    V7e030cc5dba64c8fa7e07b3c9ff8e32f = """uniform mat4 ModelViewProjectionMatrix;#ifdef USE_WORLD_CLIP_PLANES
    uniform mat4 ModelMatrix;#endif
    uniform float size;in vec3 pos;out vec2 radii;void main()
    {
      vec4 pos_4d = vec4(pos, 1.0);
      gl_Position = ModelViewProjectionMatrix * pos_4d;
      gl_PointSize = size;
      float radius = 0.5 * size;
      radii[0] = radius;
      radii[1] = radius - 1.0;
      radii /= size;
    #ifdef USE_WORLD_CLIP_PLANES
      world_clip_planes_calc_clip_distance((ModelMatrix * pos_4d).xyz);
    #endif
    }
    """
    V5a627615ffc44026829d9ad9cad99059 = """uniform mat4 ModelViewProjectionMatrix;  float x = float(gl_VertexID % 2);
      float y = float(gl_VertexID / 2);
      vec2 quad = vec2(x, y);
      vec2 interp_offset = float(interp_size) / abs(pos.zw - pos.xy);
      texCoord_interp = mix(-interp_offset, 1.0 + interp_offset, quad);
      vec2 final_pos = mix(
          pos.xy + ivec2(-interp_size, interp_size), pos.zw + ivec2(interp_size, -interp_size), quad);
      gl_Position = ModelViewProjectionMatrix * vec4(final_pos, 0.0, 1.0);
    }
    """
    V5b59af3b410046349183467a0a42d48c = """uniform mat4 ModelViewProjectionMatrix;in vec2 pos;in vec2 texco;out vec2 uv;void main()
    {
      uv = texco;
      gl_Position = (ModelViewProjectionMatrix * vec4(pos, 0.0, 1.0));
    }
    """
class FSH:
    F433323c5d24d4ddd8b57c922a7471c54 = """uniform vec4 color;uniform float scale;in vec2 uv;out vec4 fragColor;void main()
    {
    """
    F6a9320b1544e442d91982e14e1740ebe = """uniform vec4 col;out vec4 fragColor;void main()
    {
      fragColor = col;
    }
    """
    Fd21d34d84ac54149ae49b4c92dafbd77 = """in vec2 texco_interp;out vec4 fragColor;uniform sampler2D image;void main()
    {
     fragColor = texture(image, texco_interp);
    }
    """
    F4b1a4e29fe2a4e6986422b43135e57dc = """in vec2 texco_interp;out vec4 fragColor;uniform sampler2D image;void main()
    {
     vec4 texColor = texture(image, texco_interp);
     if(texColor.a < 0.05)
      discard;
     fragColor = texColor;
    }
    """
    F4fa90ce15dc74f39842b8ceb2719c9ad = """flat in vec4 radii;flat in vec4 thresholds;flat in vec4 finalColor;flat in vec4 finalOutlineColor;flat in int finalFlags;out vec4 fragColor;const float diagonal_scale = sqrt(0.5);const float minmax_bias = 0.7;const float minmax_scale = sqrt(1.0 / (1.0 + 1.0 / minmax_bias));bool test(int bit)
    {
      return (finalFlags & bit) != 0;
    }
    void main()
    {
      vec2 pos = gl_PointCoord - vec2(0.5);
      vec2 absPos = abs(pos);
      float radius = (absPos.x + absPos.y) * diagonal_scale;
      float outline_dist = -1.0;
      if (test(0x2)) {
        radius = length(absPos);
        outline_dist = max(outline_dist, radius - radii[1]);
      }
      if (test(0x8)) {
        outline_dist = max(outline_dist, absPos.x - radii[2]);
      }
      float alpha = 1 - smoothstep(thresholds[0], thresholds[1], abs(outline_dist));
        if (test(0x10)) {
          alpha = max(alpha, 1 - smoothstep(thresholds[2], thresholds[3], radius));
        }
          if (test(0x100)) {
            ypos = max(ypos, pos.y);
          }
          float minmax_dist = (ypos - radii[3]) - absPos.x * minmax_bias;
          float minmax_step = smoothstep(thresholds[0], thresholds[1], minmax_dist * minmax_scale);
      else {
        fragColor = vec4(finalOutlineColor.rgb, finalOutlineColor.a * alpha);
      }
    }
    """
    Ffe18947616754b40bde85d28c9ffc3a5 = """in vec2 uv;out vec4 fragColor;uniform vec2 u_dimensions;uniform vec3 u_color;uniform float u_input_output;const float u_radius = 4.5;const float u_radius_in_out = u_radius * 3.0;const float color_line_thickness = 4.0;const float header_height = 36.0;const vec3 header_color = vec3(0.125); //  vec3(.08); //const vec3 header_color_gradient = vec3(0.1019);const vec3 body_color   = vec3(0.157); // vec3(.11); // #  define cir_top_left (vec2(0, u_dimensions.y) + vec2(u_radius, -u_radius))
    #  define cir_top_right (vec2(u_dimensions.x, u_dimensions.y) + vec2(-u_radius, -u_radius))
    #  define cir_bot_left (u_input_output == 1 ? vec2(u_radius_in_out) : vec2(u_radius))
    #  define cir_bot_right (u_input_output == 2 ? vec2(u_dimensions.x, 0) + vec2(-u_radius_in_out, u_radius_in_out) : vec2(u_dimensions.x, 0) + vec2(-u_radius, u_radius))
    void main()
    {
      vec2 coords = uv * u_dimensions;
      vec3 color = body_color; // vec3(uv.xy, 0.0); // position map
      float radius = u_radius;
      float amp_radius = radius + 1.0;
      float alpha = 1.0;
      float len = 0.0;
      bool is_bottom_curve = false;
      if (coords.x < cir_top_left.x && coords.y > cir_top_left.y && length(coords - cir_top_left) > radius)
      {
        len = length(coords - cir_top_left);
      }
      else if (coords.x > cir_top_right.x && coords.y > cir_top_right.y && length(coords - cir_top_right) > radius)
      {
        len = length(coords - cir_top_right);
      }
      else if (coords.x < cir_bot_left.x && coords.y < cir_bot_left.y)
      {
        if (u_input_output == 1)
        {
          radius *= 3.0;
          amp_radius = radius + 1.0;
        }
        len = length(coords - cir_bot_left);
        if (len > radius - 2)
        {
          if (len > radius)
          {
            len = length(coords - cir_bot_left);
          }
          is_bottom_curve = true;
        }
        else
        {
          len = 0.0;
        }
      }
      else if (coords.x > cir_bot_right.x && coords.y < cir_bot_right.y)
      {
        if (u_input_output == 2)
        {
          radius *= 3.0;
          amp_radius = radius + 1.0;
        } 
        len = length(coords - cir_bot_right);
        if (len > radius - 2)
        {
          if (len > radius)
          {
            len = length(coords - cir_bot_left);
          }
          is_bottom_curve = true;
        }
        else
        {
          len = 0.0;
        }
      }
      if (len > amp_radius)
        discard;
      else
        alpha = smoothstep(amp_radius, radius-0.65, len) * 1.2;
      
      if (is_bottom_curve)
        color = header_color;
      else if (coords.y > (u_dimensions.y - header_height))
      {
        if (coords.y < (u_dimensions.y - header_height + 10.0))
        {
          color = mix(header_color, header_color_gradient, smoothstep(u_dimensions.y - header_height + 10.0, u_dimensions.y - header_height, coords.y));
        }
        else
        {
          color = header_color;
        }
      }
      else if (coords.y > (u_dimensions.y - header_height - color_line_thickness))
        color = u_color;
      else if (coords.x > (u_dimensions.x - 2) || coords.x < 2) // value precision error in > vs <
        color = header_color;
      else if (coords.y < 2)
        color = header_color;
      fragColor = vec4(color, alpha);
    }
    """
    Fd316e8f8cb84404eb62396c759ef067c = """#ifdef GL_ES
    precision mediump float;
    #endif
    uniform vec4 col;out vec4 fragColor;float roundedFrame (float d, float thickness)
    {
      return smoothstep(0.55, 0.45, abs(d / thickness) * 5.0);
    }
    void main()
    {
      float r = 0.0;
      vec2 cxy = 2.0 * gl_PointCoord - 1.0;
      r = dot(cxy, cxy);
      
      float s = roundedFrame(r, 9.5);
      if (s < 0.05)
        discard;
      fragColor = col;
      fragColor.a *= s;
    }
    """
    F7a4e7852ec3d4a059c923d37642a93a0 = """#ifdef GL_ES
    precision mediump float;
    #endif
    uniform vec4 col;out vec4 fragColor;float roundedFrame (float d, float thickness)
    {
      return smoothstep(0.55, 0.45, abs(d / thickness) * 5.0);
    }
    void main()
    {
      float r = 0.0;
      vec2 cxy = 2.0 * gl_PointCoord - 1.0;
      
      if (cxy.y >= 0.5)
        discard;
      
      r = dot(cxy, cxy);
      float s = roundedFrame(r, 9.5);
      if (s < 0.05)
        discard;
      fragColor = col;
      fragColor.a *= s;
    }
    """
    F80d31c191177434db9bc99f05053a5cc = """#ifdef GL_ES
    precision mediump float;
    #endif
    uniform vec4 col;out vec4 fragColor;float roundedFrame (float d, float thickness)
    {
      return smoothstep(0.55, 0.45, abs(d / thickness) * 5.0);
    }
    void main()
    {
      float r = 0.0;
      vec2 cxy = 2.0 * gl_PointCoord - 1.0;
      
      if (cxy.y <= 0.5)
        discard;
      
      r = dot(cxy, cxy);
      
      float s = roundedFrame(r, 9.5);
      if (s < 0.05)
        discard;
      fragColor = col;
      fragColor.a *= s;
    }
    """
    Fa79b657e06774b2b8415f807b7d24117 = """uniform vec4 color;in vec2 radii;out vec4 fragColor;void main()
    {
      float alpha = mix(color.a, 1.0, smoothstep(radii[1], radii[0], length(gl_PointCoord - vec2(0.5))));
      if (alpha < 0.5) {
        discard;
      }
      fragColor.rgb = color.rgb;
      fragColor.a = alpha;
    }
    """
    F30ce8db4556043b3bf85162e7d8d297d = """uniform vec4 color;out vec4 fragColor;void main()
    {
      vec2 centered = gl_PointCoord - vec2(0.5);
      float dist_squared = dot(centered, centered);
      const float rad_squared = 0.25;  if (dist_squared > rad_squared) {
        discard;
      }
      fragColor = color;
    }
    """
    F161a80971ecd45738c4a01ed9df44a0a = """uniform vec4 col;out vec4 fragColor;float roundedFrame (float d, float thickness)
    {
      return smoothstep(0.55, 0.45, abs(d / thickness) * 5.0);
    }
    void main()
    {
      float r = 0.0;
      vec2 cxy = 2.0 * gl_PointCoord - 1.0;
      r = dot(cxy, cxy);
      
      float s = roundedFrame(r, 9.5);
      if (s < 0.05)
        discard;
      fragColor = col;
      fragColor.a *= s;
    }
    float sdStar(in vec2 p, in float r, in int n, in float m) // m=[2,n]
    {
        float an = 3.141593/float(n);
        float en = 3.141593/m;
        vec2  acs = vec2(cos(an),sin(an));
        vec2  ecs = vec2(cos(en),sin(en)); // ecs=vec2(0,1) and simplify, for regular polygon,
        float bn = mod(atan(p.x,p.y),2.0*an) - an;
        p = length(p)*vec2(cos(bn),abs(sin(bn)));
        p -= r*acs;
        p += ecs*clamp( -dot(p,ecs), 0.0, r*acs.y/ecs.y);
        return length(p)*sign(p.x);
    }
    void mainImage(out vec4 fragColor, in vec2 fragCoord)
    {
    	vec2 p = (2.0*fragCoord-iResolution.xy)/iResolution.y;
        vec2 m = (2.0*iMouse.xy-iResolution.xy)/iResolution.y;
            
        float t = iTime/3.0;
        float n = 4.0;  // n, number of sides
        float a = 1.0;                 // angle factor
        float w = 3.0;        // angle divisor, between 2 and n
        
        float d = sdStar( p, 0.7, int(n), w );
        
        vec3 col = (d>0.0) ? vec3(0.0,0.0,0.0) : vec3(1.0,0.9,0.5);
        float opa = (d>0.0) ? 0.0 : 1.0;
    	//col *= 1.05 - exp(-6.0*abs(d));
    	//col *= 0.8 + 0.2*cos(110.0*d);
    	col = mix( col, vec3(1.0), 1.0-smoothstep(0.0,0.015,abs(d)) );
    	fragColor = vec4(col,opa);}
    """
    Fae407a18cf574aeeb1e7a63c37d7c77e = """flat in vec4 color_flat;noperspective in vec2 texCoord_interp;
    flat in int glyph_offset;flat in ivec2 glyph_dim;flat in int interp_size;out vec4 fragColor;uniform sampler1DArray glyph;const vec2 offsets4[4] = vec2[4](    vec2(-0.5, 0.5), vec2(0.5, 0.5), vec2(-0.5, -0.5), vec2(-0.5, -0.5));
    const vec2 offsets16[16] = vec2[16](vec2(-1.5, 1.5),                                    vec2(-0.5, 1.5),
                                        vec2(0.5, 1.5),
                                        vec2(1.5, 1.5),
                                        vec2(-1.5, 0.5),
                                        vec2(-0.5, 0.5),
                                        vec2(0.5, 0.5),
                                        vec2(1.5, 0.5),
                                        vec2(-1.5, -0.5),
                                        vec2(-0.5, -0.5),
                                        vec2(0.5, -0.5),
                                        vec2(1.5, -0.5),
                                        vec2(-1.5, -1.5),
                                        vec2(-0.5, -1.5),
                                        vec2(0.5, -1.5),
                                        vec2(1.5, -1.5));
    #define sample_glyph_offset(texel, ofs) \
      texture_1D_custom_bilinear_filter(texCoord_interp + ofs * texel)
    float texel_fetch(int index)
    {
      int size_x = textureSize(glyph, 0).r;
      if (index >= size_x) {
        return texelFetch(glyph, ivec2(index % size_x, index / size_x), 0).r;
      }
      return texelFetch(glyph, ivec2(index, 0), 0).r;
    }
    bool is_inside_box(ivec2 v)
    {
      return all(greaterThanEqual(v, ivec2(0))) && all(lessThan(v, glyph_dim));
    }
    float texture_1D_custom_bilinear_filter(vec2 uv)
    {
      vec2 texel_2d = uv * glyph_dim + 0.5;
      ivec2 texel_2d_near = ivec2(texel_2d) - 1;
      int frag_offset = glyph_offset + texel_2d_near.y * glyph_dim.x + texel_2d_near.x;
      float tl = 0.0;
      if (is_inside_box(texel_2d_near)) {
        tl = texel_fetch(frag_offset);
      }
    #ifdef GPU_NEAREST
      return tl;
    #else  // GPU_LINEAR
      int offset_x = 1;
      int offset_y = glyph_dim.x;
      float tr = 0.0;
      float bl = 0.0;
      float br = 0.0;
      if (is_inside_box(texel_2d_near + ivec2(1, 0))) {
        tr = texel_fetch(frag_offset + offset_x);
      }
      if (is_inside_box(texel_2d_near + ivec2(0, 1))) {
        bl = texel_fetch(frag_offset + offset_y);
      }
      if (is_inside_box(texel_2d_near + ivec2(1, 1))) {
        br = texel_fetch(frag_offset + offset_x + offset_y);
      }
      vec2 f = fract(texel_2d);
      float tA = mix(tl, tr, f.x);
      float tB = mix(bl, br, f.x);
      return mix(tA, tB, f.y);
    #endif
    }
    void main()
    {
      fragColor.rgb = color_flat.rgb;
      if (interp_size == 0) {
        fragColor.a = texture_1D_custom_bilinear_filter(texCoord_interp);
      }
      else {
        vec2 texel = 1.0 / glyph_dim;
        fragColor.a = 0.0;
        if (interp_size == 1) {
          fragColor.a += sample_glyph_offset(texel, offsets4[0]);
          fragColor.a += sample_glyph_offset(texel, offsets4[1]);
          fragColor.a += sample_glyph_offset(texel, offsets4[2]);
          fragColor.a += sample_glyph_offset(texel, offsets4[3]);
          fragColor.a *= (1.0 / 4.0);
        }
        else {
          fragColor.a += sample_glyph_offset(texel, offsets16[0]);
          fragColor.a += sample_glyph_offset(texel, offsets16[1]);
          fragColor.a += sample_glyph_offset(texel, offsets16[2]);
          fragColor.a += sample_glyph_offset(texel, offsets16[3]);
          fragColor.a += sample_glyph_offset(texel, offsets16[4]);
          fragColor.a += sample_glyph_offset(texel, offsets16[5]) * 2.0;
          fragColor.a += sample_glyph_offset(texel, offsets16[6]) * 2.0;
          fragColor.a += sample_glyph_offset(texel, offsets16[7]);
          fragColor.a += sample_glyph_offset(texel, offsets16[8]);
          fragColor.a += sample_glyph_offset(texel, offsets16[9]) * 2.0;
          fragColor.a += sample_glyph_offset(texel, offsets16[10]) * 2.0;
          fragColor.a += sample_glyph_offset(texel, offsets16[11]);
          fragColor.a += sample_glyph_offset(texel, offsets16[12]);
          fragColor.a += sample_glyph_offset(texel, offsets16[13]);
          fragColor.a += sample_glyph_offset(texel, offsets16[14]);
          fragColor.a += sample_glyph_offset(texel, offsets16[15]);
          fragColor.a *= (1.0 / 20.0);
        }
      }
      fragColor.a *= color_flat.a;
      fragColor = blender_srgb_to_framebuffer_space(fragColor);
    }
    """
from bpy.types import Image
from gpu_extras.batch import batch_for_shader as batsh
from gpu.types import GPUShader as gpush
class SH:
    GPUSH433323c5d24d4ddd8b57c922a7471c54 = gpush(VSH.V1b4d5bcd0bb8450f8da2d7e0d9049934,FSH.F433323c5d24d4ddd8b57c922a7471c54)
    GPUSH6a9320b1544e442d91982e14e1740ebe = gpush(VSH.V269e45bede5f44d1b83bfb27e4909e84,FSH.F6a9320b1544e442d91982e14e1740ebe)
    GPUSHd21d34d84ac54149ae49b4c92dafbd77 = gpush(VSH.V626e4c8b3bcc4352a9afc948043d5080,FSH.Fd21d34d84ac54149ae49b4c92dafbd77)
    GPUSH4b1a4e29fe2a4e6986422b43135e57dc = gpush(VSH.V626e4c8b3bcc4352a9afc948043d5080,FSH.F4b1a4e29fe2a4e6986422b43135e57dc)
    GPUSH4fa90ce15dc74f39842b8ceb2719c9ad = gpush(VSH.V14959ef82915463ba04faf325903143d,FSH.F4fa90ce15dc74f39842b8ceb2719c9ad)
    GPUSHfe18947616754b40bde85d28c9ffc3a5 = gpush(VSH.V5b59af3b410046349183467a0a42d48c,FSH.Ffe18947616754b40bde85d28c9ffc3a5)
    GPUSHd316e8f8cb84404eb62396c759ef067c = gpush(VSH.V343867d12c2e49e487a3dd93eb4ed766,FSH.Fd316e8f8cb84404eb62396c759ef067c)
    GPUSH7a4e7852ec3d4a059c923d37642a93a0 = gpush(VSH.V343867d12c2e49e487a3dd93eb4ed766,FSH.F7a4e7852ec3d4a059c923d37642a93a0)
    GPUSH80d31c191177434db9bc99f05053a5cc = gpush(VSH.V343867d12c2e49e487a3dd93eb4ed766,FSH.F80d31c191177434db9bc99f05053a5cc)
    GPUSHa79b657e06774b2b8415f807b7d24117 = gpush(VSH.Va1722d49e3d9438c9a879781e43e1e92,FSH.Fa79b657e06774b2b8415f807b7d24117)
    GPUSH30ce8db4556043b3bf85162e7d8d297d = gpush(VSH.Va1722d49e3d9438c9a879781e43e1e92,FSH.F30ce8db4556043b3bf85162e7d8d297d)
    GPUSH161a80971ecd45738c4a01ed9df44a0a = gpush(VSH.V343867d12c2e49e487a3dd93eb4ed766,FSH.F161a80971ecd45738c4a01ed9df44a0a)
    GPUSHae407a18cf574aeeb1e7a63c37d7c77e = gpush(VSH.V5a627615ffc44026829d9ad9cad99059,FSH.Fae407a18cf574aeeb1e7a63c37d7c77e)
class SH433323c5d24d4ddd8b57c922a7471c54():
    sh=SH.GPUSH433323c5d24d4ddd8b57c922a7471c54
    sh_type=ShType.UV
    sh_geom=ShGeom.UV
    def init_props(self):
        # Uniforms.
        self._color: tuple
        self._scale: float
        # Inputs.
        self._pos: tuple
    # Shader Flags.
    use_uv: bool = False
    use_vertex_color: bool = False
    # Shader specific props.
    def get_inputs(self) -> Dict[str, Any]:
        {"pos":self.pos,}
    @property
    def pos(self) -> tuple:
        return self._pos
    @pos.setter
    def pos(self, value: tuple) -> None:
        self._pos: tuple = value # Cached input value.
    def set_coords(self, coords: tuple or list) -> None:
        self.pos: tuple = coords # Update pos coordinates.
    @property
    def color(self) -> tuple:
        return self._color
    @color.setter
    def color(self, value: tuple) -> None:
        self._color: tuple = value # Cached uniform value.
        self.sh.uniform_float("color", value)
    @property
    def scale(self) -> float:
        return self._scale
    @scale.setter
    def scale(self, value: float) -> None:
        self._scale: float = value # Cached uniform value.
        self.sh.uniform_float("scale", value)
class SH6a9320b1544e442d91982e14e1740ebe():
    sh=SH.GPUSH6a9320b1544e442d91982e14e1740ebe
    sh_type=ShType.TRI
    sh_geom=ShGeom.TRI
    def init_props(self):
        # Uniforms.
        self._col: tuple
        # Inputs.
        self._pos: tuple
    # Shader Flags.
    use_uv: bool = False
    use_vertex_color: bool = False
    # Shader specific props.
    def get_inputs(self) -> Dict[str, Any]:
        {"pos":self.pos,}
    @property
    def pos(self) -> tuple:
        return self._pos
    @pos.setter
    def pos(self, value: tuple) -> None:
        self._pos: tuple = value # Cached input value.
    def set_coords(self, coords: tuple or list) -> None:
        self.pos: tuple = coords # Update pos coordinates.
    @property
    def col(self) -> tuple:
        return self._col
    @col.setter
    def col(self, value: tuple) -> None:
        self._col: tuple = value # Cached uniform value.
        self.sh.uniform_float("col", value)
class SHd21d34d84ac54149ae49b4c92dafbd77():
    sh=SH.GPUSHd21d34d84ac54149ae49b4c92dafbd77
    sh_type=ShType.IMG
    sh_geom=ShGeom.IMG
    def init_props(self):
        # Uniforms.
        self._image: Image
        # Inputs.
        self._texco: tuple = ((0,0),(1,0),(1,1),(0,1))
        self._pos: tuple
    # Shader Flags.
    use_uv: bool = True
    use_vertex_color: bool = False
    # Shader specific props.
    def get_inputs(self) -> Dict[str, Any]:
        {"texco":self.texco,"pos":self.pos,}
    @property
    def texco(self) -> tuple:
        return self._texco
    @texco.setter
    def texco(self, value: tuple) -> None:
        self._texco: tuple = value # Cached input value.
    def set_uv(self, uv: tuple or list) -> None:
        self.texco: tuple = uv # Update uv indices.
    @property
    def pos(self) -> tuple:
        return self._pos
    @pos.setter
    def pos(self, value: tuple) -> None:
        self._pos: tuple = value # Cached input value.
    def set_coords(self, coords: tuple or list) -> None:
        self.pos: tuple = coords # Update pos coordinates.
    @property
    def image(self) -> Image:
        return self._image
    @image.setter
    def image(self, value: Image) -> None:
        self._image: Image = value # Cached uniform value.
        self.sh.uniform_sampler("image", value)
class SH4b1a4e29fe2a4e6986422b43135e57dc():
    sh=SH.GPUSH4b1a4e29fe2a4e6986422b43135e57dc
    sh_type=ShType.IMG
    sh_geom=ShGeom.IMG
    def init_props(self):
        # Uniforms.
        self._image: Image
        # Inputs.
        self._texco: tuple = ((0,0),(1,0),(1,1),(0,1))
        self._pos: tuple
    # Shader Flags.
    use_uv: bool = True
    use_vertex_color: bool = False
    # Shader specific props.
    def get_inputs(self) -> Dict[str, Any]:
        {"texco":self.texco,"pos":self.pos,}
    @property
    def texco(self) -> tuple:
        return self._texco
    @texco.setter
    def texco(self, value: tuple) -> None:
        self._texco: tuple = value # Cached input value.
    def set_uv(self, uv: tuple or list) -> None:
        self.texco: tuple = uv # Update uv indices.
    @property
    def pos(self) -> tuple:
        return self._pos
    @pos.setter
    def pos(self, value: tuple) -> None:
        self._pos: tuple = value # Cached input value.
    def set_coords(self, coords: tuple or list) -> None:
        self.pos: tuple = coords # Update pos coordinates.
    @property
    def image(self) -> Image:
        return self._image
    @image.setter
    def image(self, value: Image) -> None:
        self._image: Image = value # Cached uniform value.
        self.sh.uniform_sampler("image", value)
class SH4fa90ce15dc74f39842b8ceb2719c9ad():
    sh=SH.GPUSH4fa90ce15dc74f39842b8ceb2719c9ad
    sh_type=ShType.POINT
    sh_geom=ShGeom.POINT
    def init_props(self):
        # Uniforms.
        # Inputs.
        self._pos: tuple
        self._size: float
        self._color: tuple
        self._outlineColor: tuple
        self._flags: int
        self.point_scale: float = 1.0
    # Shader Flags.
    use_uv: bool = False
    use_vertex_color: bool = True
    # Shader specific props.
    def get_inputs(self) -> Dict[str, Any]:
        {"pos":self.pos,"size":self.size,"color":self.color,"outlineColor":self.outlineColor,"flags":self.flags,}
    @property
    def pos(self) -> tuple:
        return self._pos
    @pos.setter
    def pos(self, value: tuple) -> None:
        self._pos: tuple = value # Cached input value.
    def set_coords(self, coords: tuple or list) -> None:
        self.pos: tuple = coords # Update pos coordinates.
    @property
    def size(self) -> float:
        return self._size
    @size.setter
    def size(self, value: float) -> None:
        self._size: float = value # Cached input value.
    @property
    def color(self) -> tuple:
        return self._color
    @color.setter
    def color(self, value: tuple) -> None:
        self._color: tuple = value # Cached input value.
    @property
    def outlineColor(self) -> tuple:
        return self._outlineColor
    @outlineColor.setter
    def outlineColor(self, value: tuple) -> None:
        self._outlineColor: tuple = value # Cached input value.
    @property
    def flags(self) -> int:
        return self._flags
    @flags.setter
    def flags(self, value: int) -> None:
        self._flags: int = value # Cached input value.
class SHfe18947616754b40bde85d28c9ffc3a5():
    sh=SH.GPUSHfe18947616754b40bde85d28c9ffc3a5
    sh_type=ShType.IMG
    sh_geom=ShGeom.IMG
    def init_props(self):
        # Uniforms.
        self._u_dimensions: tuple
        self._u_color: tuple
        self._u_input_output: float
        # Inputs.
        self._pos: tuple
        self._texco: tuple = ((0,0),(1,0),(1,1),(0,1))
    # Shader Flags.
    use_uv: bool = True
    use_vertex_color: bool = False
    # Shader specific props.
    def get_inputs(self) -> Dict[str, Any]:
        {"pos":self.pos,"texco":self.texco,}
    @property
    def pos(self) -> tuple:
        return self._pos
    @pos.setter
    def pos(self, value: tuple) -> None:
        self._pos: tuple = value # Cached input value.
    def set_coords(self, coords: tuple or list) -> None:
        self.pos: tuple = coords # Update pos coordinates.
    @property
    def texco(self) -> tuple:
        return self._texco
    @texco.setter
    def texco(self, value: tuple) -> None:
        self._texco: tuple = value # Cached input value.
    def set_uv(self, uv: tuple or list) -> None:
        self.texco: tuple = uv # Update uv indices.
    @property
    def u_dimensions(self) -> tuple:
        return self._u_dimensions
    @u_dimensions.setter
    def u_dimensions(self, value: tuple) -> None:
        self._u_dimensions: tuple = value # Cached uniform value.
        self.sh.uniform_float("u_dimensions", value)
    @property
    def u_color(self) -> tuple:
        return self._u_color
    @u_color.setter
    def u_color(self, value: tuple) -> None:
        self._u_color: tuple = value # Cached uniform value.
        self.sh.uniform_float("u_color", value)
    @property
    def u_input_output(self) -> float:
        return self._u_input_output
    @u_input_output.setter
    def u_input_output(self, value: float) -> None:
        self._u_input_output: float = value # Cached uniform value.
        self.sh.uniform_float("u_input_output", value)
class SHd316e8f8cb84404eb62396c759ef067c():
    sh=SH.GPUSHd316e8f8cb84404eb62396c759ef067c
    sh_type=ShType.POINT
    sh_geom=ShGeom.POINT
    def init_props(self):
        # Uniforms.
        self._col: tuple
        # Inputs.
        self._pos: tuple
        self.point_scale: float = 1.0
    # Shader Flags.
    use_uv: bool = False
    use_vertex_color: bool = False
    # Shader specific props.
    def get_inputs(self) -> Dict[str, Any]:
        {"pos":self.pos,}
    @property
    def pos(self) -> tuple:
        return self._pos
    @pos.setter
    def pos(self, value: tuple) -> None:
        self._pos: tuple = value # Cached input value.
    def set_coords(self, coords: tuple or list) -> None:
        self.pos: tuple = coords # Update pos coordinates.
    @property
    def col(self) -> tuple:
        return self._col
    @col.setter
    def col(self, value: tuple) -> None:
        self._col: tuple = value # Cached uniform value.
        self.sh.uniform_float("col", value)
class SH7a4e7852ec3d4a059c923d37642a93a0():
    sh=SH.GPUSH7a4e7852ec3d4a059c923d37642a93a0
    sh_type=ShType.POINT
    sh_geom=ShGeom.POINT
    def init_props(self):
        # Uniforms.
        self._col: tuple
        # Inputs.
        self._pos: tuple
        self.point_scale: float = 1.0
    # Shader Flags.
    use_uv: bool = False
    use_vertex_color: bool = False
    # Shader specific props.
    def get_inputs(self) -> Dict[str, Any]:
        {"pos":self.pos,}
    @property
    def pos(self) -> tuple:
        return self._pos
    @pos.setter
    def pos(self, value: tuple) -> None:
        self._pos: tuple = value # Cached input value.
    def set_coords(self, coords: tuple or list) -> None:
        self.pos: tuple = coords # Update pos coordinates.
    @property
    def col(self) -> tuple:
        return self._col
    @col.setter
    def col(self, value: tuple) -> None:
        self._col: tuple = value # Cached uniform value.
        self.sh.uniform_float("col", value)
class SH80d31c191177434db9bc99f05053a5cc():
    sh=SH.GPUSH80d31c191177434db9bc99f05053a5cc
    sh_type=ShType.POINT
    sh_geom=ShGeom.POINT
    def init_props(self):
        # Uniforms.
        self._col: tuple
        # Inputs.
        self._pos: tuple
        self.point_scale: float = 1.0
    # Shader Flags.
    use_uv: bool = False
    use_vertex_color: bool = False
    # Shader specific props.
    def get_inputs(self) -> Dict[str, Any]:
        {"pos":self.pos,}
    @property
    def pos(self) -> tuple:
        return self._pos
    @pos.setter
    def pos(self, value: tuple) -> None:
        self._pos: tuple = value # Cached input value.
    def set_coords(self, coords: tuple or list) -> None:
        self.pos: tuple = coords # Update pos coordinates.
    @property
    def col(self) -> tuple:
        return self._col
    @col.setter
    def col(self, value: tuple) -> None:
        self._col: tuple = value # Cached uniform value.
        self.sh.uniform_float("col", value)
class SHa79b657e06774b2b8415f807b7d24117():
    sh=SH.GPUSHa79b657e06774b2b8415f807b7d24117
    sh_type=ShType.POINT
    sh_geom=ShGeom.POINT
    def init_props(self):
        # Uniforms.
        self._color: tuple
        # Inputs.
        self._pos: tuple
        self.point_scale: float = 1.0
    # Shader Flags.
    use_uv: bool = False
    use_vertex_color: bool = False
    # Shader specific props.
    def get_inputs(self) -> Dict[str, Any]:
        {"pos":self.pos,}
    @property
    def pos(self) -> tuple:
        return self._pos
    @pos.setter
    def pos(self, value: tuple) -> None:
        self._pos: tuple = value # Cached input value.
    def set_coords(self, coords: tuple or list) -> None:
        self.pos: tuple = coords # Update pos coordinates.
    @property
    def color(self) -> tuple:
        return self._color
    @color.setter
    def color(self, value: tuple) -> None:
        self._color: tuple = value # Cached uniform value.
        self.sh.uniform_float("color", value)
class SH30ce8db4556043b3bf85162e7d8d297d():
    sh=SH.GPUSH30ce8db4556043b3bf85162e7d8d297d
    sh_type=ShType.POINT
    sh_geom=ShGeom.POINT
    def init_props(self):
        # Uniforms.
        self._color: tuple
        # Inputs.
        self._pos: tuple
        self.point_scale: float = 1.0
    # Shader Flags.
    use_uv: bool = False
    use_vertex_color: bool = False
    # Shader specific props.
    def get_inputs(self) -> Dict[str, Any]:
        {"pos":self.pos,}
    @property
    def pos(self) -> tuple:
        return self._pos
    @pos.setter
    def pos(self, value: tuple) -> None:
        self._pos: tuple = value # Cached input value.
    def set_coords(self, coords: tuple or list) -> None:
        self.pos: tuple = coords # Update pos coordinates.
    @property
    def color(self) -> tuple:
        return self._color
    @color.setter
    def color(self, value: tuple) -> None:
        self._color: tuple = value # Cached uniform value.
        self.sh.uniform_float("color", value)
class SH161a80971ecd45738c4a01ed9df44a0a():
    sh=SH.GPUSH161a80971ecd45738c4a01ed9df44a0a
    sh_type=ShType.POINT
    sh_geom=ShGeom.POINT
    def init_props(self):
        # Uniforms.
        self._col: tuple
        # Inputs.
        self._pos: tuple
        self.point_scale: float = 1.0
    # Shader Flags.
    use_uv: bool = False
    use_vertex_color: bool = False
    # Shader specific props.
    def get_inputs(self) -> Dict[str, Any]:
        {"pos":self.pos,}
    @property
    def pos(self) -> tuple:
        return self._pos
    @pos.setter
    def pos(self, value: tuple) -> None:
        self._pos: tuple = value # Cached input value.
    def set_coords(self, coords: tuple or list) -> None:
        self.pos: tuple = coords # Update pos coordinates.
    @property
    def col(self) -> tuple:
        return self._col
    @col.setter
    def col(self, value: tuple) -> None:
        self._col: tuple = value # Cached uniform value.
        self.sh.uniform_float("col", value)
class SHae407a18cf574aeeb1e7a63c37d7c77e():
    sh=SH.GPUSHae407a18cf574aeeb1e7a63c37d7c77e
    sh_type=ShType.IMG
    sh_geom=ShGeom.IMG
    def init_props(self):
        # Uniforms.
        # Inputs.
        self._pos: tuple
        self._col: tuple
        self._offset: int
    # Shader Flags.
    use_uv: bool = False
    use_vertex_color: bool = True
    # Shader specific props.
    def get_inputs(self) -> Dict[str, Any]:
        {"pos":self.pos,"col":self.col,"offset":self.offset,}
    @property
    def pos(self) -> tuple:
        return self._pos
    @pos.setter
    def pos(self, value: tuple) -> None:
        self._pos: tuple = value # Cached input value.
    def set_coords(self, coords: tuple or list) -> None:
        self.pos: tuple = coords # Update pos coordinates.
    @property
    def col(self) -> tuple:
        return self._col
    @col.setter
    def col(self, value: tuple) -> None:
        self._col: tuple = value # Cached input value.
    @property
    def offset(self) -> int:
        return self._offset
    @offset.setter
    def offset(self, value: int) -> None:
        self._offset: int = value # Cached input value.
