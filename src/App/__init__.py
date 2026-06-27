import qdarktheme

from PyQt5.QtWidgets import QApplication

from ParadoxParser.ParadoxNodes import GenericBlock

from App.Services import ConfigurationManager, StyleManager, ChangeTracker, FilesystemMananger
from App.GUI.Main import MainWindow

from App.Constants import ChangeState
from App.Enums import SaveTarget

class AppController:
    def __init__(self):
        self.app            = QApplication([])
        self.config         = ConfigurationManager()
        self.style_manager  = StyleManager(self)
        self.change_tracker = ChangeTracker()
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
            self.change_tracker.set_file_state(file, ChangeState.MODIFIED)

            node.value = new_value
            self.change_tracker.set_node_state(node, ChangeState.MODIFIED)
            
            self.main.propogate_changes(file, node)

    def save_target(self, target):
        if target is SaveTarget.ALL:
            for category in self.mod.categories:
                for file in category:
                    if self.change_tracker.get_file_dirty(file):
                        self.change_tracker.clear_file_dirty(file)
                        self.save_file(file)
        else:
            if self.change_tracker.get_file_dirty(file):
                self.save_file(self.file_system.open_file)

    def save_file(self, file):
        def recurse(node):
            self.change_tracker.clear_node_state(node)
            if isinstance(node, GenericBlock):
                for _node in node.nodes:
                    recurse(_node)

        # for node in file.obj.nodes:
        for node in file.nodes:
            recurse(node)

        self.file_system.save_file(file)
