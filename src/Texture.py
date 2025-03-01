import OpenGL.GL as GL
from PIL import Image
import numpy

class Texture:
    def __init__(self, imgPath, type=GL.GL_RGBA):
        self.ID = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.ID)
        
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_REPEAT)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_REPEAT)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)

        img = numpy.flip(numpy.array(Image.open(imgPath), numpy.int8),0)
        if imgPath[len(imgPath)-3:].lower() == "png":
            type=GL.GL_RGBA
        elif imgPath[len(imgPath)-3:].lower() == "jpg":
            type=GL.GL_RGB
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, type, numpy.size(img,0), numpy.size(img,1), 0, type, GL.GL_UNSIGNED_BYTE, img)
        GL.glGenerateMipmap(GL.GL_TEXTURE_2D)

    def use(self, texUnit):
        GL.glActiveTexture(GL.GL_TEXTURE0+texUnit)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.ID)