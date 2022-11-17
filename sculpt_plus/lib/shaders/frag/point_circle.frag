// VERT_ID POINT
// GEOM_ID POINT

#ifdef GL_ES
precision mediump float;
#endif

uniform vec4 col;
out vec4 fragColor;

float roundedFrame (float d, float thickness)
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
