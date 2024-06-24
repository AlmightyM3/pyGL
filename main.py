import math
import ctypes
import os

import pygame

import OpenGL.GL as GL
import OpenGL.GLU as GLU

from numpy import array, dot, eye, zeros, float32, uint32

from Shader import Shader

dirPath = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    # Make a openGL compatable window
    pygame.init()
    WINDOW_SIZE = (800,600)
    window = pygame.display.set_mode(WINDOW_SIZE,  pygame.OPENGL | pygame.DOUBLEBUF)
    clock = pygame.time.Clock()
    DT = 1.0
    run = True

    vertices = zeros(3, [("vertex_position", float32, 3), ("vertex_color", float32, 3)])
    vertices["vertex_position"] = [
        [ 0.0,  0.5, 0.0],
        [ 0.5, -0.5, 0.0],
        [-0.5, -0.5, 0.0]
    ]
    vertices["vertex_color"] = [
        [0.0, 0.0, 1.0],
        [0.0, 1.0, 0.0],
        [1.0, 0.0, 0.0]
    ]
    
    VBO = GL.glGenBuffers(1)

    VAO = GL.glGenVertexArrays(1) 
    GL.glBindVertexArray(VAO)

    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, VBO)
    GL.glBufferData(GL.GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL.GL_STATIC_DRAW)

    GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, vertices.strides[0], ctypes.c_void_p(0))
    GL.glEnableVertexAttribArray(0)
    GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, GL.GL_FALSE, vertices.strides[0], ctypes.c_void_p(vertices.dtype["vertex_position"].itemsize))
    GL.glEnableVertexAttribArray(1)

    indices = array(
        [
            0, 1, 2
        ],
        dtype=uint32,
    )
    EBO = GL.glGenBuffers(1)
    GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, EBO)
    GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL.GL_STATIC_DRAW)


    theShader = Shader(dirPath+"/shaders/shader.vert", dirPath+"/shaders/shader.frag")
    
    while run:
        pygame.display.set_caption(f"3D! | dt:{DT}, fps:{1000/DT}")

        GL.glClearColor(0.2, 0.3, 0.3, 1.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        theShader.use()
        theShader.setFloat("xOffset", 0.4)
        GL.glBindVertexArray(VAO)
        GL.glDrawElements(GL.GL_TRIANGLES, len(indices), GL.GL_UNSIGNED_INT, None)

        pygame.display.flip()
        DT = clock.tick(500)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                run = False
    pygame.quit()