// VERT_ID POINT
// GEOM_ID POINT

// This shader is based and modified from a shader by Inigo Quilez.
// Here you can find the license from the original source:
// *** The MIT License
// *** Copyright © 2019 Inigo Quilez
// *** Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions: The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software. THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

// uniform vec4 color;
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


void main(out vec4 fragColor, in vec2 fragCoord)
{
	//vec2 p = (2.0*fragCoord-iResolution.xy)/iResolution.y;
  //vec2 m = (2.0*iMouse.xy-iResolution.xy)/iResolution.y;
  vec2 cxy = 2.0 * gl_PointCoord - 1.0;
  // float r = dot(cxy, cxy);

  float n = 4.0;  // n, number of sides
  float a = 1.0;                 // angle factor
  float w = 3.0;        // angle divisor, between 2 and n
  
  // sdf
  float d = sdStar( cxy, 0.7, int(n), w );
  
  // colorize
  vec3 col = (d>0.0) ? vec3(0.0,0.0,0.0) : vec3(1.0,0.9,0.5);
  float opa = (d>0.0) ? 0.0 : 1.0;
	//col *= 1.05 - exp(-6.0*abs(d));
	//col *= 0.8 + 0.2*cos(110.0*d);
	col = mix( col, vec3(1.0), 1.0-smoothstep(0.0,0.015,abs(d)) );

	fragColor = vec4(col,opa);
}
