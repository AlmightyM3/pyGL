import OpenGL.GL as GL
import numpy

class Shader:  
    def __init__(self, vertexPath="", fragmentPath="", geometryPath=""):
        
        vertexShader = self._compileShaderFromFile(vertexPath, GL.GL_VERTEX_SHADER)
        fragmentShader = self._compileShaderFromFile(fragmentPath, GL.GL_FRAGMENT_SHADER)
        geometryShader = self._compileShaderFromFile(geometryPath, GL.GL_GEOMETRY_SHADER)

        self.ID = GL.glCreateProgram()
        GL.glAttachShader(self.ID, vertexShader)
        GL.glAttachShader(self.ID, fragmentShader)
        if geometryShader:
            GL.glAttachShader(self.ID, geometryShader)
        GL.glLinkProgram(self.ID)

        log = GL.glGetProgramInfoLog(self.ID)
        self._printDebugLog(log)
        
        GL.glDeleteShader(vertexShader)
        GL.glDeleteShader(fragmentShader)
        if geometryShader:
            GL.glDeleteShader(geometryShader)

    def _printDebugLog(self, log):
        if isinstance(log, bytes):
            log = log.decode()
        for line in log.split("\n"):
            if line == "":
                continue
            print(line)
    
    def _compileShader(self, shaderSource, type):
        shader = GL.glCreateShader(type)
        GL.glShaderSource(shader, shaderSource)
        GL.glCompileShader(shader)

        log = GL.glGetShaderInfoLog(shader)
        self._printDebugLog(log)
        return shader

    def _compileShaderFromFile(self, path, type):
        if path != "":
            with open(path, 'r') as file:
                shaderSource = file.read()
            return self._compileShader(shaderSource, type)
            
    def use(self):
        GL.glUseProgram(self.ID)
    
    def setBool(self, name, value):
        GL.glUniform1i(GL.glGetUniformLocation(self.ID, name), int(value))
    def setInt(self, name, value):
        GL.glUniform1i(GL.glGetUniformLocation(self.ID, name), value)
    def setFloat(self, name, value):
        GL.glUniform1f(GL.glGetUniformLocation(self.ID, name), value)
    def setVec3(self, name, value):
        GL.glUniform3fv(GL.glGetUniformLocation(self.ID, name), 1, numpy.array(value,numpy.float32))
    def setMat4(self, name, value):
        GL.glUniformMatrix4fv(GL.glGetUniformLocation(self.ID, name), 1, GL.GL_FALSE, value)