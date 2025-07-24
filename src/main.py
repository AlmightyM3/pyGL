from __future__ import absolute_import
import os
import pygame
import OpenGL.GL as GL
import OpenGL.GLU as GLU

from pygame import Vector3

from Camera import Camera, FreeCamera
from Node import Node, RenderNode, LightNode
from Mesh import Mesh
from Shader import Shader
from Texture import Texture
from Skybox import Skybox
from ImguiUI import GUI

dirPath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if "\\" in dirPath:
    dirPath = dirPath.replace("\\", "/")
WINDOW_SIZE = (1200,900)

if __name__ == "__main__":
    # Make a openGL compatable window
    pygame.init()
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 4)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 1)

    window = pygame.display.set_mode(WINDOW_SIZE,  pygame.OPENGL | pygame.DOUBLEBUF)
    clock = pygame.time.Clock()
    dt = 1.0
    run = True
    
    print(f"OpenGL version {pygame.display.gl_get_attribute(pygame.GL_CONTEXT_MAJOR_VERSION)}.{pygame.display.gl_get_attribute(pygame.GL_CONTEXT_MINOR_VERSION)}")

    skyboxShader = Shader(f"{dirPath}/src/shaders/skybox.vert", f"{dirPath}/src/shaders/skybox.frag")
    skybox = Skybox(f"{dirPath}/assets/skybox/",skyboxShader)

    lights: list[LightNode] = []
    litShader = Shader(f"{dirPath}/src/shaders/shader.vert", f"{dirPath}/src/shaders/shader.frag")
    
    cubeMesh = Mesh("CUBE")
    suzanneMesh = Mesh(f"{dirPath}/assets/Suzanne.obj")
    testMesh = Mesh(f"{dirPath}/assets/test.obj")
    teapotMesh = Mesh(f"{dirPath}/assets/teapot.obj")
    
    blankTex = Texture(f"{dirPath}/assets/blank.PNG")
    UVTex = Texture(f"{dirPath}/assets/UV_Grid.jpg")
    containerTex = Texture(f"{dirPath}/assets/container.PNG")
    containerSpecularTex = Texture(f"{dirPath}/assets/container_specular.PNG")

    rootNode = Node("Root Node")

    cubeNode1 = RenderNode(suzanneMesh,litShader,blankTex,blankTex, "Suzanne")
    cubeNode2 = RenderNode(cubeMesh,litShader,containerTex,containerSpecularTex, "Box 0")
    cubeNode3 = RenderNode(cubeMesh,litShader,containerTex,containerSpecularTex, "Box 1")
    cubeNode1.transform.scale = Vector3(0.7)
    cubeNode1.setParent(rootNode)
    cubeNode2.transform.position = Vector3(4,0,0)
    cubeNode2.transform.scale = Vector3(1.2)
    cubeNode2.setParent(cubeNode1)
    cubeNode3.transform.position = Vector3(1.3,0,0)
    cubeNode3.transform.scale = Vector3(0.5)
    cubeNode3.setParent(cubeNode2)

    teapot = RenderNode(teapotMesh,litShader,blankTex,blankTex, "Utah Teapot")
    teapot.transform.scale = Vector3(0.25)
    teapot.transform.position = Vector3(-4,0,-1)
    teapot.setParent(rootNode)

    uvTest = RenderNode(cubeMesh,litShader,UVTex,blankTex, "uvTest")
    uvTest.transform.position = Vector3(5,0,0)
    uvTest.setParent(rootNode)
    uvTestTri = RenderNode(testMesh,litShader,UVTex,blankTex, "uvTest")
    uvTestTri.transform.scale = Vector3(0.25)
    uvTestTri.transform.position = Vector3(0,1,0)
    uvTestTri.setParent(uvTest)

    shadowTestZone = Node("Shadow Test Zone")
    shadowTestZone.transform.position = Vector3(0,0,8)
    shadowTestZone.transform.scale = Vector3(0.5)
    shadowTestZone.setParent(rootNode)
    sGround = RenderNode(cubeMesh,litShader,blankTex,blankTex, "Ground")
    sGround.transform.scale = Vector3(10,0.5,10)
    sGround.transform.position = Vector3(0,-0.75,0)
    sGround.setParent(shadowTestZone)
    sBox0 = RenderNode(cubeMesh,litShader,blankTex,blankTex, "Box 0")
    sBox0.transform.position = Vector3(0,0,0)
    sBox0.setParent(shadowTestZone)
    sBox1 = RenderNode(cubeMesh,litShader,blankTex,blankTex, "Box 1")
    sBox1.transform.position = Vector3(1,2,3)
    sBox1.setParent(shadowTestZone)
    sBox2 = RenderNode(cubeMesh,litShader,blankTex,blankTex, "Box 2")
    sBox2.transform.position = Vector3(-3,0.5,2)
    sBox2.setParent(shadowTestZone)
    sBox3 = RenderNode(cubeMesh,litShader,blankTex,blankTex, "Box 3")
    sBox3.transform.position = Vector3(2,0,-1)
    sBox3.setParent(shadowTestZone)
    sBox4 = RenderNode(cubeMesh,litShader,blankTex,blankTex, "Box 4")
    sBox4.transform.position = Vector3(3,1,0)
    sBox4.setParent(shadowTestZone)
    sBox5 = RenderNode(cubeMesh,litShader,blankTex,blankTex, "Box 5")
    sBox5.transform.position = Vector3(-1,2,-3)
    sBox5.setParent(shadowTestZone)

    light0=LightNode(lights, name="Light 0")
    light1=LightNode(lights, name="Light 1", isDirectional=True)
    light0.transform.position = Vector3(1.2,1.0,2.0)
    light1.transform.position = Vector3(-1.5,2.5,-4)
    light0.setParent(rootNode)
    light1.setParent(rootNode)

    camera = FreeCamera(WINDOW_SIZE, startPos=Vector3(0.0, 0.0, 3.0))

    depthMapFBO = GL.glGenFramebuffers(1)
    GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, depthMapFBO)
    GL.glDrawBuffer(GL.GL_NONE)
    GL.glReadBuffer(GL.GL_NONE)
    GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)

    directionalDepthShader = Shader(f"{dirPath}/src/shaders/shadowDepthDirectional.vert", f"{dirPath}/src/shaders/shadowDepthDirectional.frag")
    pointDepthShader = Shader(f"{dirPath}/src/shaders/shadowDepthPoint.vert", f"{dirPath}/src/shaders/shadowDepthPoint.frag", f"{dirPath}/src/shaders/shadowDepthPoint.geom")

    gui = GUI(WINDOW_SIZE, rootNode)
    
    while run:
        pygame.display.set_caption(f"3D! | dt: {dt}, fps: {clock.get_fps():.6}")

        camera.Update(dt)

        if gui.shouldMakeCube:
            gui.shouldMakeCube=False
            cube = RenderNode(cubeMesh,litShader,blankTex,blankTex)
            cube.setParent(rootNode)

        cubeNode1.transform.rotationAngle += 0.05 * dt
        cubeNode2.transform.rotationAngle += 0.1 * dt
        cubeNode3.transform.rotationAngle += 0.15 * dt

        rootNode.updateWorldMatrix()
        
        for light in lights:
            light.renderDepthMap(depthMapFBO,directionalDepthShader if light.isDirectional else pointDepthShader,rootNode)
        
        GL.glViewport(0, 0, WINDOW_SIZE[0], WINDOW_SIZE[1])
        GL.glClearColor(0.1, 0.1, 0.1, 1.0)#0.2, 0.3, 0.3, 1.0
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        
        rootNode.renderChildren(camera, lights)

        skybox.render(camera)

        gui.draw(rootNode)

        pygame.display.flip()
        dt = clock.tick(500)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                run = False
            gui.processEvent(event)
        gui.processInputs()
    pygame.quit()