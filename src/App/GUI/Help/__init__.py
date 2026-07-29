import sys
from pathlib import Path

from PyQt5.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)


class HelpDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.pages = []
        self.page_buttons = []

        if getattr(sys, "frozen", False):
            self.html_directory = Path(sys._MEIPASS) / "HTML"
        else:
            self.html_directory = (Path(__file__).parent / "HTML")

        layout = QHBoxLayout(self)
        self.nav = QVBoxLayout()
        layout.addLayout(self.nav)

        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        self.add_page("General", "General.html")
        self.add_page("Workspaces/Load Order", "LoadOrder.html")
        self.add_page("Directory Tree", "FileTree.html")
        self.add_page("File Tree", "ScriptViewer.html")
        self.add_page("Report Issues", "GithubHelp.html")
        self.show()

    def add_page(self, name:str, file:str) -> None:
        widget = HelpPage(self.read_html(file))
        button = QPushButton(name)
        button.clicked.connect(lambda _, w=widget: self.stack.setCurrentWidget(w))
        self.nav.addWidget(button)
        self.page_buttons.append(button)

        self.stack.addWidget(widget)
        self.pages.append(widget)

    def read_html(self, file_name:str) -> None:
        return (self.html_directory / file_name).read_text()
    
class HelpPage(QWidget):
    def __init__(self, text:str):
        super().__init__()

        layout = QVBoxLayout(self)
        page_contents = QTextBrowser()
        page_contents.setHtml(text)
        layout.addWidget(page_contents)
