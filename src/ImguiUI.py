import imgui # On lines 3 and 12 of imgui\integrations\pygame.py change FixedPipelineRenderer to ProgrammablePipelineRenderer
from imgui.integrations.pygame import PygameRenderer
import OpenGL.GL as GL

class GUI:
    def __init__(self, WINDOW_SIZE, rootNode):
        self._makeImGUIHappy()

        imgui.create_context()
        self.impl = PygameRenderer()

        self.io = imgui.get_io()
        self.io.display_size = WINDOW_SIZE

        self.shouldMakeCube=False
        self.inspectedNode = rootNode
    
    def draw(self, rootNode):
        self._makeImGUIHappy()

        imgui.new_frame()

        if imgui.begin_main_menu_bar():
            if imgui.begin_menu("File", True):
                clicked_quit, selected_quit = imgui.menu_item(
                    "Quit", "ESC", False, True
                )
                if clicked_quit:
                    run=False
                imgui.end_menu()
            if imgui.begin_menu("Edit", True):
                clicked_AddCube, selected_AddCube = imgui.menu_item(
                    "Add Cube", "", False, True
                )
                if clicked_AddCube:
                    self.shouldMakeCube=True
                imgui.end_menu()
            imgui.end_main_menu_bar()

        #imgui.show_test_window()
        imgui.begin("Node Tree")
        clickedNode = rootNode.treeUI()
        if clickedNode:
            self.inspectedNode = clickedNode
        imgui.end()
        
        if imgui.begin("Node Inspector"):
            self.inspectedNode.inspectorUI(rootNode)
        imgui.end()
        
        imgui.render()
        self.impl.render(imgui.get_draw_data())
    
    def processEvent(self, event):
        self.impl.process_event(event)
    def processInputs(self):
        self.impl.process_inputs()

    def _makeImGUIHappy(self):
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER,0)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)
        GL.glUseProgram(0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
        GL.glActiveTexture(GL.GL_TEXTURE0)