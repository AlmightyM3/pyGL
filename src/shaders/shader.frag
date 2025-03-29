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

    mat4 lightSpaceMatrix;
    sampler2D shadowMap;
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


    vec4 posLightSpace = light.lightSpaceMatrix * vec4(fragPos, 1.0);
    vec3 projPosLightSpace = posLightSpace.xyz / posLightSpace.w  * 0.5 + 0.5;

    float bias = max(0.01 * (1.0 - dot(normal, light.direction)), 0.0005); 

    float currentDepth = projPosLightSpace.z;  

    // float closestDepth = texture(light.shadowMap, projPosLightSpace.xy).r;  
    // float shadow = currentDepth - bias > closestDepth  ? 1.0 : 0.0; 
    float shadow = 0.0;
    vec2 texelSize = 1.0 / textureSize(light.shadowMap, 0);
    for(int x = -1; x <= 1; ++x)
    {
        for(int y = -1; y <= 1; ++y)
        {
            float pcfDepth = texture(light.shadowMap, projPosLightSpace.xy + vec2(x, y) * texelSize).r; 
            shadow += currentDepth - bias > pcfDepth ? 1.0 : 0.0;        
        }    
    }
    shadow /= 9.0;

    if(projPosLightSpace.z > 1.0)  shadow = 0.0;
    //return texture(light.shadowMap, TexCoord).xyz;// projPosLightSpace;//vec3(currentDepth);//projPosLightSpace;//texture(light.shadowMap, TexCoord).xyz;

    return ambient + (1.0 - shadow) * (diffuse + specular);
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