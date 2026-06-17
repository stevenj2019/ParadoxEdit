from PyQt5.QtWidgets import QMainWindow, QWidget, QSplitter, QVBoxLayout, QToolBar, QAction
from PyQt5.QtCore import Qt
from PyQt5.Qt import QMenu
from PyQt5.QtGui import QCursor
from gui.mod_panel import ModPanel
from gui.contents_panel import ContentsPanel
from gui.settings import SettingsWindow
from gui.util import get_safe_mode_opposed_text, toggle_dark_mode, add_menu_heading, get_main_window
from gui.warning_messages import toggle_safe_mode_warning

class MainWindow(QMainWindow):
    def __init__(self, mod, config):
        super().__init__()
        self.mod = mod
        self.config = config
        self.safe_mode:bool = config.safe_mode
        self.bulk_warning_shown:bool = False

        self.setWindowTitle("ParadoxEdit")
        #TopBar
        topbar = MainTopBar(self)
        self.addToolBar(topbar)
        #Splitter
        splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(splitter)

        #ModPanel(left)
        self.mod_panel = ModPanel(mod)
        self.mod_panel.setMinimumWidth(150)
        splitter.addWidget(self.mod_panel)

        self.right_panel = ContentsPanel(mod)
        self.right_panel.setMinimumWidth(300)
        self.right_panel.load_block(self.mod.descriptor_object)
        splitter.addWidget(self.right_panel)
        
        self.mod_panel.request_load_block.connect(self.right_panel.load_block)
        self.mod_panel.request_context_menu.connect(self.show_context_menu)

        splitter.setSizes([200, 600])

    def show_context_menu(self, panel, selected):
        menu = QMenu(self)

        add_menu_heading(menu, "Editor")
        menu.addAction("Toggle Dark Mode", lambda:toggle_dark_mode(self.config))
        menu.addAction(f"{get_safe_mode_opposed_text(self)} Safe Mode", lambda:toggle_safe_mode_warning(self))
        panel.populate_context_menu(menu, self, selected)

        menu.exec_(QCursor.pos())

#OLD
# class MainTopBar(QWidget):
#     def __init__(self, parent):
#         super().__init__(parent)

#         self.setFixedHeight(40)
#         self.layout = QHBoxLayout(self)
#         self.layout.setContentsMargins(10, 0, 0, 0)
        
#         self.settings_button = QPushButton("Settings")
#         self.settings_button.clicked.connect(self.open_settings_window)
#         self.layout.addWidget(self.settings_button)

#         self.layout.addStretch()

#     def open_settings_window(self):
#         settings = SettingsWindow("PDXEdit Settings", get_main_window().config)
#         settings.exec_()

class MainTopBar(QToolBar):
    def __init__(self, parent):
        super().__init__(parent)

        self.setMovable(False)

        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.open_settings_window)
        self.addAction(settings_action)

        # self.settings_button = QPushButton("Settings")
        # self.settings_button.clicked.connect(self.open_settings_window)
        # self.layout.addWidget(self.settings_button)

        # self.layout.addStretch()

    def open_settings_window(self):
        settings = SettingsWindow("PDXEdit Settings", get_main_window().config)
        settings.exec_()