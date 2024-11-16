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
        self._position = Vector3()
        self._rotationAxis = Vector3(0,1,0)
        self._rotationAngle = 0
        self._scale = Vector3(1)

        self.changed = False

        self.updateLocalMatrix()

    @property
    def position(self):
        return self._position
    @position.setter
    def position(self, new_position):
        self._position = new_position
        self.changed = True

    @property
    def rotationAxis(self):
        return self._rotationAxis
    @rotationAxis.setter
    def rotationAxis(self, new_rotationAxis):
        self._rotationAxis = new_rotationAxis
        self.changed = True

    @property
    def rotationAngle(self):
        return self._rotationAngle
    @rotationAngle.setter
    def rotationAngle(self, new_rotationAngle):
        self._rotationAngle = new_rotationAngle
        self.changed = True

    @property
    def scale(self):
        return self._scale
    @scale.setter
    def scale(self, new_scale):
        self._scale = new_scale
        self.changed = True
    
    def updateLocalMatrix(self):
        self.localMatrix =  translate(rotate(scale(numpy.eye(4), self._scale.x, self._scale.y, self._scale.z), self._rotationAngle, self._rotationAxis.x, self._rotationAxis.y, self._rotationAxis.z), self._position.x, self._position.y, self._position.z)
        self.changed = False

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
        if self.transform.changed:
            self.transform.updateLocalMatrix()
        
        if not self.parent == None:
            self.worldMatrix = numpy.dot(self.transform.localMatrix, self.parent.worldMatrix)
        else:
            self.worldMatrix = self.transform.localMatrix

        for child in self.children:
            child.updateWorldMatrix()
    
    def renderChildren(self, camera, numLights,lightPositions,lightColors,lightFalloffs):
        for child in self.children:
            child.renderChildren(camera, numLights,lightPositions,lightColors,lightFalloffs)

class RenderNode(Node):
    def __init__(self, meshPath="", diffusePath=f"{dirPath}/assets/blank.PNG", specularPath=f"{dirPath}/assets/blank.PNG"):
        super().__init__()
        self.mesh = Mesh(meshPath)

        self.diffuseTexture = Texture(diffusePath, GL.GL_RGBA)
        self.specularTexture = Texture(specularPath, GL.GL_RGBA)

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
    
    def renderChildren(self, camera, numLights,lightPositions,lightColors,lightFalloffs):
        self.render(camera, numLights,lightPositions,lightColors,lightFalloffs)
        for child in self.children:
            child.renderChildren(camera, numLights,lightPositions,lightColors,lightFalloffs)