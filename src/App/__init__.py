import qdarktheme

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QApplication

from App.Services import ConfigurationManager, StyleManager, FilesystemMananger
from App.GUI.Main import MainWindow

from App.Enums import SaveTarget, PropagationType, ChangeState
from App.Contracts import PropagationRequest, NodeMutationRequest, BlockMutationRequest

class AppController(QObject):
    request_node_mutation = pyqtSignal(object)
    request_block_mutation = pyqtSignal(object)
    request_save = pyqtSignal(object)
    def __init__(self):
        super().__init__()
        self.app           = QApplication([])

        self.configuration = ConfigurationManager()
        self.file_system   = FilesystemMananger(self.configuration)
        self.style_manager = StyleManager(self.configuration)

        self.main = MainWindow(self)
        self.run()

    def run(self):
        self.app.setStyleSheet(qdarktheme.load_stylesheet("dark" if self.configuration.dark_mode else "light"))
        self.request_node_mutation.connect(self._request_node_mutation)
        self.request_block_mutation.connect(self._request_block_mutation)
        self.request_save.connect(self._save_target)
        self.main.show()
        self.app.exec_()

    def load_mod(self, path):
        try:
            self.file_system.load_mod(path)
        except Exception as e:
            self.main.load_mod_failed(e)
            return 
        
        self.main.load_mod_to_gui(self.file_system.mod)

    def _request_node_mutation(self, request:NodeMutationRequest):
        file = request.file if request.file else self.file_system.open_file
        node = request.node
        node_value = request.node_value
        value = request.value
        if node_value.value != value:
            node_value.value = value
            self.file_system.changed_file(file, node, ChangeState.MODIFIED)
            self.main.propagation_request.emit(PropagationRequest(type=PropagationType.NODE,
                                                                  file=file,
                                                                  node=node,
                                                                  state=ChangeState.MODIFIED))

    def _request_block_mutation(self, request:BlockMutationRequest):
        file = request.file if request.file else self.file_system.open_file
        node = request.target
        value = request.value
        state = request.state
        # if state == ChangeState.ADDED:
        #     node.insert(index, value)
        self.file_system.changed_file(file, node, state)
        self.main.propagation_request.emit(PropagationRequest(type=PropagationType.NODE, 
                                                       file=file,
                                                       node=node,
                                                       state=state))

    def _save_target(self, target):
        def save_routine(file):
            saved = self.file_system.save_file(file)
            if saved:
                self.main.propagation_request.emit(PropagationRequest(type=PropagationType.FILE, 
                                                                      file=file,
                                                                      node=None,
                                                                      state=ChangeState.CLEAN))

        if target is SaveTarget.ALL:
            save_routine(self.file_system.mod.descriptor_object)
            for category in self.file_system.mod.categories.values():
                for file in category.files.values():
                    save_routine(file)
        else:
            save_routine(self.file_system.open_file)
        self.main.load_file(self.file_system.open_file)