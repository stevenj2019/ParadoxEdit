from PyQt5.QtWidgets import QMainWindow, QSplitter
from PyQt5.QtCore import Qt, pyqtSignal

from ParadoxParser.ParadoxNodes import GenericBlock

from App.Enums import PDXMetadata
from App.Services import AppLogger
from App.Contracts import PropagationRequest
from App.Contracts.Enums import PropagationType, ChangeState
from App.GUI.Menus.Topbar import Topbar
from App.GUI.Main.InlineEdit import InLineEditManager
from App.GUI.Main.ModPanel import ModPanel
from App.GUI.Main.ContentsPanel import ContentsPanel

from App.GUI.Widgets.IconPreview import IconPreviewDialog
from App.GUI.Widgets.FileDialogues import select_mod_file, workspace_selector, workspace_save_selector
from App.GUI.Widgets.PopupModels import could_not_load_mod_critical, no_icon_available_warning, file_is_unsupported
from App.GUI.Forms.Settings import SettingsForm

from App.Loading.Models import UnloadedFile
class MainWindow(QMainWindow):
    request_propagation = pyqtSignal(object)
    request_icon_preview = pyqtSignal(object)
    def __init__(self, app):
        super().__init__()
        self.app_controller = app
        self.editor_session = InLineEditManager(mutate_callback=self.app_controller.request_node_mutation)

        #MainWindow
        self.setWindowTitle("ParadoxEdit")
        self.showMaximized()

        #TopBar
        self.topbar = Topbar(self, app)
        self.addToolBar(self.topbar)
        self.topbar.request_load_mod.connect(self.load_mod_requested)
        self.topbar.request_load_vanilla.connect(self.app_controller.load_vanilla_files)
        self.topbar.request_load_workspace.connect(self.load_workspace)
        self.topbar.request_workspace_save.connect(self.save_workspace_as_file)
        self.topbar.request_settings_window.connect(self.settings_window_requested)
        #Splitter
        self.splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(self.splitter)

        #ModPanel(left)
        self.mod_panel = ModPanel(self, app)
        self.mod_panel.setMinimumWidth(150)
        self.splitter.addWidget(self.mod_panel)
        self.mod_panel.request_load_block.connect(self.load_file)

        #ContentsPanel
        self.contents_panel = ContentsPanel(self, app)
        self.contents_panel.setMinimumWidth(300)
        self.splitter.addWidget(self.contents_panel)
        self.contents_panel.edit_open_request.connect(self.editor_session.open_request)

        self.splitter.setSizes([200, 600])
        self.showMaximized()
        # if not self.app_controller.configuration.initialised:
        #     self.settings_window_requested()

        self.request_propagation.connect(self._propogate_mutations)
        self.request_icon_preview.connect(self._preview_icon)

    def _propogate_mutations(self, request:PropagationRequest):
        type = request.type
        file = request.file.file
        node = request.node
        state = request.state
        def recurse(node):
            self.contents_panel.set_node_state(node, state)
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
                    for node in file.nodes:
                        recurse(node)

    def settings_window_requested(self):
        title = "PDXEdit Setup" if self.app_controller.configuration.initialised else "PDXEdit Settings"
        settings = SettingsForm(title, self.app_controller)
        settings.exec_()

    def load_mod_requested(self):
        path = select_mod_file(self)
        self.app_controller.add_mod_to_workspace(path)
     
    def load_workspace(self):
        path = workspace_selector(self)
        self.app_controller.load_workspace(path)
    
    def load_mod(self, mod):
        self.mod_panel.populate_tree(mod)
        self.topbar._enable_actions()

    def load_workspace_failed(self, exc, tb):
        could_not_load_mod_critical(exc, tb)

    def save_workspace_as_file(self):
        file_path = workspace_save_selector(self)
        self.app_controller.save_workspace(file_path)

    def load_file(self, file):
        if isinstance(file.file, UnloadedFile):
            file_is_unsupported()
            AppLogger.warning(f"attemped to open {file.file.path}/{file.file.filename}, is unsupported.")
            return
        self.editor_session.cancel_request(reason="file switch")
        self.app_controller.file_system.load_file(file)
        self.contents_panel.load_block(file)

    def _preview_icon(self, icon):
        icon_name = icon.value
        icon_registry = self.app_controller.registry.get_metadata(PDXMetadata.GFXIcon)
        if icon_name in icon_registry.keys():
            full_path = icon_registry[icon_name]
        else:
            no_icon_available_warning(f"{icon} does not exist in Mod Metadata")
            return
        # if icon:
        # mod = self.app_controller.registry.mod
        # category_metadata = self.app_controller.registry.get_category_metadata(PDXMetadata.GFXIcon)
        # icon_relative_path = category_metadata[icon]
        # if not icon_relative_path:
        #     no_icon_available_warning(f"{icon} does not exist in Mod Metadata")
        #     return
        # full_path = mod._resolve_path(icon_relative_path)
        dialog = IconPreviewDialog(icon, full_path)
        dialog.exec()