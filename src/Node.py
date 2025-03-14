import OpenGL.GL as GL
import numpy
import imgui
from pygame import Vector3
from Transform import Transform
from Mesh import Mesh
from Shader import Shader
from Texture import Texture
from MatrixTools import orthographic,view

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
        
        if not self.parent == None:
            self.worldMatrix = numpy.dot(self.transform.localMatrix, self.parent.worldMatrix)
        else:
            self.worldMatrix = self.transform.localMatrix

        for child in self.children:
            child.updateWorldMatrix()
    
    def renderChildren(self, camera, lights):
        for child in self.children:
            child.renderChildren(camera, lights)
    
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
            if light.isDirectional:
                self.shader.setVec3(f"directionalLights[{numDirectional}].ambient", light.color*0.2)
                self.shader.setVec3(f"directionalLights[{numDirectional}].diffuse", light.color*0.5)
                self.shader.setVec3(f"directionalLights[{numDirectional}].specular", Vector3(1.0))
                self.shader.setVec3(f"directionalLights[{numDirectional}].direction", Vector3(*light.parent.worldMatrix.dot([*light.transform.position,0])[:3]).normalize())
                numDirectional+=1
            else:
                self.shader.setVec3(f"pointLights[{numPoint}].ambient", light.color*0.2)
                self.shader.setVec3(f"pointLights[{numPoint}].diffuse", light.color*0.5)
                self.shader.setVec3(f"pointLights[{numPoint}].specular", Vector3(1.0))
                self.shader.setVec3(f"pointLights[{numPoint}].position", light.parent.worldMatrix.dot([*light.transform.position,0]))
                self.shader.setFloat(f"pointLights[{numPoint}].falloff", light.falloff)
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

    def calcLightSpaceMatrix(self):
        self.lightSpaceMatrix = orthographic(10,1,0.1,50).dot(view(self.transform.position,Vector3(0 if self.transform.position!=Vector3(0) else 1),Vector3(0,1,0))).T

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
