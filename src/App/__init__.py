import qdarktheme
from contextlib import contextmanager

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QApplication

from ParadoxParser.ParadoxNodes import GenericBlock

from App.ModClasses.Categories import GenericCategory
from App.Services import ConfigurationManager, StyleManager, FilesystemMananger
from App.GUI.Main import MainWindow

from App.Enums import SaveTarget, PropagationType, ChangeState
from App.Contracts import OpenFile, PropagationRequest, NodeMutationRequest, BlockMutationRequest, BulkMutationRequest
from App.Contexts.FileContexts import ParadoxFileContext

class AppController(QObject):
    request_node_mutation = pyqtSignal(object)
    request_block_mutation = pyqtSignal(object)
    request_bulk_mutation = pyqtSignal(object)
    request_save = pyqtSignal(object)
    def __init__(self):
        super().__init__()
        self.app           = QApplication([])

        self.configuration = ConfigurationManager()
        self.file_system   = FilesystemMananger(self.configuration)
        self.style_manager = StyleManager(self.configuration)

        self.main = MainWindow(self)

        self._batch_depth = 0
        self._batch_file = set()

        self.run()

    def run(self):
        self.app.setStyleSheet(qdarktheme.load_stylesheet("dark" if self.configuration.dark_mode else "light"))
        self.request_node_mutation.connect(self._request_node_mutation)
        self.request_block_mutation.connect(self._request_block_mutation)
        self.request_bulk_mutation.connect(self._request_bulk_mutation)
        self.request_save.connect(self._save_target)
        self.main.show()
        self.app.exec_()

    def load_mod(self, path):
        try:
            self.file_system.load_mod(path)
        except Exception as e:
            self.main.load_mod_failed(e)
            return 
        self.file_system.load_file(OpenFile(self.file_system.mod.descriptor_object, ParadoxFileContext))
        self.main.load_mod(self.file_system.mod)
        self.main.load_file(self.file_system.open_file)

    @contextmanager
    def batch_manager(self):
        self._batch_depth += 1
        try:
            yield
        finally:
            self._batch_depth -= 1
            if self._batch_depth == 0:
                self._refresh_file()

    def _refresh_file(self):
        for file in self._batch_file:
            if file is self.file_system.open_file.file:
                self.main.load_file(self.file_system.open_file)
        self._batch_file.clear()

    def _request_node_mutation(self, request:NodeMutationRequest):
        file = request.file if request.file else self.file_system.open_file.file
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
        file   = request.file if request.file else self.file_system.open_file.file
        parent = request.parent
        index  = request.index
        payload  = request.payload
        state  = request.state

        #ADDED - mutate (DELETE just marks item for deletion)
        if state == ChangeState.ADDED:
            node = payload() if callable(payload) else payload
            parent.nodes.insert(index, node)
        else:
            node = parent.nodes[index]

        self.file_system.changed_file(file, node, state)
        self.main.propagation_request.emit(PropagationRequest(type=PropagationType.NODE, 
                                                       file=file,
                                                       node=node,
                                                       state=state))
        #refreshes file when batch is complete
        self._batch_file.add(file)
        if self._batch_depth ==0:
            self._refresh_file()

    def _request_bulk_mutation(self, request:BulkMutationRequest):
        target = request.target
        action = request.action
        if isinstance(target, GenericCategory):
            file_list = [f for f in target.files.values()]
        else:
            file_list = [target]

        for file in file_list:
            action(file, self)
            self.main.propagation_request.emit(PropagationRequest(type=PropagationType.FILE,
                                                                  file=file,
                                                                  node=None,
                                                                  state=ChangeState.MODIFIED))
        if self.file_system.open_file.file in file_list:
            self.main.load_file(self.file_system.open_file)

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
            save_routine(self.file_system.open_file.file)
        self.main.load_file(self.file_system.open_file)