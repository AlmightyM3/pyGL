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
from ModelLoader import OBJ
from MatrixTools import *

CAMERA_SPEED = 2.5
MOUSE_SENSITIVITY = 0.1
NUM_POINT_LIGHTS = 2


if __name__ == "__main__":
    # Make a openGL compatable window
    pygame.init()
    WINDOW_SIZE = (800,600)
    window = pygame.display.set_mode(WINDOW_SIZE,  pygame.OPENGL | pygame.DOUBLEBUF)
    clock = pygame.time.Clock()
    DT = 1.0
    run = True
    #test = OBJ("Suzanne.obj")

    vertices = numpy.array([
        #positions          normals           texture coords
         0.5, -0.5, -0.5,   0.0,  0.0, -1.0,  1.0, 0.0,
        -0.5, -0.5, -0.5,   0.0,  0.0, -1.0,  0.0, 0.0,
         0.5,  0.5, -0.5,   0.0,  0.0, -1.0,  1.0, 1.0,
        -0.5,  0.5, -0.5,   0.0,  0.0, -1.0,  0.0, 1.0,
 
        -0.5, -0.5,  0.5,   0.0,  0.0, 1.0,   0.0, 0.0,
         0.5, -0.5,  0.5,   0.0,  0.0, 1.0,   1.0, 0.0,
         0.5,  0.5,  0.5,   0.0,  0.0, 1.0,   1.0, 1.0,
        -0.5,  0.5,  0.5,   0.0,  0.0, 1.0,   0.0, 1.0,
 
        -0.5,  0.5,  0.5,  -1.0,  0.0,  0.0,  1.0, 0.0,
        -0.5,  0.5, -0.5,  -1.0,  0.0,  0.0,  1.0, 1.0,
        -0.5, -0.5, -0.5,  -1.0,  0.0,  0.0,  0.0, 1.0,
        -0.5, -0.5,  0.5,  -1.0,  0.0,  0.0,  0.0, 0.0,
 
         0.5,  0.5,  0.5,   1.0,  0.0,  0.0,  1.0, 0.0,
         0.5,  0.5, -0.5,   1.0,  0.0,  0.0,  1.0, 1.0,
         0.5, -0.5, -0.5,   1.0,  0.0,  0.0,  0.0, 1.0,
         0.5, -0.5,  0.5,   1.0,  0.0,  0.0,  0.0, 0.0,
 
        -0.5, -0.5, -0.5,   0.0, -1.0,  0.0,  0.0, 1.0,
         0.5, -0.5, -0.5,   0.0, -1.0,  0.0,  1.0, 1.0,
         0.5, -0.5,  0.5,   0.0, -1.0,  0.0,  1.0, 0.0,
        -0.5, -0.5,  0.5,   0.0, -1.0,  0.0,  0.0, 0.0,
 
        -0.5,  0.5, -0.5,   0.0,  1.0,  0.0,  0.0, 1.0,
         0.5,  0.5, -0.5,   0.0,  1.0,  0.0,  1.0, 1.0,
         0.5,  0.5,  0.5,   0.0,  1.0,  0.0,  1.0, 0.0,
        -0.5,  0.5,  0.5,   0.0,  1.0,  0.0,  0.0, 0.0,
    ], numpy.float32)
    #vertices = test.vertices
    
    VBO = GL.glGenBuffers(1)
    VAO = GL.glGenVertexArrays(1) 
    GL.glBindVertexArray(VAO)

    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, VBO)
    GL.glBufferData(GL.GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL.GL_STATIC_DRAW)

    GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 32, ctypes.c_void_p(0)) # 32 = 8*(32/8) 
    GL.glEnableVertexAttribArray(0)
    GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, GL.GL_FALSE, 32, ctypes.c_void_p(3*vertices.itemsize))#vertices.dtype["vertex_position"].itemsize
    GL.glEnableVertexAttribArray(1)
    GL.glVertexAttribPointer(2, 2, GL.GL_FLOAT, GL.GL_FALSE, 32, ctypes.c_void_p(6*vertices.itemsize))#vertices.dtype["vertex_position"].itemsize+vertices.dtype["vertex_normal"].itemsize
    GL.glEnableVertexAttribArray(2)

    indices = numpy.array([
        0, 1, 2,  1, 3, 2, 
        4, 5, 6,  6, 7, 4, 
        8, 9, 10, 10,11,8, 
        14,13,12, 12,15,14,
        16,17,18, 18,19,16,
        22,21,20, 20,23,22
    ], numpy.uint32)
    #indices = test.indices
    
    EBO = GL.glGenBuffers(1)
    GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, EBO)
    GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL.GL_STATIC_DRAW)

    GL.glEnable(GL.GL_CULL_FACE)

    diffuseTexture = Texture("container2.PNG", GL.GL_RGBA)
    specularTexture = Texture("container2_specular.PNG", GL.GL_RGBA)

    mainShader = Shader("shaders/shader.vert", "shaders/shader.frag")
    mainShader.use()
    trans = numpy.eye(4)
    mainShader.setMat4("transform", trans)
    cameraPos = Vector3(0.0, 0.0, 3.0)
    cameraFront = Vector3(0.0, 0.0, -1.0)
    cameraUp = Vector3(0.0, 1.0,  0.0)
    view = genCamera(cameraPos, cameraPos+cameraFront)
    mainShader.setMat4("view", view)
    proj = perspective(45, WINDOW_SIZE[0]/WINDOW_SIZE[1], 0.1, 100)
    mainShader.setMat4("projection", proj)
    mainShader.setInt("material.diffuse", 0)
    mainShader.setInt("material.specular", 1)
    mainShader.setFloat("material.shininess", 32.0)
    lightPositions = [Vector3(1.2,1.0,2.0), Vector3(-3,5,-8)]
    lightColors = [Vector3(1.0,1.0,1.0), Vector3(1.0,1.0,1.0)]
    lightFalloffs = [0.06, 0.06]
    for i in range(NUM_POINT_LIGHTS):
        mainShader.setVec3(f"lights[{i}].ambient", lightColors[i]*0.2)
        mainShader.setVec3(f"lights[{i}].diffuse", lightColors[i]*0.5)
        mainShader.setVec3(f"lights[{i}].specular", Vector3(1.0))
        mainShader.setVec3(f"lights[{i}].position", lightPositions[i])
        mainShader.setFloat(f"lights[{i}].falloff", lightFalloffs[i])
    mainShader.setVec3("viewPos", cameraPos)

    lightShader = Shader("shaders/light.vert", "shaders/light.frag")
    lightShader.use()
    lightShader.setMat4("view", view)
    lightShader.setMat4("projection", proj)

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
        if pygame.mouse.get_pressed()[0]:
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
        
        GL.glClearColor(0.1, 0.1, 0.1, 1.0)#0.2, 0.3, 0.3, 1.0
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        diffuseTexture.use(0)
        specularTexture.use(1)

        view = genCamera(cameraPos, cameraPos+cameraFront)
        
        lightShader.use()
        lightShader.setMat4("view", view)
        for i in range(NUM_POINT_LIGHTS):
            lightShader.setMat4("transform", translate(scale(numpy.eye(4), 0.2,0.2,0.2), lightPositions[i].x,lightPositions[i].y,lightPositions[i].z))
            lightShader.setVec3("lightColor", lightColors[i])
            GL.glBindVertexArray(VAO)
            GL.glDrawElements(GL.GL_TRIANGLES, len(indices), GL.GL_UNSIGNED_INT, None)
        
        mainShader.use()
        mainShader.setMat4("view", view)
        mainShader.setVec3("viewPos", cameraPos)
        GL.glBindVertexArray(VAO)
        GL.glDrawElements(GL.GL_TRIANGLES, len(indices), GL.GL_UNSIGNED_INT, None)

        pygame.display.flip()
        DT = clock.tick(500)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                run = False
    pygame.quit()