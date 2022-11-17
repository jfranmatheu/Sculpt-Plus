// VERT_ID UV
// GEOM_ID IMG

//uniform vec4 color;
//uniform float scale;
//in vec2 uv;


in vec2 uv;
out vec4 fragColor;

uniform vec2 u_dimensions;
uniform vec3 u_color;
uniform float u_input_output;

const float u_radius = 4.5;
const float u_radius_in_out = u_radius * 3.0;
const float color_line_thickness = 4.0;
const float header_height = 36.0;

const vec3 header_color = vec3(0.125); //  vec3(.08); //
const vec3 header_color_gradient = vec3(0.1019);
const vec3 body_color   = vec3(0.157); // vec3(.11); // 

#  define cir_top_left (vec2(0, u_dimensions.y) + vec2(u_radius, -u_radius))
#  define cir_top_right (vec2(u_dimensions.x, u_dimensions.y) + vec2(-u_radius, -u_radius))
#  define cir_bot_left (u_input_output == 1 ? vec2(u_radius_in_out) : vec2(u_radius))
#  define cir_bot_right (u_input_output == 2 ? vec2(u_dimensions.x, 0) + vec2(-u_radius_in_out, u_radius_in_out) : vec2(u_dimensions.x, 0) + vec2(-u_radius, u_radius))

void main()
{
  vec2 coords = uv * u_dimensions;

  vec3 color = body_color; // vec3(uv.xy, 0.0); // position map

  //vec2 cir_top_left  = vec2(0, u_dimensions.y) + vec2(u_radius, -u_radius);
  //vec2 cir_top_right = vec2(u_dimensions.x, u_dimensions.y) + vec2(-u_radius, -u_radius);
  //vec2 cir_bot_left  = u_input_output == 1 ? vec2(u_radius_in_out) : vec2(u_radius);
  //vec2 cir_bot_right = u_input_output == 2 ? vec2(u_dimensions.x, 0) + vec2(-u_radius_in_out, u_radius_in_out) : vec2(u_dimensions.x, 0) + vec2(-u_radius, u_radius);

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
