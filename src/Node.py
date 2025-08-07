import OpenGL.GL as GL
import numpy
import imgui
from pygame import Vector3
from Transform import Transform
from Mesh import Mesh
from Shader import Shader
from Texture import Texture
from MatrixTools import orthographic,perspective,view

import os
dirPath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if "\\" in dirPath:
    dirPath = dirPath.replace("\\", "/")

class Node:
    def __init__(self, name="Unnamed Node"):
        self.transform = Transform()
        self.children: list[Node] = []
        self.parent: Node = None
        self.name = name

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
        
        if self.parent == None:
            self.worldMatrix = self.transform.localMatrix
        else:
            self.worldMatrix = numpy.dot(self.transform.localMatrix, self.parent.worldMatrix)

        self.worldPosition = Vector3(*self.worldMatrix.T.dot([0,0,0,1])[:3])

        for child in self.children:
            child.updateWorldMatrix()
    
    def renderChildren(self, camera, lights):
        for child in self.children:
            child.renderChildren(camera, lights)

    def renderChildrenWithShader(self, shader):
        for child in self.children:
            child.renderChildrenWithShader(shader)
    
    def treeUI(self):
        clicked = None
        if self.children:
            if imgui.tree_node(self.name,imgui.TREE_NODE_OPEN_ON_DOUBLE_CLICK|imgui.TREE_NODE_OPEN_ON_ARROW):
                if imgui.is_item_clicked():
                    clicked=self
                for child in self.children:
                    childClicked = child.treeUI()
                    if childClicked:
                        clicked=childClicked
                imgui.tree_pop()
            elif imgui.is_item_clicked():
                clicked=self
        else:
            imgui.indent()
            imgui.text(self.name)
            if imgui.is_item_clicked():
                clicked=self
            imgui.unindent()
        return clicked
    def inspectorUI(self, rootNode):
        nChanged, newName = imgui.input_text('Object Name', self.name)
        if nChanged:
            self.name = newName

        imgui.text("\nLocal Transform: ")
        imgui.indent()
        pChanged, pValues = imgui.input_float3("Position",*self.transform.position)
        if pChanged:
            self.transform.position = Vector3(pValues)

        r1Changed, rValues = imgui.input_float3("Rotation Axis",*self.transform.rotationAxis)
        if r1Changed:
            self.transform.rotationAxis = Vector3(rValues)

        r2Changed, rValue = imgui.input_float("Rotation Angle", self.transform.rotationAngle)
        if r2Changed:
            self.transform.rotationAngle = rValue

        sChanged, sValues = imgui.input_float3("Scale",*self.transform.scale)
        if sChanged:
            self.transform.scale = Vector3(sValues)
        imgui.unindent()

        imgui.text(f"\nNum Children: {len(self.children)}")
        pChanged, pValue = imgui.input_text('Parent', self.parent.name if self.parent else "")
        if pChanged:
            newParent = rootNode.getFromName(pValue)
            if newParent:
                self.setParent(newParent)
    
    def getFromName(self, name):
        if self.name == name:
            return self
        for child in self.children:
            childOut = child.getFromName(name)
            if childOut:
                return childOut
        return None

