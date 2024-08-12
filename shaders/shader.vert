#version 330 core

layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aNormal;
layout (location = 2) in vec2 aTexCord;

uniform mat4 transform;
uniform mat4 view;
uniform mat4 projection;

out vec2 TexCoord;
out vec3 FragPos;  
out vec3 Normal;

void main()
{
    gl_Position = projection * view * transform * vec4(aPos, 1.0f);
    TexCoord = aTexCord;
    FragPos = vec3(transform * vec4(aPos, 1.0));
    Normal = mat3(transpose(inverse(transform))) * aNormal; //The matrix should probably be calculated on the CPU beforehand
}