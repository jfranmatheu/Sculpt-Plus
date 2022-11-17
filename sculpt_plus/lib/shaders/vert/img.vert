uniform mat4 ModelViewProjectionMatrix;
in vec2 texco;
in vec2 pos;
out vec2 texco_interp;
void main()
{
 gl_Position = ModelViewProjectionMatrix * vec4(pos, 1.0, 1.0);
 texco_interp = texco;
}
