from PyQt5.QtWidgets import QMainWindow, QSplitter
from PyQt5.QtCore import Qt, pyqtSignal

from ParadoxParser.ParadoxNodes import GenericNode, GenericKeyValue
from App.ModClasses.Categories import GenericCategory, GenericCategoryItem
from App.GUI.Menus.TopBar import TopBar
from App.GUI.Panels import ModPanel, ContentsPanel
from App.GUI.Dialogues.FileDialogues import select_mod_file
from App.GUI.Dialogues.PopupModels import could_not_load_mod_critical
from App.GUI.Windows.Settings import SettingsWindow

class MainWindow(QMainWindow):
    node_changed = pyqtSignal(object)
    def __init__(self, app):
        super().__init__()
        self.app_controller = app

        #MainWindow
        self.setWindowTitle("ParadoxEdit")
        self.showMaximized()

        #TopBar
        self.topbar = TopBar(self)
        self.addToolBar(self.topbar)
        self.topbar.request_load_mod.connect(self.load_mod_requested)
        self.topbar.request_settings_window.connect(self.settings_window_requested)
        self.topbar.request_save_open_signal.connect(lambda:self._save_file(self.mod_panel.open_file))
        self.topbar.request_save_all_changed_signal.connect(lambda:self._save_files(True))
        self.topbar.request_save_all_signal.connect(lambda:self._save_files(False))
        
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
        self.contents_panel.edit_open_request.connect(self.app_controller.editor_session.open_request)

        self.splitter.setSizes([200, 600])
        self.showMaximized()
    
    def propogate_changes(self, 
                          category:GenericCategory, 
                          category_item:GenericCategoryItem, 
                          node:GenericNode|GenericKeyValue #unsure which is it tbh
    ):
        self.node_changed.emit(node)

    def settings_window_requested(self):
        title = "PDXEdit Setup" if self.app_controller.config.initalised else "PDXEdit Settings"
        settings = SettingsWindow(title, self.app_controller.config)
        settings.exec_()

    def load_mod_requested(self):
        path = select_mod_file(config=self.app_controller.config)
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
        self.app_controller.editor_session.cancel_request(reason="file switch")
        self.contents_panel._load_block(file.obj)

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
            file.obj._backup_file()
        file.obj._to_pdx_file()
