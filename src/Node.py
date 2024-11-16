from pygame import Vector3
from MatrixTools import *

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