import OpenGL.GL as GL
import numpy

class Shader:  
    def __init__(self, vertexPath, fragmentPath):
        with open(vertexPath, 'r') as file:
            vertexShaderSource = file.read()
        
        vertexShader = GL.glCreateShader(GL.GL_VERTEX_SHADER)
        GL.glShaderSource(vertexShader, vertexShaderSource)
        GL.glCompileShader(vertexShader)

        log = GL.glGetShaderInfoLog(vertexShader)
        self._printDebugLog(log)

        with open(fragmentPath, 'r') as file:
            fragmentShaderSource = file.read()
        
        fragmentShader = GL.glCreateShader(GL.GL_FRAGMENT_SHADER)
        GL.glShaderSource(fragmentShader, fragmentShaderSource)
        GL.glCompileShader(fragmentShader)
        
        log = GL.glGetShaderInfoLog(fragmentShader)
        self._printDebugLog(log)

        self.ID = GL.glCreateProgram()
        GL.glAttachShader(self.ID, vertexShader)
        GL.glAttachShader(self.ID, fragmentShader)
        GL.glLinkProgram(self.ID)

        log = GL.glGetProgramInfoLog(self.ID)
        self._printDebugLog(log)
        
        GL.glDeleteShader(vertexShader)
        GL.glDeleteShader(fragmentShader)

    def _printDebugLog(self, log):
        if isinstance(log, bytes):
            log = log.decode()
        for line in log.split("\n"):
            if line == "":
                continue
            print(line)
    
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