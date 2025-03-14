import numpy
import pygame
from pygame import Vector3
import math
from MatrixTools import *

class Camera:
    def __init__(self, startPos=Vector3(0.0, 0.0, 0.0), startFront=Vector3(0.0, 0.0,-1.0), startUp = Vector3(0.0, 1.0,  0.0)):
        self.position = startPos
        self.front = startFront
        self.worldUp = startUp
        self.matrix = self.genMatrix(self.position+self.front)
        self.proj = numpy.eye(4)
    
    def Update(self, dt):
        self.matrix = self.genMatrix(self.position+self.front)
    
    def genMatrix(self, target):
        return view(self.position, target, self.worldUp)

class orthographicCamera(Camera):
    def __init__(self,WINDOW_SIZE, startPos=Vector3(0.0, 0.0, 0.0), startFront=Vector3(0.0, 0.0,-1.0), startUp = Vector3(0.0, 1.0,  0.0), scale=5):
        super().__init__(startPos, startFront, startUp)
        self.proj = orthographic(scale, WINDOW_SIZE[0]/WINDOW_SIZE[1], 0.1, 100)

class perspectiveCamera(Camera):
    def __init__(self,WINDOW_SIZE, startPos=Vector3(0.0, 0.0, 0.0), startFront=Vector3(0.0, 0.0,-1.0), startUp = Vector3(0.0, 1.0,  0.0), fov=45):
        super().__init__(startPos, startFront, startUp)
        self.proj = perspective(fov, WINDOW_SIZE[0]/WINDOW_SIZE[1], 0.1, 100)

class FreeCamera(perspectiveCamera):
    def __init__(self,WINDOW_SIZE, startPos=Vector3(0.0, 0.0, 0.0), startFront=Vector3(0.0, 0.0,-1.0), startUp = Vector3(0.0, 1.0,  0.0), fov=45, speed = 2.75, sensitivity = 0.1):
        super().__init__(WINDOW_SIZE, startPos, startFront, startUp, fov)
        
        self.speed = speed
        self.sensitivity = sensitivity
        self.pitch = 0.0
        self.yaw = -90.0
        self.oldMousePos = pygame.mouse.get_pos()
    
    def Update(self, dt):
        inputs = pygame.key.get_pressed()
        if inputs[pygame.K_w] or inputs[pygame.K_UP]:
            self.position += self.front * self.speed * (dt/1000)
        if inputs[pygame.K_s] or inputs[pygame.K_DOWN]:
            self.position -= self.front * self.speed * (dt/1000)
        if inputs[pygame.K_a] or inputs[pygame.K_LEFT]:
            self.position -= self.front.cross(self.worldUp).normalize() * self.speed * (dt/1000)
        if inputs[pygame.K_d] or inputs[pygame.K_RIGHT]:
            self.position += self.front.cross(self.worldUp).normalize() * self.speed * (dt/1000)
        if inputs[pygame.K_q]:
            self.position += self.worldUp * self.speed * (dt/1000)
        if inputs[pygame.K_e]:
            self.position -= self.worldUp * self.speed * (dt/1000)
        
        mousePos = pygame.mouse.get_pos()
        offsetX = mousePos[0]-self.oldMousePos[0]
        offsetY = self.oldMousePos[1]-mousePos[1]
        self.oldMousePos = mousePos
        if pygame.mouse.get_pressed()[2]:
            self.yaw += offsetX * self.sensitivity
            self.pitch += offsetY * self.sensitivity
            self.yaw %= 360
            if self.pitch > 89.0:
                self.pitch =  89.0
            if self.pitch < -89.0:
                self.pitch = -89.0
            direction = Vector3()
            direction.x = math.cos(math.radians(self.yaw)) * math.cos(math.radians(self.pitch))
            direction.y = math.sin(math.radians(self.pitch))
            direction.z = math.sin(math.radians(self.yaw)) * math.cos(math.radians(self.pitch))
            self.front = direction.normalize()
        super().Update(dt)