class RenderNode(Node):
    def __init__(self, mesh:Mesh,shader:Shader,diffuseTexture:Texture,specularTexture:Texture, name="Unnamed RenderNode"): #meshPath="", diffusePath=f"{dirPath}/assets/blank.PNG", specularPath=f"{dirPath}/assets/blank.PNG"
        super().__init__(name)
        self.mesh = mesh #Mesh(meshPath)

        self.diffuseTexture = diffuseTexture #Texture(diffusePath, GL.GL_RGBA)
        self.specularTexture = specularTexture #Texture(specularPath, GL.GL_RGBA)

        self.shader = shader #Shader(f"{dirPath}/src/shaders/shader.vert", f"{dirPath}/src/shaders/shader.frag")
    
    def render(self, camera, lights):
        self.shader.use()
        
        self.shader.setMat4("view", camera.matrix)
        self.shader.setVec3("viewPos", camera.position)
        self.shader.setMat4("projection", camera.proj)
        self.shader.setMat4("transform", self.worldMatrix)

        numPoint,numDirectional = 0,0
        for light in lights:
            lightNum = numDirectional+numPoint

            GL.glActiveTexture(GL.GL_TEXTURE2+lightNum)
            if light.isDirectional:
                GL.glBindTexture(GL.GL_TEXTURE_2D, light.depthMap)
                self.shader.setVec3(f"directionalLights[{numDirectional}].ambient", light.color*0.2)
                self.shader.setVec3(f"directionalLights[{numDirectional}].diffuse", light.color*0.5)
                self.shader.setVec3(f"directionalLights[{numDirectional}].specular", Vector3(1.0))
                self.shader.setVec3(f"directionalLights[{numDirectional}].direction", light.worldPosition)
                self.shader.setMat4(f"directionalLights[{numDirectional}].lightSpaceMatrix", light.lightSpaceMatrix)
                self.shader.setInt(f"directionalLights[{numDirectional}].shadowMap", 2+lightNum)
                numDirectional+=1
            else:
                GL.glBindTexture(GL.GL_TEXTURE_CUBE_MAP, light.depthMap)
                self.shader.setVec3(f"pointLights[{numPoint}].ambient", light.color*0.2)
                self.shader.setVec3(f"pointLights[{numPoint}].diffuse", light.color*0.5)
                self.shader.setVec3(f"pointLights[{numPoint}].specular", Vector3(1.0))
                self.shader.setVec3(f"pointLights[{numPoint}].position", light.worldPosition)
                self.shader.setFloat(f"pointLights[{numPoint}].falloff", light.falloff)
                self.shader.setFloat(f"pointLights[{numPoint}].farPlane", 15)
                self.shader.setInt(f"pointLights[{numPoint}].shadowMap", 2+lightNum)
                numPoint+=1
        
        self.shader.setInt("material.diffuse", 0)
        self.shader.setInt("material.specular", 1)
        self.shader.setFloat("material.shininess", 32.0)

        self.diffuseTexture.use(0)
        self.specularTexture.use(1)
        
        self.mesh.render()
    
    def renderChildren(self, camera, lights):
        self.render(camera, lights)
        super().renderChildren(camera, lights)

    def renderWithShader(self, shader):
        shader.use()
        shader.setMat4("transform", self.worldMatrix)

        self.mesh.render()
    
    def renderChildrenWithShader(self, shader):
        self.renderWithShader(shader)
        super().renderChildrenWithShader(shader)
    
    def inspectorUI(self, rootNode):
        super().inspectorUI(rootNode)
        imgui.text(f"\nMesh: {self.mesh}")
        imgui.text(f"Diffuse Texture: {self.diffuseTexture}")
        imgui.text(f"Specular Texture: {self.specularTexture}")

