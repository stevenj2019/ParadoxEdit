from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App import AppController
    from App.Loading.Models import FileReference

from ParadoxParser import ParadoxLocParser as PDXLoc
from ParadoxParser import ParadoxScriptParser as PDXScript
from PyQt5.QtWidgets import QStackedWidget, QVBoxLayout, QWidget

from App.GUI.Main.Contents.ImageView import IconView
from App.GUI.Main.Contents.ScriptView import ScriptView
from App.Loading.Models import IconFile


class ContentsPanel(QWidget):
    def __init__(self, app_controller:AppController) -> None:
        super().__init__()
        self.stack = QStackedWidget()

        self.script_view = ScriptView(app_controller)
        self.stack.addWidget(self.script_view)

        self.image_viewer = IconView(app_controller)
        self.stack.addWidget(self.image_viewer)

        layout = QVBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)

    def load_file(self, file:FileReference) -> None:
        if isinstance(file.file, (PDXScript, PDXLoc)):
            self.show_script(file)
        elif isinstance(file.file, IconFile):
            self.show_image(file)

    def show_script(self, file:FileReference) -> None:
        self.stack.setCurrentWidget(self.script_view)
        self.script_view.load_block(file)

    def show_image(self, file:FileReference) -> None:
        self.stack.setCurrentWidget(self.image_viewer)
        self.image_viewer.load_image(file)
        return 