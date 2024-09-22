import os
import pygame
import OpenGL.GL as GL
import OpenGL.GLU as GLU
import numpy

from pygame import Vector3

from Shader import Shader
from Texture import Texture
from MatrixTools import *
from Camera import *
from Mesh import Mesh

dirPath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if "\\" in dirPath:
    dirPath = dirPath.replace("\\", "/")
NUM_POINT_LIGHTS = 2
WINDOW_SIZE = (800,600)


if __name__ == "__main__":
    # Make a openGL compatable window
    pygame.init()
    window = pygame.display.set_mode(WINDOW_SIZE,  pygame.OPENGL | pygame.DOUBLEBUF)
    clock = pygame.time.Clock()
    dt = 1.0
    run = True
    
    lightMesh = Mesh()
    cube = Mesh() # Mesh(f"{dirPath}/assets/test.obj")

    diffuseTexture = Texture(f"{dirPath}/assets/container.PNG", GL.GL_RGBA)
    specularTexture = Texture(f"{dirPath}/assets/container_specular.PNG", GL.GL_RGBA)

    camera = FreeCamera(startPos=Vector3(0.0, 0.0, 3.0))

    mainShader = Shader(f"{dirPath}/src/shaders/shader.vert", f"{dirPath}/src/shaders/shader.frag")
    mainShader.use()
    trans = numpy.eye(4)
    mainShader.setMat4("transform", trans)
    mainShader.setMat4("view", camera.matrix)
    proj = perspective(45, WINDOW_SIZE[0]/WINDOW_SIZE[1], 0.1, 100)
    mainShader.setMat4("projection", proj)
    mainShader.setInt("material.diffuse", 0)
    mainShader.setInt("material.specular", 1)
    mainShader.setFloat("material.shininess", 32.0)
    lightPositions = [Vector3(1.2,1.0,2.0), Vector3(-3,5,-8)]
    lightColors = [Vector3(1.0,1.0,1.0), Vector3(1.0,1.0,1.0)]
    lightFalloffs = [0.06, 0.06]
    for i in range(NUM_POINT_LIGHTS):
        mainShader.setVec3(f"lights[{i}].ambient", lightColors[i]*0.2)
        mainShader.setVec3(f"lights[{i}].diffuse", lightColors[i]*0.5)
        mainShader.setVec3(f"lights[{i}].specular", Vector3(1.0))
        mainShader.setVec3(f"lights[{i}].position", lightPositions[i])
        mainShader.setFloat(f"lights[{i}].falloff", lightFalloffs[i])
    mainShader.setVec3("viewPos", camera.position)

    lightShader = Shader(f"{dirPath}/src/shaders/light.vert", f"{dirPath}/src/shaders/light.frag")
    lightShader.use()
    lightShader.setMat4("view", camera.matrix)
    lightShader.setMat4("projection", proj)

    GL.glEnable(GL.GL_DEPTH_TEST)

    pitch = 0.0
    yaw = -90.0
    oldMousePos = pygame.mouse.get_pos()
    
    while run:
        pygame.display.set_caption(f"3D! | dt:{dt}, fps:{1000/dt}")

        camera.Update(dt)
        
        GL.glClearColor(0.1, 0.1, 0.1, 1.0)#0.2, 0.3, 0.3, 1.0
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        diffuseTexture.use(0)
        specularTexture.use(1)
        
        lightShader.use()
        lightShader.setMat4("view", camera.matrix)
        for i in range(NUM_POINT_LIGHTS):
            lightShader.setMat4("transform", translate(scale(numpy.eye(4), 0.2,0.2,0.2), lightPositions[i].x,lightPositions[i].y,lightPositions[i].z))
            lightShader.setVec3("lightColor", lightColors[i])
            lightMesh.render()
        
        mainShader.use()
        mainShader.setMat4("view", camera.matrix)
        mainShader.setVec3("viewPos", camera.position)
        cube.render()

        pygame.display.flip()
        dt = clock.tick(500)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                run = False
    pygame.quit()