import math
import ctypes
import os
import pygame
import OpenGL.GL as GL
import OpenGL.GLU as GLU
import numpy

from PIL import Image

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

    vertices = numpy.zeros(4, [("vertex_position", numpy.float32, 3), ("vertex_color", numpy.float32, 3), ("texture_cords", numpy.float32, 2)])
    vertices["vertex_position"] = [
        [ 0.5,  0.5, 0.0],
        [ 0.5, -0.5, 0.0],
        [-0.5, -0.5, 0.0],
        [-0.5,  0.5, 0.0]
    ]
    vertices["vertex_color"] = [
        [0.0, 0.0, 1.0],
        [0.0, 1.0, 0.0],
        [1.0, 0.0, 0.0],
        [0.8, 0.4, 0.6]
    ]
    vertices["texture_cords"] = [
        [1.0, 1.0],
        [1.0, 0.0],
        [0.0, 0.0],
        [0.0, 1.0]
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
    GL.glVertexAttribPointer(2, 2, GL.GL_FLOAT, GL.GL_FALSE, vertices.strides[0], ctypes.c_void_p(vertices.dtype["vertex_position"].itemsize+vertices.dtype["vertex_color"].itemsize))
    GL.glEnableVertexAttribArray(2)

    indices = numpy.array(
        [
            0, 1, 3,
            1, 2, 3
        ], numpy.uint32,
    )
    EBO = GL.glGenBuffers(1)
    GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, EBO)
    GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL.GL_STATIC_DRAW)

    texture = GL.glGenTextures(1)
    GL.glBindTexture(GL.GL_TEXTURE_2D, texture)
    
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_REPEAT)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_REPEAT)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR_MIPMAP_LINEAR)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)

    img = numpy.array(Image.open(f"{dirPath}/container.jpg"), numpy.int8)
    GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGB, numpy.size(img,0), numpy.size(img,1), 0, GL.GL_RGB, GL.GL_UNSIGNED_BYTE, img)
    GL.glGenerateMipmap(GL.GL_TEXTURE_2D)

    theShader = Shader(dirPath+"/shaders/shader.vert", dirPath+"/shaders/shader.frag")
    
    while run:
        pygame.display.set_caption(f"3D! | dt:{DT}, fps:{1000/DT}")

        GL.glClearColor(0.2, 0.3, 0.3, 1.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        theShader.use()
        GL.glBindTexture(GL.GL_TEXTURE_2D, texture)
        GL.glBindVertexArray(VAO)
        GL.glDrawElements(GL.GL_TRIANGLES, len(indices), GL.GL_UNSIGNED_INT, None)

        pygame.display.flip()
        DT = clock.tick(500)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                run = False
    pygame.quit()