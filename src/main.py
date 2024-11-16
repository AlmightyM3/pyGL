import os
import pygame
import OpenGL.GL as GL
import OpenGL.GLU as GLU

from pygame import Vector3

from Camera import Camera, FreeCamera
from Node import Node, RenderNode, LightNode

dirPath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if "\\" in dirPath:
    dirPath = dirPath.replace("\\", "/")
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

    lights: list[LightNode] = []

    rootNode = Node()

    cubeNode1 = RenderNode(meshPath=f"{dirPath}/assets/Suzanne.obj")
    cubeNode2 = RenderNode(diffusePath=f"{dirPath}/assets/container.PNG", specularPath=f"{dirPath}/assets/container_specular.PNG")
    cubeNode3 = RenderNode(diffusePath=f"{dirPath}/assets/container.PNG", specularPath=f"{dirPath}/assets/container_specular.PNG")
    cubeNode1.transform.scale = Vector3(0.7)
    cubeNode1.setParent(rootNode)
    cubeNode2.transform.position = Vector3(4,0,0)
    cubeNode2.transform.scale = Vector3(1.2)
    cubeNode2.setParent(cubeNode1)
    cubeNode3.transform.position = Vector3(1.3,0,0)
    cubeNode3.transform.scale = Vector3(0.5)
    cubeNode3.setParent(cubeNode2)

    light1=LightNode(lights)
    light2=LightNode(lights)
    light1.transform.position = Vector3(1.2,1.0,2.0)
    light2.transform.position = Vector3(-3,5,-8)
    light1.setParent(rootNode)
    light2.setParent(rootNode)

    camera = FreeCamera(WINDOW_SIZE, startPos=Vector3(0.0, 0.0, 3.0))

    GL.glEnable(GL.GL_DEPTH_TEST)
    
    while run:
        pygame.display.set_caption(f"3D! | dt:{dt}, fps:{1000/dt}")

        camera.Update(dt)

        cubeNode1.transform.rotationAngle += 0.05 * dt
        cubeNode2.transform.rotationAngle += 0.1 * dt
        cubeNode3.transform.rotationAngle += 0.15 * dt

        rootNode.updateWorldMatrix()
        
        GL.glClearColor(0.1, 0.1, 0.1, 1.0)#0.2, 0.3, 0.3, 1.0
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        
        rootNode.renderChildren(camera, lights)

        pygame.display.flip()
        dt = clock.tick(500)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                run = False
    pygame.quit()