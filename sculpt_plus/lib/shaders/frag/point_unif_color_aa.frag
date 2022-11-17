// VERT_ID POINT_2D_UNIF_SIZE_AA
// GEOM_ID POINT

uniform vec4 color;

in vec2 radii;
out vec4 fragColor;

void main()
{
  float alpha = mix(color.a, 1.0, smoothstep(radii[1], radii[0], length(gl_PointCoord - vec2(0.5))));

  if (alpha < 0.5) {
    discard;
  }

  // transparent outside of point
  // --- 0 ---
  //  smooth transition
  // --- 1 ---
  // pure point color
  // ...
  // dist = 0 at center of point

  fragColor.rgb = color.rgb;
  fragColor.a = alpha;
}
