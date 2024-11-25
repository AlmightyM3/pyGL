#version 330 core

out vec4 FragColor;

in vec2 TexCoord;
in vec3 FragPos; 
in vec3 Normal; 

uniform float Roundness;
uniform vec3 color;

float sdRoundBox( vec2 p, vec2 b, float r ) // https://iquilezles.org/articles/distfunctions/
{
  vec2 q = abs(p) - b + r;
  return length(max(q,0.0)) + min(max(q.x,q.y),0.0) - r;
}

void main()
{
    if(sdRoundBox(TexCoord-0.5, vec2(0.5), Roundness) >0)
        discard;
    
    FragColor = vec4(color, 1.0);
}