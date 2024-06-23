import math
import ctypes

import pygame

import OpenGL.GL as GL
import OpenGL.GLU as GLU

from numpy import array, dot, eye, zeros, float32, uint32

if __name__ == "__main__":
    # Make a openGL compatable window
    pygame.init()
    WINDOW_SIZE = (800,600)
    window = pygame.display.set_mode(WINDOW_SIZE,  pygame.OPENGL | pygame.DOUBLEBUF)
    clock = pygame.time.Clock()
    DT = 1.0
    run = True

    vertices = zeros(4, [("vertex_position", float32, 3), ("vertex_color", float32, 3)])
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
            0, 1, 3,
            1, 2, 3
        ],
        dtype=uint32,
    )
    EBO = GL.glGenBuffers(1)
    GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, EBO)
    GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL.GL_STATIC_DRAW)


    vertexShaderSource = '''#version 330 core
    layout (location = 0) in vec3 aPos;
    layout (location = 1) in vec3 aColor;
    out vec3 Color;

    void main()
    {
        gl_Position = vec4(aPos.x, aPos.y, aPos.z, 1.0);
        Color = aColor;
    }'''
    vertexShader = GL.glCreateShader(GL.GL_VERTEX_SHADER)
    GL.glShaderSource(vertexShader, vertexShaderSource)
    GL.glCompileShader(vertexShader)

    log = GL.glGetShaderInfoLog(vertexShader)
    if isinstance(log, bytes):
        log = log.decode()
    for line in log.split("\n"):
        print(line)

    fragmentShaderSource = '''#version 330 core
    in vec3 Color;
    out vec4 FragColor;
    void main()
    {
        FragColor = vec4(Color, 1.0f);
    } '''
    fragmentShader = GL.glCreateShader(GL.GL_FRAGMENT_SHADER)
    GL.glShaderSource(fragmentShader, fragmentShaderSource)
    GL.glCompileShader(fragmentShader)
    
    log = GL.glGetShaderInfoLog(fragmentShader)
    if isinstance(log, bytes):
        log = log.decode()
    for line in log.split("\n"):
        print(line)

    shaderProgram = GL.glCreateProgram()
    GL.glAttachShader(shaderProgram, vertexShader)
    GL.glAttachShader(shaderProgram, fragmentShader)
    GL.glLinkProgram(shaderProgram)
    GL.glUseProgram(shaderProgram)
    
    GL.glDeleteShader(vertexShader)
    GL.glDeleteShader(fragmentShader)
    

    while run:
        pygame.display.set_caption(f"3D! | dt:{DT}, fps:{1000/DT}")

        GL.glClearColor(0.2, 0.3, 0.3, 1.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        GL.glUseProgram(shaderProgram)
        GL.glBindVertexArray(VAO)
        GL.glDrawElements(GL.GL_TRIANGLES, len(indices), GL.GL_UNSIGNED_INT, None)

        pygame.display.flip()
        DT = clock.tick(500)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                run = False
    pygame.quit()