#version 330 core

out vec4 FragColor;

in vec3 Color;
in vec2 TexCoord;

uniform sampler2D Texture;

void main()
{
    //FragColor = vec4(Color, 1.0f);
    FragColor = texture(Texture, TexCoord);
    //FragColor = vec4(TexCoord,  0.5f, 1.0f);
}