from PyQt5.QtWidgets import QWidget, QStackedWidget, QVBoxLayout

from ParadoxParser import ParadoxScriptParser as PDXScript, ParadoxLocParser as PDXLoc

from App.Loading.Models import IconFile
from App.GUI.Main.Contents.ScriptView import ScriptView
from App.GUI.Main.Contents.ImageView import IconView

class ContentsPanel(QWidget):
    def __init__(self, app_controller):
        super().__init__()
        self.stack = QStackedWidget()

        self.script_view = ScriptView(app_controller)
        self.stack.addWidget(self.script_view)

        self.image_viewer = IconView(app_controller)
        self.stack.addWidget(self.image_viewer)

        layout = QVBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)

    def load_file(self, file):
        if isinstance(file.file, (PDXScript, PDXLoc)):
            self.show_script(file)
        elif isinstance(file.file, IconFile):
            self.show_image(file)

    def show_script(self, file):
        self.stack.setCurrentWidget(self.script_view)
        self.script_view.load_block(file)

    def show_image(self, file):
        self.stack.setCurrentWidget(self.image_viewer)
        self.image_viewer.load_image(file)
        return 