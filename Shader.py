import OpenGL.GL as GL

class Shader:  
    def __init__(self, vertexPath, fragmentPath):
        with open(vertexPath, 'r') as file:
            vertexShaderSource = file.read()
            
        
        vertexShader = GL.glCreateShader(GL.GL_VERTEX_SHADER)
        GL.glShaderSource(vertexShader, vertexShaderSource)
        GL.glCompileShader(vertexShader)

        log = GL.glGetShaderInfoLog(vertexShader)
        if isinstance(log, bytes):
            log = log.decode()
        for line in log.split("\n"):
            print(line)

        with open(fragmentPath, 'r') as file:
            fragmentShaderSource = file.read()
        
        fragmentShader = GL.glCreateShader(GL.GL_FRAGMENT_SHADER)
        GL.glShaderSource(fragmentShader, fragmentShaderSource)
        GL.glCompileShader(fragmentShader)
        
        log = GL.glGetShaderInfoLog(fragmentShader)
        if isinstance(log, bytes):
            log = log.decode()
        for line in log.split("\n"):
            print(line)

        self.ID = GL.glCreateProgram()
        GL.glAttachShader(self.ID, vertexShader)
        GL.glAttachShader(self.ID, fragmentShader)
        GL.glLinkProgram(self.ID)

        log = GL.glGetProgramInfoLog(self.ID)
        if isinstance(log, bytes):
            log = log.decode()
        for line in log.split("\n"):
            print(line)
        
        GL.glDeleteShader(vertexShader)
        GL.glDeleteShader(fragmentShader)

    def use(self):
        GL.glUseProgram(self.ID)
    
    def setBool(self, name, value):
        GL.glUniform1i(GL.glGetUniformLocation(self.ID, name), int(value))
    def setInt(self, name, value):
        GL.glUniform1i(GL.glGetUniformLocation(self.ID, name), value)
    def setFloat(self, name, value):
        GL.glUniform1f(GL.glGetUniformLocation(self.ID, name), value)