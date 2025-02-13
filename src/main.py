from __future__ import absolute_import
import os
from imgui.integrations.pygame import PygameRenderer
import pygame
import imgui
import OpenGL.GL as GL
import OpenGL.GLU as GLU

from pygame import Vector3

from Camera import Camera, FreeCamera
from Node import Node, RenderNode, LightNode, UIPanelNode

dirPath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if "\\" in dirPath:
    dirPath = dirPath.replace("\\", "/")
WINDOW_SIZE = (1200,900)

def makeImGUIHappy():
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER,0)
    GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)
    GL.glBindVertexArray(0)
    GL.glUseProgram(0)
    GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
    GL.glActiveTexture(GL.GL_TEXTURE0)

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

    rootNode = Node("Root Node")
    inspectedNode:Node = rootNode

    cubeNode1 = RenderNode(name="Suzanne", meshPath=f"{dirPath}/assets/Suzanne.obj")
    cubeNode2 = RenderNode(name="Box 0", diffusePath=f"{dirPath}/assets/container.PNG", specularPath=f"{dirPath}/assets/container_specular.PNG")
    cubeNode3 = RenderNode(name="Box 1", diffusePath=f"{dirPath}/assets/container.PNG", specularPath=f"{dirPath}/assets/container_specular.PNG")
    cubeNode1.transform.scale = Vector3(0.7)
    cubeNode1.setParent(rootNode)
    cubeNode2.transform.position = Vector3(4,0,0)
    cubeNode2.transform.scale = Vector3(1.2)
    cubeNode2.setParent(cubeNode1)
    cubeNode3.transform.position = Vector3(1.3,0,0)
    cubeNode3.transform.scale = Vector3(0.5)
    cubeNode3.setParent(cubeNode2)

    teapot = RenderNode(name="Utah Teapot", meshPath=f"{dirPath}/assets/teapot.obj")
    teapot.transform.scale = Vector3(0.25)
    teapot.transform.position = Vector3(-4,0,-1)
    teapot.setParent(rootNode)

    uvTest = RenderNode(name="uvTest", diffusePath=f"{dirPath}/assets/UV_Grid.jpg")
    uvTest.transform.position = Vector3(5,0,0)
    uvTest.setParent(rootNode)
    uvTestTri = RenderNode(name="uvTest", meshPath=f"{dirPath}/assets/test.obj", diffusePath=f"{dirPath}/assets/UV_Grid.jpg")
    uvTestTri.transform.scale = Vector3(0.25)
    uvTestTri.transform.position = Vector3(0,1,0)
    uvTestTri.setParent(uvTest)

    light0=LightNode(lights, name="Light 0")
    light1=LightNode(lights, name="Light 1", isDirectional=True)
    light0.transform.position = Vector3(1.2,1.0,2.0)
    light1.transform.position = Vector3(-3,5,-8)
    light0.setParent(rootNode)
    light1.setParent(rootNode)

    camera = FreeCamera(WINDOW_SIZE, startPos=Vector3(0.0, 0.0, 3.0))

    shouldMakeCube = False

    makeImGUIHappy()

    imgui.create_context()
    impl = PygameRenderer()

    io = imgui.get_io()
    io.display_size = WINDOW_SIZE
    
    while run:
        pygame.display.set_caption(f"3D! | dt:{dt}, fps:{1000/dt}")

        camera.Update(dt)

        if shouldMakeCube:
            shouldMakeCube=False
            cube = RenderNode(name="unnamed cube")
            cube.setParent(rootNode)

        cubeNode1.transform.rotationAngle += 0.05 * dt
        cubeNode2.transform.rotationAngle += 0.1 * dt
        cubeNode3.transform.rotationAngle += 0.15 * dt

        rootNode.updateWorldMatrix()
        
        GL.glClearColor(0.1, 0.1, 0.1, 1.0)#0.2, 0.3, 0.3, 1.0
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        
        rootNode.renderChildren(camera, lights)

        makeImGUIHappy()

        imgui.new_frame()

        if imgui.begin_main_menu_bar():
            if imgui.begin_menu("File", True):
                clicked_quit, selected_quit = imgui.menu_item(
                    "Quit", "ESC", False, True
                )
                if clicked_quit:
                    run=False
                imgui.end_menu()
            if imgui.begin_menu("Edit", True):
                clicked_AddCube, selected_AddCube = imgui.menu_item(
                    "Add Cube", "", False, True
                )
                if clicked_AddCube:
                    shouldMakeCube=True
                imgui.end_menu()
            imgui.end_main_menu_bar()

        #imgui.show_test_window()
        imgui.begin("Node Tree")
        clickedNode = rootNode.treeUI()
        if clickedNode:
            inspectedNode = clickedNode
        imgui.end()
        
        if imgui.begin("Node Inspector"):
            inspectedNode.inspectorUI(rootNode)
        imgui.end()
        
        imgui.render()
        impl.render(imgui.get_draw_data())

        pygame.display.flip()
        dt = clock.tick(500)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                run = False
            impl.process_event(event)
        impl.process_inputs()
    pygame.quit()