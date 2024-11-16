import OpenGL.GL as GL
from pygame import Vector3
from MatrixTools import *
from Mesh import Mesh
from Shader import Shader
from Texture import Texture

import os
dirPath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if "\\" in dirPath:
    dirPath = dirPath.replace("\\", "/")

class Transform:
    def __init__(self):
        self.position = Vector3()
        self.rotationAxis = Vector3(0,1,0)
        self.rotationAngle = 0
        self.scale = Vector3(1)

        self.updateLocalMatrix()
    
    def updateLocalMatrix(self):
        self.localMatrix =  translate(rotate(scale(numpy.eye(4), self.scale.x, self.scale.y, self.scale.z), self.rotationAngle, self.rotationAxis.x, self.rotationAxis.y, self.rotationAxis.z), self.position.x, self.position.y, self.position.z)

class Node:
    def __init__(self):
        self.transform = Transform()
        self.children = []
        self.parent: Node = None

        self.updateWorldMatrix()
    
    def setParent(self, newParent):
        if self.parent: 
            try:
                self.parent.children.remove(self)
            except ValueError:
                pass
        
        if newParent:
            newParent.children.append(self)
        self.parent = newParent
    
    def updateWorldMatrix(self):
        if not self.parent == None:
            self.worldMatrix = numpy.dot(self.transform.localMatrix, self.parent.worldMatrix)
        else:
            self.worldMatrix = self.transform.localMatrix

        for child in self.children:
            child.updateWorldMatrix()

class RenderNode(Node):
    def __init__(self):
        super().__init__()
        self.mesh = Mesh()

        self.diffuseTexture = Texture(f"{dirPath}/assets/container.PNG", GL.GL_RGBA)
        self.specularTexture = Texture(f"{dirPath}/assets/container_specular.PNG", GL.GL_RGBA)

        self.shader = Shader(f"{dirPath}/src/shaders/shader.vert", f"{dirPath}/src/shaders/shader.frag")
        self.shader.use()
        self.shader.setInt("material.diffuse", 0)
        self.shader.setInt("material.specular", 1)
        self.shader.setFloat("material.shininess", 32.0)
    
    def render(self, camera, numLights,lightPositions,lightColors,lightFalloffs):
        self.shader.use()
        
        self.shader.setMat4("view", camera.matrix)
        self.shader.setVec3("viewPos", camera.position)
        self.shader.setMat4("projection", camera.proj)
        self.shader.setMat4("transform", self.worldMatrix)

        for i in range(numLights):
            self.shader.setVec3(f"lights[{i}].ambient", lightColors[i]*0.2)
            self.shader.setVec3(f"lights[{i}].diffuse", lightColors[i]*0.5)
            self.shader.setVec3(f"lights[{i}].specular", Vector3(1.0))
            self.shader.setVec3(f"lights[{i}].position", lightPositions[i])
            self.shader.setFloat(f"lights[{i}].falloff", lightFalloffs[i])

        self.diffuseTexture.use(0)
        self.specularTexture.use(1)
        
        self.mesh.render()