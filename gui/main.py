from PyQt5.QtWidgets import QMainWindow, QSplitter
from PyQt5.QtCore import Qt
from gui.mod_panel import ModPanel
from gui.contents_panel import ContentsPanel

class MainWindow(QMainWindow):
    def __init__(self, mod):
        super().__init__()
        self.mod = mod

        splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(splitter)

        self.left_panel = ModPanel(mod)
        self.left_panel.setMinimumWidth(150)
        self.right_panel = ContentsPanel(mod)
        self.right_panel.setMinimumWidth(300)
        
        self.right_panel.load_block(self.mod.descriptor_object)

        splitter.addWidget(self.left_panel)
        splitter.addWidget(self.right_panel)
        splitter.setSizes([200, 600])