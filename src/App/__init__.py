import copy
import sys
import traceback
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from types import TracebackType
from typing import Type

import qdarktheme
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QDialog

from App.AppLogger import AppLogger
from App.Contracts import (
    BlockMutationRequest,
    BulkMutationRequest,
    FileMutationRequest,
    ModLoaderResult,
    NodeMutationRequest,
    PropagationRequest,
)
from App.Contracts.Enums import ChangeState, PropagationType, SaveTarget, TargetProperty
from App.GUI.Forms.Settings import SettingsForm
from App.GUI.Main import MainWindow
from App.GUI.StyleManager import StyleManager
from App.GUI.Widgets.PopupModels import setup_process_cancelled, unhandled_exception_popup
from App.Loading import LoadingDialog, LoadProcess
from App.Loading.Directories.Base import GenericDirectory
from App.Loading.Models import FileReference
from App.Loading.ParadoxSource import ParadoxMod, ParadoxSource
from App.Services import (
    ConfigurationManager,
    FilesystemMananger,
    ParadoxRegistry,
    Workspace,
)


class AppController(QObject):
    request_node_mutation = pyqtSignal(object)
    request_block_mutation = pyqtSignal(object)
    request_bulk_mutation = pyqtSignal(object)
    request_file_mutation = pyqtSignal(object)
    request_file_unload = pyqtSignal(object)
    request_registry_refresh = pyqtSignal()
    request_save = pyqtSignal(object)

    def __init__(self) -> None:
        super().__init__()
        AppLogger.initialise()
        AppLogger.application_metadata_logger()
        AppLogger.runtime_metadata_logger()
        sys.excepthook = self.global_exception_handler
        self.app = QApplication(sys.argv)

        self.configuration = ConfigurationManager()
        self.file_system = FilesystemMananger(self.configuration)
        self.style_manager = StyleManager(self.configuration)
        self.registry = ParadoxRegistry()

        self.main = MainWindow(self)

        if not self.configuration.initialised:
            settings = SettingsForm("PDXEdit Setup", self)
            result = settings.exec_()
            if result != QDialog.Accepted:
                AppLogger.error("Setup workflow cancelled.")
                setup_process_cancelled(self.main)
                sys.exit()

        self._batch_depth = 0
        self._batch_file = set()

        self.run()

    def global_exception_handler(
        self,
        exc_type: Type[BaseException],
        exc_value: BaseException,
        exc_traceback: TracebackType,
    ) -> None:
        if exc_type is KeyboardInterrupt:
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        error = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))

        AppLogger.error(f"Unhandled exception:\n{error}")
        unhandled_exception_popup(self.main, exc_value, error)

    def run(self) -> None:
        self.app.setStyleSheet(
            qdarktheme.load_stylesheet(
                "dark" if self.configuration.dark_mode else "light"
            )
        )
        self.request_node_mutation.connect(self._request_node_mutation)
        self.request_block_mutation.connect(self._request_block_mutation)
        self.request_bulk_mutation.connect(self._request_bulk_mutation)
        self.request_file_mutation.connect(self._request_file_mutation)
        self.request_file_unload.connect(self._request_file_unload)
        self.request_registry_refresh.connect(self._request_registry_rebuild)
        self.request_save.connect(self._save_target)
        self.main.show()

        self.app.exec_()

    def load_vanilla_files(self) -> None:
        workspace_candidate = copy.deepcopy(self.file_system.workspace)
        workspace_candidate.set_vanilla_status(True)

        self.reload_workspace(workspace_candidate)

    def add_mod_to_workspace(self, path: Path) -> None:
        workspace_candidate = copy.deepcopy(self.file_system.workspace)
        workspace_candidate.add_mod_to_workspace(path)

        self.reload_workspace(workspace_candidate)

    def load_workspace(self, path: Path) -> None:
        workspace_candidate = Workspace()
        workspace_candidate.read_file(path)

        self.reload_workspace(workspace_candidate)

    def reload_workspace(self, workspace: Workspace) -> None:
        self.loading_screen = LoadingDialog()

        self.thread = QThread()
        self.loading_process = LoadProcess(
            workspace, self.registry, self.configuration.game_install_path
        )

        self.loading_process.moveToThread(self.thread)
        self.thread.started.connect(self.loading_process.run)
        self.loading_process.progress_message.connect(
            self.loading_screen.update_message
        )
        self.loading_process.progress_bar_start.connect(
            self.loading_screen.start_progress_bar
        )
        self.loading_process.progress_bar_update.connect(
            self.loading_screen.update_progress_bar
        )
        self.loading_process.progress_bar_end.connect(
            self.loading_screen.end_progress_bar
        )
        self.loading_process.finished.connect(self.workspace_loaded)
        self.loading_process.failed.connect(self.workspace_load_failed)
        self.loading_screen.show()
        self.thread.start()

    def workspace_loaded(self, result: ModLoaderResult) -> None:
        self.file_system.load_workspace(result.workspace, result.load_order)
        self.main.load_mod(result.load_order)
        AppLogger.workspace_metadata_logger(result.workspace, result.load_order)
        self.loading_screen.close()
        self.thread.quit()
        self.thread.wait()

    def workspace_load_failed(self, error: Exception, traceback: str) -> None:
        self.loading_screen.close()
        self.main.load_workspace_failed(error, traceback)
        self.thread.quit()
        self.thread.wait()

    def save_workspace(self, file_path: Path) -> None:
        self.file_system.workspace.write_file(file_path)

    def _refresh_file(self) -> None:
        for file in self._batch_file:
            if file is self.file_system.open_file:
                self.main.load_file(self.file_system.open_file)
        self._batch_file.clear()

    @contextmanager
    def batch_manager(self)-> Generator[None, None, None]:
        self._batch_depth += 1
        try:
            yield
        finally:
            self._batch_depth -= 1
            if self._batch_depth == 0:
                self._refresh_file()

    def _request_node_mutation(self, request: NodeMutationRequest) -> None:
        file = request.file if request.file else self.file_system.open_file
        node = request.node
        target = request.target
        value = request.value
        changed = False
        if target is TargetProperty.KEY:
            if node.key != value:
                old_value = node.key
                node.key = value
                changed = True

        elif target is TargetProperty.VALUE:
            if node.value != value:
                old_value = node.value
                node.value = value
                changed = True

        if changed:
            AppLogger.info(f"{old_value} to {value}")
            self.file_system.changed_file(file.file, node, ChangeState.MODIFIED)
            self.main.request_propagation.emit(
                PropagationRequest(
                    type=PropagationType.NODE,
                    file=file,
                    node=node,
                    state=ChangeState.MODIFIED,
                )
            )

    def _request_block_mutation(self, request: BlockMutationRequest) -> None:
        file = request.file if request.file else self.file_system.open_file
        parent = request.parent
        index = request.index
        payload = request.payload
        state = request.state

        if state == ChangeState.ADDED:
            node = payload() if callable(payload) else payload
            parent.nodes.insert(index, node)
        else:
            node = parent.nodes[index]
        self.file_system.changed_file(file, node, state)
        self.main.request_propagation.emit(
            PropagationRequest(
                type=PropagationType.NODE, file=file, node=node, state=state
            )
        )
        self._batch_file.add(file)
        if self._batch_depth == 0:
            self._refresh_file()

    def _request_bulk_mutation(self, request: BulkMutationRequest) -> None:
        target = request.target
        action = request.action
        if isinstance(target, (ParadoxSource, GenericDirectory)):
            files = target.iter_files()
        else:
            files = [target]

        for file in files:
            action(file, self)
            self.main.request_propagation.emit(
                PropagationRequest(
                    type=PropagationType.FILE,
                    file=file,
                    node=None,
                    state=ChangeState.MODIFIED,
                )
            )
        if self.file_system.open_file.file in files:
            self.main.load_file(self.file_system.open_file)

    def _request_file_mutation(self, request: FileMutationRequest) -> None:
        print("MUTATION HANDLER CALLED", id(request.file))
        file = request.file
        if request.state == ChangeState.ADDED:
            request.directory.add_file(file.file.filepath, file.file.filename, file)
            self.registry.load_file_data(file.directory.source, file)
        self.file_system.change_tracker.set_file_state(request.file, request.state)
        self.main.mod_panel.add_file(request.directory, request.file)
        self.main.mod_panel.set_file_state(request.file, request.state)

    def _request_file_unload(self, file:FileReference) -> None:
        #if tree loaded, clear
        if self.file_system.open_file is file:
            self.main.contents_panel.script_view.unload_block()
        #remove item from file tree
        self.main.mod_panel.remove_file(file)
        #delete reference in source tree
        file.directory.delete_file(file)
        self.file_system.change_tracker.clear_file_state(file)
        self.registry.purge_file_data(file)

    def _request_registry_rebuild(self) -> None:
        self.registry._build_registry_cache()

    def _save_target(self, target: SaveTarget) -> None:
        def save_routine(file: FileReference) -> None:
            saved = self.file_system.save_file(file)
            if saved:
                self.main.request_propagation.emit(
                    PropagationRequest(
                        type=PropagationType.FILE, file=file, node=None, state=None
                    )
                )

        if target is SaveTarget.ALL:
            for source in self.file_system.load_order.sources:
                if isinstance(source, ParadoxMod):
                    save_routine(source.descriptor_object)
                    for file in source.root.iter_files():
                        save_routine(file)
        else:
            save_routine(self.file_system.open_file)
        if self.file_system.open_file is not None:
            self.main.load_file(self.file_system.open_file)
