import numpy
from pygame import Vector3
from MatrixTools import translate, rotate, scale

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