from PyQt5.QtWidgets import QApplication, QMainWindow, QSplitter
from PyQt5.QtCore import Qt
from PyQt5.Qt import QMenu
from PyQt5.QtGui import QCursor
from gui.mod_panel import ModPanel
from gui.contents_panel import ContentsPanel
from gui.util import get_safe_mode_opposed_text, toggle_dark_mode, add_menu_heading
from gui.warning_messages import toggle_safe_mode_warning
# from gui.interactions import connect_main_events

#basic shit works, click a relevant mod item, itll get the attached object anf load it to the right,
#this absolutely, works, but the vategories need a hell of a lot more work, 
# i need to integrate ._organise() somewhere, 
class MainWindow(QMainWindow):
    def __init__(self, mod, config):
        super().__init__()
        self.mod = mod
        self.config = config
        self.safe_mode:bool = True #disable to stop generating .bak
        # self.been_modified:bool = False #idk if i need this
        self.bulk_warning_shown:bool = False

        self.setWindowTitle("ParadoxEdit")
        splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(splitter)

        self.mod_panel = ModPanel(mod)
        self.mod_panel.setMinimumWidth(150)
        self.right_panel = ContentsPanel(mod)
        self.right_panel.setMinimumWidth(300)
        
        self.right_panel.load_block(self.mod.descriptor_object)

        splitter.addWidget(self.mod_panel)
        splitter.addWidget(self.right_panel)
        splitter.setSizes([200, 600])

        self.mod_panel.request_load_block.connect(
            self.right_panel.load_block
        )
        self.mod_panel.request_context_menu.connect(
            self.show_context_menu
        )

    def show_context_menu(self, panel, selected):
        menu = QMenu(self)

        # menu.addSection("Editor")
        add_menu_heading(menu, "Editor")
        menu.addAction("Toggle Dark Mode", lambda:toggle_dark_mode(self))
        menu.addAction(f"{get_safe_mode_opposed_text(self)} Safe Mode", lambda:toggle_safe_mode_warning(self))

        panel.populate_context_menu(menu, self, selected)

        menu.exec_(QCursor.pos())