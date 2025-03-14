#version 330 core

out vec4 FragColor;

struct Material {
    sampler2D diffuse;
    sampler2D specular;
    float shininess;
}; 
uniform Material material;

struct PointLight {
    vec3 position;
  
    vec3 ambient;
    vec3 diffuse;
    vec3 specular;

    float falloff;
};
#define NUM_POINT_LIGHTS 1
uniform PointLight[NUM_POINT_LIGHTS] pointLights; 

struct DirectionalLight {
    vec3 direction;
  
    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
};
#define NUM_DIRECTIONAL_LIGHTS 1
uniform DirectionalLight[NUM_DIRECTIONAL_LIGHTS] directionalLights; 

uniform vec3 viewPos;
in vec2 TexCoord;
in vec3 FragPos; 
in vec3 Normal; 

vec3 pointLight(PointLight light, vec3 normal, vec3 fragPos, vec3 viewDir){
    vec3 ambient = light.ambient * vec3(texture(material.diffuse, TexCoord));
    
    vec3 lightDir = normalize(light.position - fragPos); 
    float diffuseValue = max(dot(normal, lightDir), 0.0);
    vec3 diffuse = light.diffuse * diffuseValue * vec3(texture(material.diffuse, TexCoord));

    vec3 reflectDir = reflect(-lightDir, normal);  
    float specularValue = pow(max(dot(viewDir, reflectDir), 0.0), material.shininess);
    vec3 specular = light.specular * specularValue * vec3(texture(material.specular, TexCoord));  

    float distance    = length(light.position - FragPos);
    float attenuation = 1.0 / (1 + light.falloff*(distance * distance)); 

    return (ambient + diffuse + specular) * attenuation;
}

vec3 directionalLight(DirectionalLight light, vec3 normal, vec3 fragPos, vec3 viewDir){
    vec3 ambient = light.ambient * vec3(texture(material.diffuse, TexCoord));

    float diffuseValue = max(dot(normal, light.direction), 0.0);
    vec3 diffuse = light.diffuse * diffuseValue * vec3(texture(material.diffuse, TexCoord));

    vec3 reflectDir = reflect(-light.direction, normal);  
    float specularValue = pow(max(dot(viewDir, reflectDir), 0.0), material.shininess);
    vec3 specular = light.specular * specularValue * vec3(texture(material.specular, TexCoord));  

    return ambient + diffuse + specular;
}

void main()
{
    vec3 viewDir = normalize(viewPos - FragPos);
    vec3 norm = normalize(Normal);
    vec3 color = vec3(0.0);

    for(int i = 0; i < NUM_DIRECTIONAL_LIGHTS; i++)
        color += directionalLight(directionalLights[i], norm, FragPos, viewDir);
    for(int i = 0; i < NUM_POINT_LIGHTS; i++)
        color += pointLight(pointLights[i], norm, FragPos, viewDir);

    FragColor = vec4(color, 1.0);
}