import math
import ctypes
import os
import pygame
import OpenGL.GL as GL
import OpenGL.GLU as GLU
import numpy

from PIL import Image
from pygame import Vector3

from Shader import Shader
from Texture import Texture

dirPath = os.path.dirname(os.path.abspath(__file__))
CAMERA_SPEED = 2.5
MOUSE_SENSITIVITY = 0.1

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

def genCamera(cameraPos, cameraTarget, cameraUp):
    cameraDirection = (cameraPos - cameraTarget).normalize()
    cameraRight = Vector3(0.0, 1.0, 0.0).cross(cameraDirection)
    #cameraUp = cameraDirection.cross(cameraRight)
    return numpy.array([
        [cameraRight.x, cameraRight.y, cameraRight.z, 0.0],
        [cameraUp.x,cameraUp.y,cameraUp.z, 0.0],
        [cameraDirection.x,cameraDirection.y,cameraDirection.z, 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ], numpy.float32).dot([
        [1.0, 0.0, 0.0, -cameraPos.x],
        [0.0, 1.0, 0.0, -cameraPos.y],
        [0.0, 0.0, 1.0, -cameraPos.z],
        [0.0, 0.0, 0.0, 1.0],
    ]).T

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
    WINDOW_SIZE = (800*2,600*2)
    window = pygame.display.set_mode(WINDOW_SIZE,  pygame.OPENGL | pygame.DOUBLEBUF)
    clock = pygame.time.Clock()
    startTime = pygame.time.get_ticks()
    DT = 1.0
    run = True

    vertices = numpy.zeros(24, [("vertex_position", numpy.float32, 3), ("texture_cords", numpy.float32, 2)]) # cube adaped from https://pastebin.com/XiCprv6S
    vertices["vertex_position"] = [
        [-0.5, -0.5, -0.5], # A0
        [ 0.5, -0.5, -0.5], # B1
        [ 0.5,  0.5, -0.5], # C2
        [-0.5,  0.5, -0.5], # D3
        [-0.5, -0.5,  0.5], # E4
        [ 0.5, -0.5,  0.5], # F5
        [ 0.5,  0.5,  0.5], # G6
        [-0.5,  0.5,  0.5], # H7

        [-0.5,  0.5, -0.5], # D8
        [-0.5, -0.5, -0.5], # A9
        [-0.5, -0.5,  0.5], # E10
        [-0.5,  0.5,  0.5], # H11
        [ 0.5, -0.5, -0.5], # B12
        [ 0.5,  0.5, -0.5], # C13
        [ 0.5,  0.5,  0.5], # G14
        [ 0.5, -0.5,  0.5], # F15

        [-0.5, -0.5, -0.5], # A16
        [ 0.5, -0.5, -0.5], # B17
        [ 0.5, -0.5,  0.5], # F18
        [-0.5, -0.5,  0.5], # E19
        [ 0.5,  0.5, -0.5], # C20
        [-0.5,  0.5, -0.5], # D21
        [-0.5,  0.5,  0.5], # H22
        [ 0.5,  0.5,  0.5], # G23
    ]
    vertices["texture_cords"] = [
        [0.0, 0.0], # A0
        [1.0, 0.0], # B1 
        [1.0, 1.0], # C2
        [0.0, 1.0], # D3
        [0.0, 0.0], # E4
        [1.0, 0.0], # F5
        [1.0, 1.0], # G6
        [0.0, 1.0], # H7
        [0.0, 0.0], # D8
        [1.0, 0.0], # A9
        [1.0, 1.0], # E10
        [0.0, 1.0], # H11
        [0.0, 0.0], # B12
        [1.0, 0.0], # C13
        [1.0, 1.0], # G14
        [0.0, 1.0], # F15
        [0.0, 0.0], # A16
        [1.0, 0.0], # B17
        [1.0, 1.0], # F18
        [0.0, 1.0], # E19
        [0.0, 0.0], # C20
        [1.0, 0.0], # D21
        [1.0, 1.0], # H22
        [0.0, 1.0], # G23
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

    indices = numpy.array([
        # front and back
        0, 3, 2,
        2, 1, 0,
        4, 5, 6,
        6, 7 ,4,
        # left and right
        11, 8, 9,
        9, 10, 11,
        12, 13, 14,
        14, 15, 12,
        # bottom and top
        16, 17, 18,
        18, 19, 16,
        20, 21, 22,
        22, 23, 20
    ], numpy.uint32)
    
    EBO = GL.glGenBuffers(1)
    GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, EBO)
    GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL.GL_STATIC_DRAW)

    containerTexture = Texture(f"{dirPath}/container.jpg", GL.GL_RGB)
    smileyTexture = Texture(f"{dirPath}/awesomeface.png", GL.GL_RGBA)

    theShader = Shader(dirPath+"/shaders/shader.vert", dirPath+"/shaders/shader.frag")
    theShader.use()
    theShader.setInt("texture1", 0)
    theShader.setInt("texture2", 1)
    trans = numpy.eye(4)
    theShader.setMat4("transform", trans)
    cameraPos = Vector3(0.0, 0.0, 3.0)
    cameraFront = Vector3(0.0, 0.0, -1.0)
    cameraUp = Vector3(0.0, 1.0,  0.0)
    view = genCamera(cameraPos, cameraPos+cameraFront, cameraUp)
    theShader.setMat4("view", view)
    proj = perspective(45, WINDOW_SIZE[0]/WINDOW_SIZE[1], 0.1, 100)
    theShader.setMat4("projection", proj)

    GL.glEnable(GL.GL_DEPTH_TEST)

    pitch = 0.0
    yaw = -90.0
    oldMousePos = pygame.mouse.get_pos()
    
    while run:
        pygame.display.set_caption(f"3D! | dt:{DT}, fps:{1000/DT}")

        inputs = pygame.key.get_pressed()
        if inputs[pygame.K_w] or inputs[pygame.K_UP]:
            cameraPos += cameraFront * CAMERA_SPEED * (DT/1000)
        if inputs[pygame.K_s] or inputs[pygame.K_DOWN]:
            cameraPos -= cameraFront * CAMERA_SPEED * (DT/1000)
        if inputs[pygame.K_a] or inputs[pygame.K_LEFT]:
            cameraPos -= cameraFront.cross(cameraUp).normalize() * CAMERA_SPEED * (DT/1000)
        if inputs[pygame.K_d] or inputs[pygame.K_RIGHT]:
            cameraPos += cameraFront.cross(cameraUp).normalize() * CAMERA_SPEED * (DT/1000)
        if inputs[pygame.K_q]:
            cameraPos += cameraUp * CAMERA_SPEED * (DT/1000)
        if inputs[pygame.K_e]:
            cameraPos -= cameraUp * CAMERA_SPEED * (DT/1000)
        
        mousePos = pygame.mouse.get_pos()
        offsetX = mousePos[0]-oldMousePos[0]
        offsetY = oldMousePos[1]-mousePos[1]
        oldMousePos = mousePos
        yaw += offsetX * MOUSE_SENSITIVITY
        pitch += offsetY * MOUSE_SENSITIVITY
        yaw %= 360
        if pitch > 89.0:
            pitch =  89.0
        if pitch < -89.0:
            pitch = -89.0
        direction = Vector3()
        direction.x = math.cos(math.radians(yaw)) * math.cos(math.radians(pitch))
        direction.y = math.sin(math.radians(pitch))
        direction.z = math.sin(math.radians(yaw)) * math.cos(math.radians(pitch))
        cameraFront = direction.normalize()
        
        GL.glClearColor(0.2, 0.3, 0.3, 1.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        containerTexture.use(0)
        smileyTexture.use(1)

        theShader.use()
        # trans = numpy.eye(4)
        # trans = rotate(trans, (pygame.time.get_ticks()-startTime)*0.05%360,  0.5,1.0,0.0)
        # theShader.setMat4("transform", trans)

        view = genCamera(cameraPos, cameraPos+cameraFront, cameraUp)
        theShader.setMat4("view", view)

        GL.glBindVertexArray(VAO)
        GL.glDrawElements(GL.GL_TRIANGLES, len(indices), GL.GL_UNSIGNED_INT, None)

        pygame.display.flip()
        DT = clock.tick(500)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                run = False
    pygame.quit()