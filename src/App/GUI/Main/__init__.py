from PyQt5.QtWidgets import QMainWindow, QSplitter
from PyQt5.QtCore import Qt, pyqtSignal

from ParadoxParser import ParadoxScriptParser as PDXScript
from ParadoxParser.ParadoxNodes import GenericBlock

from App.Enums import SaveTarget

# from App.GUI.Menus.TopBar import 
from App.Contracts import PropagationRequest
from App.Enums import PropagationType, ChangeState
from App.GUI.Menus import TopBar
from App.GUI.Main.InlineEdit import InLineEditManager
from App.GUI.Main.Panels import ModPanel, ContentsPanel
from App.GUI.Dialogues.FileDialogues import select_mod_file
from App.GUI.Dialogues.PopupModels import could_not_load_mod_critical
from App.GUI.Windows.Settings import SettingsWindow

class MainWindow(QMainWindow):
    propagation_request = pyqtSignal(object)
    # node_changed = pyqtSignal(object)
    def __init__(self, app):
        super().__init__()
        self.app_controller = app
        self.editor_session = InLineEditManager(mutate_callback=self.app_controller.request_node_mutation)

        #MainWindow
        self.setWindowTitle("ParadoxEdit")
        self.showMaximized()

        #TopBar
        self.topbar = TopBar(self, app)
        self.addToolBar(self.topbar)
        self.topbar.request_load_mod.connect(self.load_mod_requested)
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
        if not self.app_controller.configuration.initialised:
            self.settings_window_requested()

        self.propagation_request.connect(self._propogate_mutations)
    
    def _propogate_mutations(self, request:PropagationRequest):
        type = request.type
        file = request.file
        node = request.node #this may be None
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
            case _:
                print("ERROR")

    def settings_window_requested(self):
        title = "PDXEdit Setup" if self.app_controller.configuration.initialised else "PDXEdit Settings"
        settings = SettingsWindow(title, self)
        settings.exec_()

    def load_mod_requested(self):
        path = select_mod_file(self)
        self.app_controller.load_mod(path)

    def load_mod_to_gui(self, mod):
        # self.mod = mod
        self.mod_panel._populate_tree(mod)
        self.load_file(mod.descriptor_object)
        self.topbar._enable_actions()

    def load_mod_failed(self, exc):
        could_not_load_mod_critical(exc)

    # def _apply_bulkable_operation(self, action, target):
    #     if bulk_operation_warning(self):
    #         for file in target.iter_files():
    #             action(file)
    #             file.has_been_modified = True
    #     self._refresh_contents()

    def load_file(self, file):
        self.editor_session.cancel_request(reason="file switch")
        self.app_controller.file_system.load_file(file)
        self.contents_panel.load_block(file)

    def _refresh_contents(self):
        open_file = self.mod_panel.open_file
        if open_file:
            self.load_file(open_file)


