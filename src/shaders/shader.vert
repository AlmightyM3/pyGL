#version 330 core

layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aNormal;
layout (location = 2) in vec2 aTexCord;
layout (location = 3) in vec3 aTangent;

uniform mat4 transform;
uniform mat4 view;
uniform mat4 projection;

out vec2 TexCoord;
out vec3 FragPos;  
out mat3 TBN;

void main()
{
    gl_Position = projection * view * transform * vec4(aPos, 1.0f);
    TexCoord = aTexCord;
    FragPos = vec3(transform * vec4(aPos, 1.0));

    vec3 normal = normalize(vec3(transform * vec4(aNormal, 0.0)));
    vec3 tangent = normalize(vec3(transform * vec4(aTangent, 0.0)));
    vec3 bitangent  = cross(normal, tangent);
    TBN = mat3(tangent, bitangent, normal);
}