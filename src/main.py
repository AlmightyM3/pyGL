import os
import pygame
import OpenGL.GL as GL
import OpenGL.GLU as GLU
import numpy

from pygame import Vector3

from Shader import Shader
from Camera import *
from Mesh import Mesh
from Node import *

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
    
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 4)
    print(f"OpenGL version {pygame.display.gl_get_attribute(pygame.GL_CONTEXT_MAJOR_VERSION)}.{pygame.display.gl_get_attribute(pygame.GL_CONTEXT_MINOR_VERSION)}")

    lightMesh = Mesh()

    rootNode = Node()

    cubeNode = RenderNode(meshPath=f"{dirPath}/assets/Suzanne.obj")
    cubeNode2 = RenderNode(diffusePath=f"{dirPath}/assets/container.PNG", specularPath=f"{dirPath}/assets/container_specular.PNG")
    cubeNode3 = RenderNode(diffusePath=f"{dirPath}/assets/container.PNG", specularPath=f"{dirPath}/assets/container_specular.PNG")
    cubeNode.transform.scale = Vector3(0.7)
    cubeNode.setParent(rootNode)
    cubeNode2.transform.position = Vector3(4,0,0)
    cubeNode2.transform.scale = Vector3(1.2)
    cubeNode2.setParent(cubeNode)
    cubeNode3.transform.position = Vector3(1.3,0,0)
    cubeNode3.transform.scale = Vector3(0.5)
    cubeNode3.setParent(cubeNode2)
    cubeNode.updateWorldMatrix()

    camera = FreeCamera(WINDOW_SIZE, startPos=Vector3(0.0, 0.0, 3.0))

    lightPositions = [Vector3(1.2,1.0,2.0), Vector3(-3,5,-8)]
    lightColors = [Vector3(1.0,1.0,1.0), Vector3(1.0,1.0,1.0)]
    lightFalloffs = [0.06, 0.06]

    lightShader = Shader(f"{dirPath}/src/shaders/light.vert", f"{dirPath}/src/shaders/light.frag")
    lightShader.use()
    lightShader.setMat4("view", camera.matrix)
    lightShader.setMat4("projection", camera.proj)

    GL.glEnable(GL.GL_DEPTH_TEST)
    
    while run:
        pygame.display.set_caption(f"3D! | dt:{dt}, fps:{1000/dt}")

        camera.Update(dt)
        
        GL.glClearColor(0.1, 0.1, 0.1, 1.0)#0.2, 0.3, 0.3, 1.0
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        cubeNode.transform.rotationAngle += 0.05 * dt
        cubeNode2.transform.rotationAngle += 0.1 * dt
        cubeNode3.transform.rotationAngle += 0.15 * dt
        
        rootNode.updateWorldMatrix()
        
        lightShader.use()
        lightShader.setMat4("view", camera.matrix)
        for i in range(NUM_POINT_LIGHTS):
            lightShader.setMat4("transform", translate(scale(numpy.eye(4), 0.2,0.2,0.2), lightPositions[i].x,lightPositions[i].y,lightPositions[i].z))
            lightShader.setVec3("lightColor", lightColors[i])
            lightMesh.render()
        
        rootNode.renderChildren(camera, NUM_POINT_LIGHTS,lightPositions,lightColors,lightFalloffs)

        pygame.display.flip()
        dt = clock.tick(500)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                run = False
    pygame.quit()