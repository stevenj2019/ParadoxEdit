import qdarktheme

from PyQt5.QtWidgets import QApplication

from App.Services import ConfigurationManager, StyleManager, FilesystemMananger
from App.GUI.Main import MainWindow

from App.Constants import ChangeState
from App.Enums import SaveTarget

class AppController:
    def __init__(self):
        self.app            = QApplication([])
        self.config         = ConfigurationManager()
        self.style_manager  = StyleManager(self)
        # self.file_system.change_tracker = ChangeTracker()
        self.file_system    = FilesystemMananger(self)

        self.main = MainWindow(self)
        self.apply_stylesheet()
        self.run()

    def cancel_edit(self):
        self.main.editor_session.cancel_request()

    def apply_stylesheet(self):
        self.app.setStyleSheet(qdarktheme.load_stylesheet("dark" if self.config.dark_mode else "light"))

    def run(self):
        self.main.show()
        self.app.exec_()

    def load_mod(self, path):
        try:
            self.file_system.load_mod(path)
        except Exception as e:
            self.main.load_mod_failed(e)
            return 
        
        self.main.load_mod_to_gui(self.file_system.mod)

    def modify_node(self, node, new_value):
        if node.value is not new_value:
            file = self.file_system.open_file
            node.value = new_value
            self.file_system.changed_file(file, node, ChangeState.MODIFIED)
            self.main.propogate_changes(file, node)

    def save_target(self, target):
        def save_routine(file):
            saved = self.file_system.save_file(file)
            if saved:
                self.main.propogate_save(file)

        if target is SaveTarget.ALL:
            for category in self.file_system.mod.categories.values():
                for file in category.files.values():
                    save_routine(file)
        else:
            save_routine(self.file_system.open_file)

    # def save_file(self, file):
    #     self.file_system.change_tracker.clear_file_state(file)
    #     self.file_system.save_file(file)
    #     self.main.propogate_save(file)
