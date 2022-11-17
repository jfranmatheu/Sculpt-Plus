// VERT_ID IMG
// GEOM_ID IMG

in vec2 texco_interp;
out vec4 fragColor;
uniform sampler2D image;
void main()
{
 fragColor = texture(image, texco_interp);
}
