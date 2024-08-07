#version 330 core

layout (location = 0) in vec3 aPos;
layout (location = 1) in vec2 aTexCord;

uniform mat4 transform;
uniform mat4 camera;
uniform mat4 projection;

out vec3 Color;
out vec2 TexCoord;

void main()
{
    gl_Position = projection * camera * transform * vec4(aPos, 1.0f);
    TexCoord = aTexCord;
}