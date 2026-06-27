from PyQt5.QtWidgets import QMainWindow, QSplitter
from PyQt5.QtCore import Qt, pyqtSignal

from ParadoxParser import ParadoxScriptParser as PDXScript
from ParadoxParser.ParadoxNodes import GenericNode, GenericKeyValue

from App.Enums import SaveTarget
from App.ModClasses.Categories import GenericCategory, GenericCategoryItem

# from App.GUI.Menus.TopBar import 
from App.GUI.Menus import TopBar
from App.GUI.Main.InlineEdit import InLineEditManager
from App.GUI.Main.Panels import ModPanel, ContentsPanel
from App.GUI.Dialogues.FileDialogues import select_mod_file
from App.GUI.Dialogues.PopupModels import could_not_load_mod_critical
from App.GUI.Windows.Settings import SettingsWindow

class MainWindow(QMainWindow):
    file_changed = pyqtSignal(object)
    # file_changed = pyqtSignal(object, object)
    node_changed = pyqtSignal(object)
    def __init__(self, app):
        super().__init__()
        self.app_controller = app
        self.editor_session = InLineEditManager(mutate_callback=self.app_controller.modify_node)

        #MainWindow
        self.setWindowTitle("ParadoxEdit")
        self.showMaximized()

        #TopBar
        self.topbar = TopBar(self)
        self.addToolBar(self.topbar)
        self.topbar.request_load_mod.connect(self.load_mod_requested)
        self.topbar.request_settings_window.connect(self.settings_window_requested)
        self.topbar.request_save_open_signal.connect(lambda:self.app_controller.save_target(SaveTarget.OPEN))
        self.topbar.request_save_all_signal.connect(lambda:self.app_controller.save_target(SaveTarget.ALL))
        
        #Splitter
        self.splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(self.splitter)

        #ModPanel(left)
        self.mod_panel = ModPanel(self)
        self.mod_panel.setMinimumWidth(150)
        self.splitter.addWidget(self.mod_panel)
        self.mod_panel.request_load_block.connect(self._load_file)
        # self.mod_panel.request_bulkable_operation.connect(self._apply_bulkable_operation)
        
        #ContentsPanel
        self.contents_panel = ContentsPanel(self)
        self.contents_panel.setMinimumWidth(300)
        self.splitter.addWidget(self.contents_panel)
        self.contents_panel.edit_open_request.connect(self.editor_session.open_request)

        self.splitter.setSizes([200, 600])
        self.showMaximized()
        if not self.app_controller.config.initialised:
            self.settings_window_requested()
    
    def propogate_changes(self,
                          file:PDXScript, 
                          node:GenericNode|GenericKeyValue #unsure which is it tbh
    ):
        self.mod_panel.set_file_dirty(file)
        self.contents_panel.refresh_node(node)

    def propogate_save(self, file):
        self.mod_panel.set_file_clean(file)
        if self.app_controller.file_system.open_file == file:
            self.contents_panel.set_file_clean(file)

    def settings_window_requested(self):
        title = "PDXEdit Setup" if self.app_controller.config.initialised else "PDXEdit Settings"
        settings = SettingsWindow(title, self)
        settings.exec_()

    def load_mod_requested(self):
        path = select_mod_file(self)
        self.app_controller.load_mod(path)

    def load_mod_to_gui(self, mod):
        # self.mod = mod
        self.mod_panel._populate_tree(mod)
        self._load_file(mod.descriptor_object)
        self.topbar._enable_actions()

    def load_mod_failed(self, exc):
        could_not_load_mod_critical(exc)

    # def _apply_bulkable_operation(self, action, target):
    #     if bulk_operation_warning(self):
    #         for file in target.iter_files():
    #             action(file)
    #             file.has_been_modified = True
    #     self._refresh_contents()

    def _load_file(self, file):
        self.editor_session.cancel_request(reason="file switch")
        self.app_controller.file_system.load_file(file)
        # self.contents_panel._load_block(file.obj)
        self.contents_panel._load_block(file)

    def _refresh_contents(self):
        open_file = self.mod_panel.open_file
        
        if open_file:
            self._load_file(open_file)

    #TODO delegate these to FileSystemManager in AppController, at some point
    def _save_files(self, modified_only:bool=True):
        for file in self.mod.iter_file():
            if modified_only and not file.has_been_modified:
                continue
            self._save_file(file)
    
    def _save_file(self, file):
        if self.config.safe_mode:
            file._backup_file()
            # file.obj._backup_file()
        file._to_pdx_file()
        # file.obj._to_pdx_file()
