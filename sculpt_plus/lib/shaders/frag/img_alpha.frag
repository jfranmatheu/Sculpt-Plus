// VERT_ID IMG
// GEOM_ID IMG

in vec2 texco_interp;
out vec4 fragColor;
uniform sampler2D image;
void main()
{
 vec4 texColor = texture(image, texco_interp);
 if(texColor.a < 0.05)
  discard;
 fragColor = texColor;
}