class LightNode(Node):
    def __init__(self, lights, name="Unnamed LightNode", color=Vector3(1), falloff=0.06, isDirectional=False):
        super().__init__(name)
        self.mesh = Mesh()

        self.transform.scale = Vector3(0.2)
        self.color = color
        self.falloff = falloff
        self.isDirectional = isDirectional
        self.calcLightSpaceMatrix()

        self.shader = Shader(f"{dirPath}/src/shaders/light.vert", f"{dirPath}/src/shaders/light.frag")

        lights.append(self)

        self.depthMap = GL.glGenTextures(1)
        if self.isDirectional:
            GL.glBindTexture(GL.GL_TEXTURE_2D, self.depthMap)
            GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_DEPTH_COMPONENT, 1024, 1024, 0, GL.GL_DEPTH_COMPONENT, GL.GL_FLOAT, None)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_NEAREST)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_NEAREST)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_BORDER)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_BORDER)
            GL.glTexParameterfv(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_BORDER_COLOR, [1.0,1.0,1.0,1.0])
        else:
            GL.glBindTexture(GL.GL_TEXTURE_CUBE_MAP, self.depthMap)
            for i in range(6):
                GL.glTexImage2D(GL.GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, GL.GL_DEPTH_COMPONENT, 1024, 1024, 0, GL.GL_DEPTH_COMPONENT, GL.GL_FLOAT, None)
            GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_MIN_FILTER, GL.GL_NEAREST)
            GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_MAG_FILTER, GL.GL_NEAREST)
            GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
            GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)
            GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_WRAP_R, GL.GL_CLAMP_TO_EDGE)

    def calcLightSpaceMatrix(self):
        try:
            if self.isDirectional:
                self.lightSpaceMatrix = orthographic(5,1,0,15).dot(view(self.worldPosition,Vector3(0 if self.worldPosition!=Vector3(0) else 1),Vector3(0,1,0)).T).T
            else:
                shadowProj = perspective(90, 1, 1, 15) # znear must be 1
                self.lightSpaceMatrix = [
                    shadowProj.dot(view(self.worldPosition,self.worldPosition+Vector3(1,0,0),Vector3(0,-1,0)).T).T,
                    shadowProj.dot(view(self.worldPosition,self.worldPosition+Vector3(-1,0,0),Vector3(0,-1,0)).T).T,
                    shadowProj.dot(view(self.worldPosition,self.worldPosition+Vector3(0,1,0),Vector3(0,0,1)).T).T,
                    shadowProj.dot(view(self.worldPosition,self.worldPosition+Vector3(0,-1,0),Vector3(0,0,-1)).T).T,
                    shadowProj.dot(view(self.worldPosition,self.worldPosition+Vector3(0,0,1),Vector3(0,-1,0)).T).T,
                    shadowProj.dot(view(self.worldPosition,self.worldPosition+Vector3(0,0,-1),Vector3(0,-1,0)).T).T,
                ]
        except(AttributeError):
            self.lightSpaceMatrix = numpy.eye(4)
            

    def updateWorldMatrix(self):
        super().updateWorldMatrix()
        self.calcLightSpaceMatrix()
    
    def render(self, camera):
        self.shader.use()
        
        self.shader.setMat4("view", camera.matrix)
        self.shader.setVec3("viewPos", camera.position)
        self.shader.setMat4("projection", camera.proj)
        self.shader.setMat4("transform", self.worldMatrix)
        self.shader.setVec3("lightColor", self.color)
        
        self.mesh.render()
    
    def renderChildren(self, camera, lights):
        self.render(camera)
        super().renderChildren(camera, lights)
    
    def renderDepthMap(self, depthMapFBO, depthShader, rootNode):
        GL.glViewport(0, 0, 1024, 1024)
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, depthMapFBO)
        
        if self.isDirectional:
            GL.glFramebufferTexture2D(GL.GL_FRAMEBUFFER, GL.GL_DEPTH_ATTACHMENT, GL.GL_TEXTURE_2D, self.depthMap, 0)
        else:
            GL.glFramebufferTexture(GL.GL_FRAMEBUFFER, GL.GL_DEPTH_ATTACHMENT, self.depthMap, 0)

        GL.glDrawBuffer(GL.GL_NONE)
        GL.glReadBuffer(GL.GL_NONE)

        # GL.glCullFace(GL.GL_FRONT)

        GL.glClear(GL.GL_DEPTH_BUFFER_BIT)
        depthShader.use()
        if self.isDirectional:
            depthShader.setMat4("lightSpaceMatrix", self.lightSpaceMatrix)
        else:
            depthShader.setVec3("lightPos", self.worldPosition)
            depthShader.setFloat("farPlane", 15)
            for i in range(6):
                depthShader.setMat4(f"shadowMatrices[{i}]", self.lightSpaceMatrix[i])
        
        rootNode.renderChildrenWithShader(depthShader)
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)
        # GL.glCullFace(GL.GL_BACK)

    def inspectorUI(self, rootNode):
        super().inspectorUI(rootNode)
        imgui.text(f"\nMesh: {self.mesh}")
        imgui.text(f"")
        dChanged, dValue = imgui.checkbox("Is Directional",self.isDirectional)
        if dChanged:
            self.isDirectional = dValue
        
        cChanged, cValues = imgui.color_edit3("Color",*self.color)
        if cChanged:
            self.color = Vector3(cValues)

        fChanged, fValue = imgui.input_float("Falloff", self.falloff)
        if fChanged:
            self.falloff = fValue