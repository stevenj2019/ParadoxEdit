from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App import AppController
    from App.Loading.Models import FileReference

from ParadoxParser.ParadoxNodes import GenericBlock
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QApplication, QMainWindow, QShortcut, QSplitter

from App.Contracts import PropagationRequest
from App.Contracts.Enums import ChangeState, PropagationType
from App.Enums import PDXMetadata
from App.GUI.Forms.Search import SearchForm
from App.GUI.Forms.Settings import SettingsForm
from App.GUI.Main.Contents import ContentsPanel
from App.GUI.Main.InlineEdit import InLineEditManager
from App.GUI.Main.ModPanel import ModPanel
from App.GUI.Menus.Topbar import Topbar
from App.GUI.Widgets.FileDialogues import (
    select_mod_file,
    workspace_save_selector,
    workspace_selector,
)
from App.GUI.Widgets.IconPreview import IconPreviewDialog
from App.GUI.Widgets.PopupModels import (
    could_not_load_mod_critical,
    file_is_unsupported,
    no_icon_available_warning,
)
from App.Loading.Models import UnloadedFile
from App.Loading.ParadoxSource import ParadoxSource
from App.Services import AppLogger


class MainWindow(QMainWindow):
    request_propagation = pyqtSignal(object)
    request_icon_preview = pyqtSignal(object)
    def __init__(self, app_controller:AppController) -> None:
        super().__init__()
        self.app_controller = app_controller
        self.editor_session = InLineEditManager(mutate_callback=self.app_controller.request_node_mutation)

        self.setWindowTitle("ParadoxEdit")
        self.showMaximized()

        self.topbar = Topbar(self.app_controller)
        self.addToolBar(self.topbar)
        self.topbar.request_load_mod.connect(self.load_mod_requested)
        self.topbar.request_load_vanilla.connect(self.app_controller.load_vanilla_files)
        self.topbar.request_load_workspace.connect(self.load_workspace)
        self.topbar.request_workspace_save.connect(self.save_workspace_as_file)
        self.topbar.request_settings_window.connect(self.settings_window_requested)

        self.splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(self.splitter)

        self.mod_panel = ModPanel(self.app_controller)
        self.mod_panel.setMinimumWidth(150)
        self.splitter.addWidget(self.mod_panel)
        self.mod_panel.request_load_block.connect(self.load_file)

        self.contents_panel = ContentsPanel(self.app_controller)
        self.contents_panel.setMinimumWidth(300)
        self.splitter.addWidget(self.contents_panel)
        self.contents_panel.script_view.edit_open_request.connect(self.editor_session.open_request)

        self.splitter.setSizes([200, 600])
        self.showMaximized()

        self.request_propagation.connect(self._propogate_mutations)
        self.request_icon_preview.connect(self._preview_icon)

        self.search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        self.search_shortcut.activated.connect(self.handle_search)

    def _propogate_mutations(self, request:PropagationRequest) -> None:
        type = request.type
        file = request.file
        node = request.node
        state = request.state
        def recurse(node):
            self.contents_panel.script_view.set_node_state(node, state)
            if isinstance(node, GenericBlock):
                for child in node.nodes:
                    recurse(child)
        match type:
            case PropagationType.NODE:
                self.mod_panel.set_file_state(file, ChangeState.MODIFIED)
                recurse(node)
            case PropagationType.FILE:
                self.mod_panel.set_file_state(file, state)
                if file is self.app_controller.file_system.open_file:
                    try:
                        for node in file.file.nodes:
                            recurse(node)
                    except AttributeError:
                        pass

    def handle_search(self) -> None:
        if self.app_controller.file_system.load_order.sources:
            widget = QApplication.focusWidget()
            while widget and widget is not self:
                if hasattr(widget, "search_window_requested"):
                    widget.search_window_requested()
                    return
                widget = widget.parent()
            self.search_window_requested()
    
    def settings_window_requested(self) -> None:
        settings = SettingsForm("PDXEdit Settings", self.app_controller)
        settings.exec_()

    def search_window_requested(self) -> None:
        self.search = SearchForm(self.app_controller)
        self.search.show()

    def load_mod_requested(self) -> None:
        path = select_mod_file(self)
        self.app_controller.add_mod_to_workspace(path)
     
    def load_workspace(self) -> None:
        path, exists = workspace_selector(self)
        if exists:
            self.app_controller.load_workspace(path)

    def load_mod(self, source:ParadoxSource) -> None:
        self.mod_panel.populate_tree(source)
        self.topbar._enable_actions()

    def load_workspace_failed(self, exc:Exception, tb:str) -> None:
        could_not_load_mod_critical(exc, tb)

    def save_workspace_as_file(self) -> None:
        file_path, exists = workspace_save_selector(self)
        if exists:
            self.app_controller.save_workspace(file_path)

    def load_file(self, file:FileReference) -> None:
        if isinstance(file.file, UnloadedFile):
            file_is_unsupported()
            AppLogger.warning(f"attemped to open {file.file.path}/{file.file.filename}, is unsupported.")
            return
        else:
            self.editor_session.cancel_request(reason="file switch")
            self.app_controller.file_system.load_file(file)
            self.contents_panel.load_file(file)

    def _preview_icon(self, icon:str) -> None:
        icon_name = icon.value
        icon_registry = self.app_controller.registry.get_metadata(PDXMetadata.GFXIcon)
        if icon_name in icon_registry.keys():
            full_path = icon_registry[icon]
        else:
            no_icon_available_warning(f"{icon} does not exist in Mod Metadata")
            return
        dialog = IconPreviewDialog(icon, full_path)
        dialog.exec()