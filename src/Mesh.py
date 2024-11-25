import numpy
import OpenGL.GL as GL
import ctypes

from ModelLoader import OBJ

class Mesh:
    def __init__(self, path = "", backFaceCulling = True, depthBuffer = True):
        self.backFaceCulling = backFaceCulling
        self.depthBuffer = depthBuffer
        if path == "" or path == "CUBE":
            self.vertices = numpy.array([
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

            self.indices = numpy.array([
                0, 1, 2,  1, 3, 2, 
                4, 5, 6,  6, 7, 4, 
                8, 9, 10, 10,11,8, 
                14,13,12, 12,15,14,
                16,17,18, 18,19,16,
                22,21,20, 20,23,22
            ], numpy.uint32)
        elif path == "UI":
            self.vertices = numpy.array([
                #positions         normals           texture coords
                 0.5,  0.5, 0.0,   0.0,  0.0, 1.0,   1.0, 1.0,
                 0.5, -0.5, 0.0,   0.0,  0.0, 1.0,   1.0, 0.0,
                -0.5, -0.5, 0.0,   0.0,  0.0, 1.0,   0.0, 0.0,
                -0.5,  0.5, 0.0,   0.0,  0.0, 1.0,   0.0, 1.0
            ], numpy.float32)

            self.indices = numpy.array([
                3, 1, 0,
                3, 2, 1 
            ], numpy.uint32)
        else:
            modle = OBJ(path)
            self.vertices = modle.vertices
            self.indices = modle.indices
        
        self.VBO = GL.glGenBuffers(1)
        self.VAO = GL.glGenVertexArrays(1) 
        GL.glBindVertexArray(self.VAO)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.VBO)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL.GL_STATIC_DRAW)

        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 32, ctypes.c_void_p(0)) # 32 = 8*(32/8) 
        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, GL.GL_FALSE, 32, ctypes.c_void_p(3*self.vertices.itemsize))
        GL.glEnableVertexAttribArray(1)
        GL.glVertexAttribPointer(2, 2, GL.GL_FLOAT, GL.GL_FALSE, 32, ctypes.c_void_p(6*self.vertices.itemsize))
        GL.glEnableVertexAttribArray(2)
        
        self.EBO = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.EBO)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL.GL_STATIC_DRAW)

    def render(self):
        if self.backFaceCulling:
            GL.glEnable(GL.GL_CULL_FACE)
        else:
            GL.glDisable(GL.GL_CULL_FACE)
        if self.depthBuffer:
            GL.glEnable(GL.GL_DEPTH_TEST)
        else:
            GL.glDisable(GL.GL_DEPTH_TEST)
        GL.glBindVertexArray(self.VAO)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.EBO)
        GL.glDrawElements(GL.GL_TRIANGLES, len(self.indices), GL.GL_UNSIGNED_INT, None)