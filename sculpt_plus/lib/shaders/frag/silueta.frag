// VERT_ID IMG
// GEOM_ID IMG

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
