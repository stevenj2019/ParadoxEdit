import sys
import traceback

from PyQt5.QtWidgets import QApplication, QDialog

from App.Services import ConfigurationManager, StyleManager, InlineEditManager, ChangeTracker, FilesystemMananger
from App.GlobalEventFilter import GlobalEventFilter
from App.GUI.Windows import MainWindow
from App.GUI.Windows.Settings import SettingsWindow

from App.Constants import ChangeState

class AppController:
    def __init__(self):
        self.app            = QApplication([])
        self.config         = ConfigurationManager()
        self.style_manager  = StyleManager()
        self.change_tracker = ChangeTracker()
        self.file_system    = FilesystemMananger()

        self.editor_session = InlineEditManager(
            mutate_callback=self.mutate_node
        )
        self.inline_filter = GlobalEventFilter(
            cancel_callback=self.editor_session.cancel_request
        )

        self.app.installEventFilter(self.inline_filter)
        self.apply_stylesheet()
        self.main = MainWindow(self)
        self.run()

    def apply_stylesheet(self):
        self.app.setStyleSheet(self.style_manager._build_stylesheet(self.config.dark_mode))

    def run(self):
        if not self.config.initalised:
            settings = SettingsWindow("PDXEdit Setup", self.config)
            if not settings.exec_() == QDialog.Accepted:
                sys.exit()
        
        self.main.show()
        self.app.exec_()

    def load_mod(self, path):
        try:
            self.file_system.load_mod(path)
        except Exception as e:
            self.main.load_mod_failed(e)
            return 
        
        self.main.load_mod_to_gui(self.file_system.mod)

    def mutate_node(self, node, new_value):
        if node.value is not new_value:
            node.value = new_value
            self.change_tracker.set_state(node, ChangeState.MODIFIED)
            self.main.propogate_changes(None, None, node)