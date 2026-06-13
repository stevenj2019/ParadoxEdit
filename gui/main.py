from PyQt5.QtWidgets import QMainWindow, QSplitter
from PyQt5.QtCore import Qt
from gui.mod_panel import ModPanel
from gui.contents_panel import ContentsPanel
from gui.interactions import connect_main_events


#basic shit works, click a relevant mod item, itll get the attached object anf load it to the right,
#this absolutely, works, but the vategories need a hell of a lot more work, 
# i need to integrate ._organise() somewhere, 
class MainWindow(QMainWindow):
    def __init__(self, mod):
        super().__init__()
        self.mod = mod
        self.safe_mode:bool = True #disable to stop generating .bak
        # self.been_modified:bool = False #idk if i need this
        self.bulk_warning_shown:bool = False

        self.setWindowTitle("ParadoxEdit")
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

        connect_main_events(self)