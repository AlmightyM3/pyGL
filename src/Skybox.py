import OpenGL.GL as GL
from PIL import Image
import numpy
from Mesh import Mesh
from Shader import Shader

class Skybox:
    def __init__(self, skyboxFolder, shader):
        self.textureID = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_CUBE_MAP, self.textureID)

        faces = ["right", "left", "top", "bottom", "front", "back"]
        for i in range(6):
            img = numpy.array(Image.open(f"{skyboxFolder}{faces[i]}.jpg"), numpy.int8)
            GL.glTexImage2D(GL.GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, GL.GL_RGB, numpy.size(img,0), numpy.size(img,1), 0, GL.GL_RGB, GL.GL_UNSIGNED_BYTE, img)
        
        GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_WRAP_R, GL.GL_CLAMP_TO_EDGE)

        self.mesh = Mesh("CUBE",False)
        self.shader = shader

    def render(self, camera):
        self.shader.use()
        view = numpy.eye(4)
        view[:3, :3] = camera.matrix[:3, :3]
        self.shader.setMat4("view", view)
        self.shader.setMat4("projection", camera.proj)
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_CUBE_MAP, self.textureID)
        self.shader.setInt("skybox", 0)
        GL.glDepthFunc(GL.GL_LEQUAL)
        self.mesh.render()

        GL.glDepthFunc(GL.GL_LESS)

