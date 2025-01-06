from __future__ import absolute_import
import os
from imgui.integrations.pygame import PygameRenderer
import OpenGL.GL as GL
import imgui
import pygame
import sys

from pygame import Vector3
from Camera import FreeCamera
from Node import Node, RenderNode, LightNode

dirPath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if "\\" in dirPath:
    dirPath = dirPath.replace("\\", "/")

def main():
    pygame.init()
    size = (800, 600)

    pygame.display.set_mode(size, pygame.DOUBLEBUF | pygame.OPENGL)
    clock = pygame.time.Clock()
    dt = 1.0

    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 4)
    GL.glEnable(GL.GL_DEPTH_TEST)

    lights: list[LightNode] = []

    rootNode = Node()
    cubeNode = RenderNode()
    cubeNode.setParent(rootNode)
    cubeNode2 = RenderNode(diffusePath=f"{dirPath}/assets/container.PNG", specularPath=f"{dirPath}/assets/container_specular.PNG")
    cubeNode2.transform.position = Vector3(2,0,0)
    cubeNode2.transform.scale = Vector3(0.7)
    cubeNode2.setParent(rootNode)

    light=LightNode(lights)
    light.transform.position = Vector3(1.2,1.0,2.0)
    light.setParent(rootNode)

    GL.glBindBuffer(GL.GL_ARRAY_BUFFER,0)
    GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)
    GL.glBindVertexArray(0)
    GL.glUseProgram(0)
    GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
    GL.glActiveTexture(GL.GL_TEXTURE0)

    camera = FreeCamera(size, startPos=Vector3(0.0, 0.0, 3.0))

    imgui.create_context()
    impl = PygameRenderer()

    io = imgui.get_io()
    io.display_size = size

    show_custom_window = True

    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            impl.process_event(event)
        impl.process_inputs()

        GL.glClearColor(0.1, 0.1, 0.1, 1)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        camera.Update(dt)
        rootNode.updateWorldMatrix()
        rootNode.renderChildren(camera, lights)


        GL.glBindBuffer(GL.GL_ARRAY_BUFFER,0)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)
        GL.glUseProgram(0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
        GL.glActiveTexture(GL.GL_TEXTURE0)

        imgui.new_frame()

        if imgui.begin_main_menu_bar():
            if imgui.begin_menu("File", True):

                clicked_quit, selected_quit = imgui.menu_item(
                    "Quit", "Cmd+Q", False, True
                )

                if clicked_quit:
                    sys.exit(0)

                imgui.end_menu()
            imgui.end_main_menu_bar()

        imgui.show_test_window()

        if show_custom_window:
            is_expand, show_custom_window = imgui.begin("Custom window", True)
            if is_expand:
                imgui.text("Bar")
                imgui.text_colored("Eggs", 0.2, 1.0, 0.0)
            imgui.end()
        
        imgui.render()
        impl.render(imgui.get_draw_data())

        pygame.display.flip()
        dt = clock.tick(500)

if __name__ == "__main__":
    main()