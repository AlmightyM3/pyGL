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

def translate(matrix, x, y, z):
    translation_matrix = numpy.array([
            [1.0, 0.0, 0.0, x  ],
            [0.0, 1.0, 0.0, y  ],
            [0.0, 0.0, 1.0, z  ],
            [0.0, 0.0, 0.0, 1.0],
        ], dtype=matrix.dtype).T
    return numpy.dot(matrix, translation_matrix)
def scale(matrix, x, y, z):
    translation_matrix = numpy.array([
            [x  , 0.0, 0.0, 0.0],
            [0.0, y  , 0.0, 0.0],
            [0.0, 0.0, z  , 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ], dtype=matrix.dtype).T
    return numpy.dot(matrix, translation_matrix)

# All further matrix functions are taken from the Pygame-ce glcube example. I hope to rewrite them myself once I actually understand how the math works, but for now this is what I have.
def rotate(matrix, angle, x, y, z):
    """
    Rotate a matrix around an axis.

    :param matrix: The matrix to rotate.
    :param angle: The angle to rotate by.
    :param x: x of axis to rotate around.
    :param y: y of axis to rotate around.
    :param z: z of axis to rotate around.

    :return: The rotated matrix
    """
    angle = math.pi * angle / 180
    c, s = math.cos(angle), math.sin(angle)
    n = math.sqrt(x * x + y * y + z * z)
    x, y, z = x / n, y / n, z / n
    cx, cy, cz = (1 - c) * x, (1 - c) * y, (1 - c) * z
    rotation_matrix = numpy.array(
        [
            [cx * x + c, cy * x - z * s, cz * x + y * s, 0],
            [cx * y + z * s, cy * y + c, cz * y - x * s, 0],
            [cx * z - y * s, cy * z + x * s, cz * z + c, 0],
            [0, 0, 0, 1],
        ],
        dtype=matrix.dtype,
    ).T
    matrix[...] = numpy.dot(matrix, rotation_matrix)
    return matrix

def frustum(left, right, bottom, top, znear, zfar):
    """
    Build a perspective matrix from the clipping planes, or camera 'frustrum'
    volume.

    :param left: left position of the near clipping plane.
    :param right: right position of the near clipping plane.
    :param bottom: bottom position of the near clipping plane.
    :param top: top position of the near clipping plane.
    :param znear: z depth of the near clipping plane.
    :param zfar: z depth of the far clipping plane.

    :return: A perspective matrix.
    """
    perspective_matrix = numpy.zeros((4, 4), dtype=numpy.float32)
    perspective_matrix[0, 0] = +2.0 * znear / (right - left)
    perspective_matrix[2, 0] = (right + left) / (right - left)
    perspective_matrix[1, 1] = +2.0 * znear / (top - bottom)
    perspective_matrix[3, 1] = (top + bottom) / (top - bottom)
    perspective_matrix[2, 2] = -(zfar + znear) / (zfar - znear)
    perspective_matrix[3, 2] = -2.0 * znear * zfar / (zfar - znear)
    perspective_matrix[2, 3] = -1.0
    return perspective_matrix


def perspective(fovy, aspect, znear, zfar):
    """
    Build a perspective matrix from field of view, aspect ratio and depth
    planes.

    :param fovy: the field of view angle in the y axis.
    :param aspect: aspect ratio of our view port.
    :param znear: z depth of the near clipping plane.
    :param zfar: z depth of the far clipping plane.

    :return: A perspective matrix.
    """
    h = math.tan(fovy / 360.0 * math.pi) * znear
    w = h * aspect
    return frustum(-w, w, -h, h, znear, zfar)


if __name__ == "__main__":
    # Make a openGL compatable window
    pygame.init()
    WINDOW_SIZE = (800,600)
    window = pygame.display.set_mode(WINDOW_SIZE,  pygame.OPENGL | pygame.DOUBLEBUF)
    clock = pygame.time.Clock()
    startTime = pygame.time.get_ticks()
    DT = 1.0
    run = True

    vertices = numpy.zeros(4, [("vertex_position", numpy.float32, 3), ("texture_cords", numpy.float32, 2)])
    vertices["vertex_position"] = [
        [ 0.5,  0.5, 0.0],
        [ 0.5, -0.5, 0.0],
        [-0.5, -0.5, 0.0],
        [-0.5,  0.5, 0.0]
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
    GL.glVertexAttribPointer(1, 2, GL.GL_FLOAT, GL.GL_FALSE, vertices.strides[0], ctypes.c_void_p(vertices.dtype["vertex_position"].itemsize))
    GL.glEnableVertexAttribArray(1)

    indices = numpy.array(
        [
            0, 1, 3,
            1, 2, 3
        ], numpy.uint32,
    )
    EBO = GL.glGenBuffers(1)
    GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, EBO)
    GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL.GL_STATIC_DRAW)

    texture1 = GL.glGenTextures(1)
    GL.glBindTexture(GL.GL_TEXTURE_2D, texture1)
    
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_REPEAT)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_REPEAT)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)

    img1 = numpy.flip(numpy.array(Image.open(f"{dirPath}/container.jpg"), numpy.int8),0)
    GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGB, numpy.size(img1,0), numpy.size(img1,1), 0, GL.GL_RGB, GL.GL_UNSIGNED_BYTE, img1)
    GL.glGenerateMipmap(GL.GL_TEXTURE_2D)

    texture2 = GL.glGenTextures(1)
    GL.glBindTexture(GL.GL_TEXTURE_2D, texture2)
    
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_REPEAT)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_REPEAT)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
    img2 = numpy.flip(numpy.array(Image.open(f"{dirPath}/awesomeface.png"), numpy.int8),0)
    GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, numpy.size(img2,0), numpy.size(img2,1), 0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, img2)
    GL.glGenerateMipmap(GL.GL_TEXTURE_2D)


    theShader = Shader(dirPath+"/shaders/shader.vert", dirPath+"/shaders/shader.frag")
    theShader.use()
    theShader.setInt("texture1", 0)
    theShader.setInt("texture2", 1)

    trans = numpy.eye(4)
    transformLoc = GL.glGetUniformLocation(theShader.ID, "transform")
    GL.glUniformMatrix4fv(transformLoc, 1, GL.GL_FALSE, trans)
    
    while run:
        pygame.display.set_caption(f"3D! | dt:{DT}, fps:{1000/DT}")

        GL.glClearColor(0.2, 0.3, 0.3, 1.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, texture1)
        GL.glActiveTexture(GL.GL_TEXTURE1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, texture2)

        theShader.use()
        trans = numpy.eye(4)
        trans = rotate(trans, (pygame.time.get_ticks()-startTime)*0.05%360,  0.0,0.0,1.0)
        trans = scale(trans, 0.75,0.75,0.75)
        trans = translate(trans, 0.5,-0.5,0.0)
        transformLoc = GL.glGetUniformLocation(theShader.ID, "transform")
        GL.glUniformMatrix4fv(transformLoc, 1, GL.GL_FALSE, trans)

        GL.glBindVertexArray(VAO)
        GL.glDrawElements(GL.GL_TRIANGLES, len(indices), GL.GL_UNSIGNED_INT, None)

        pygame.display.flip()
        DT = clock.tick(500)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                run = False
    pygame.quit()