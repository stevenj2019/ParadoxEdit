import qdarktheme
from contextlib import contextmanager
import traceback
import copy

from PyQt5.QtCore import QObject, pyqtSignal, QThread
from PyQt5.QtWidgets import QApplication

from App.Loading import LoadingDialog, LoadProcess
from App.Loading.Directories.Base import GenericDirectoryContext
from App.Services import ConfigurationManager, AppLogger, StyleManager, FilesystemMananger, ParadoxRegistry, Workspace
from App.GUI.Main import MainWindow
from App.Contracts import PropagationRequest, NodeMutationRequest, BlockMutationRequest, BulkMutationRequest
from App.Contracts.Enums import SaveTarget, PropagationType, ChangeState

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
        self.registry      = ParadoxRegistry()
        AppLogger.initialise()

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

    def load_vanilla_files(self):
        workspace_candidate = copy.deepcopy(self.file_system.workspace)
        workspace_candidate.set_vanilla_status(True)

        self.reload_workspace(workspace_candidate)

    def add_mod_to_workspace(self, path):
        workspace_candidate = copy.deepcopy(self.file_system.workspace)
        workspace_candidate.add_mod_to_workspace(path)

        self.reload_workspace(workspace_candidate)

    def load_workspace(self, path):
        workspace_candidate = Workspace()
        workspace_candidate.read_file(path)

        self.reload_workspace(workspace_candidate)

    def reload_workspace(self, workspace):
        self.loading_screen = LoadingDialog()

        self.thread = QThread()
        self.loading_process = LoadProcess(workspace, self.configuration.game_install_path)
        
        self.loading_process.moveToThread(self.thread)
        self.thread.started.connect(self.loading_process.run)
        self.loading_process.progress.connect(self.loading_screen.update_message)
        self.loading_process.finished.connect(self.workspace_loaded)
        self.loading_process.failed.connect(self.workspace_load_failed)
        self.loading_screen.show()
        self.thread.start()

    def workspace_loaded(self, result):
        self.registry.load_tokens(result.tokens)
        
        self.file_system.load_workspace(result.workspace)
        
        self.main.load_mod(result.load_order)
        
        self.loading_screen.close()
        self.thread.quit()
        self.thread.wait()

    def workspace_load_failed(self, error):
        print(traceback.format_exc())
        self.loading_screen.close()
        self.main.load_workspace_failed(error)
        self.thread.quit()
        self.thread.wait()

    def save_workspace(self, file_path):
        self.file_system.workspace.write_file(file_path)

    def _refresh_file(self):
        for file in self._batch_file:
            if file is self.file_system.open_file.file:
                self.main.load_file(self.file_system.open_file)
        self._batch_file.clear()

    @contextmanager
    def batch_manager(self):
        self._batch_depth += 1
        try:
            yield
        finally:
            self._batch_depth -= 1
            if self._batch_depth == 0:
                self._refresh_file()

    def _request_node_mutation(self, request:NodeMutationRequest):
        file = request.file if request.file else self.file_system.open_file.file
        node = request.node
        node_value = request.node_value
        value = request.value
        if node_value.value != value:
            node_value.value = value
            self.file_system.changed_file(file, node, ChangeState.MODIFIED)
            self.main.request_propagation.emit(PropagationRequest(type=PropagationType.NODE,
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
        self.main.request_propagation.emit(PropagationRequest(type=PropagationType.NODE, 
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
        if isinstance(target, GenericDirectoryContext):
            files = target.iter_files()
        else:
            files = [target]

        for file in files:
            action(file, self)
            self.main.request_propagation.emit(PropagationRequest(type=PropagationType.FILE,
                                                                  file=file,
                                                                  node=None,
                                                                  state=ChangeState.MODIFIED))
        if self.file_system.open_file.file in files:
            self.main.load_file(self.file_system.open_file)

    def _save_target(self, target):
        def save_routine(file):
            saved = self.file_system.save_file(file)
            if saved:
                self.main.request_propagation.emit(PropagationRequest(type=PropagationType.FILE, 
                                                                      file=file,
                                                                      node=None,
                                                                      state=None
                                                                      ))

        if target is SaveTarget.ALL:
            save_routine(self.file_system.mod.descriptor_object)
            for category in self.file_system.mod.categories.values():
                for file in category.files.values():
                    save_routine(file)
        else:
            save_routine(self.file_system.open_file.file)
        self.main.load_file(self.file_system.open_file)
