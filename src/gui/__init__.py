from PyQt5.QtWidgets import QApplication, QMainWindow, QSplitter
from PyQt5.QtCore import Qt, pyqtSignal, QEvent
from PyQt5.Qt import QMenu
from PyQt5.QtGui import QCursor

from gui.menus.top_bar import MainTopBar
from gui.panels import ModPanel, ContentsPanel
from gui.InlineEditor import InlineEditManager
from gui.dialogues.warning_messages import bulk_operation_warning

class MainWindow(QMainWindow):
    global_edit_cancel_request = pyqtSignal(str)
    def __init__(self, config):
        super().__init__()
        self.mod = None
        self.config = config
        self.editor_session = InlineEditManager(self)
        self.safe_mode:bool = config.safe_mode
        self.bulk_warning_shown:bool = False

        #MainWindow
        self.setWindowTitle("ParadoxEdit")
        QApplication.instance().installEventFilter(self)
        self.global_edit_cancel_request.connect(self.editor_session.cancel_request)
        
        #TopBar
        self.topbar = MainTopBar(self)
        self.addToolBar(self.topbar)
        self.topbar.mod_loaded_signal.connect(self._load_mod_to_gui)
        self.topbar.save_open_signal.connect(lambda:self._save_file(self.mod_panel.open_file))
        self.topbar.save_all_changed_signal.connect(lambda:self._save_files(True))
        self.topbar.save_all_signal.connect(lambda:self._save_files(False))
        
        #Splitter
        self.splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(self.splitter)
        
        #ModPanel(left)
        self.mod_panel = ModPanel()
        self.mod_panel.setMinimumWidth(150)
        self.splitter.addWidget(self.mod_panel)
        self.mod_panel.request_load_block.connect(self._load_file)
        self.mod_panel.request_bulkable_operation.connect(self._apply_bulkable_operation)
        
        #ContentsPanel
        self.contents_panel = ContentsPanel()
        self.contents_panel.setMinimumWidth(300)
        self.splitter.addWidget(self.contents_panel)
        self.contents_panel.edit_open_request.connect(self.editor_session.open_request)

        self.splitter.setSizes([200, 600])
        self.showMaximized()

    def eventFilter(self, obj, event):
        def _focus_inside_editor():
            editor = self.editor_session.editor
            if editor is None:
                return False
            widget = QApplication.focusWidget()
            while widget is not None:
                if widget is editor:
                    return True
                widget = widget.parent()

            return False
        
        if event.type() in (
            QEvent.MouseButtonPress, 
            QEvent.MouseButtonDblClick
        ):
            if _focus_inside_editor():
                return super().eventFilter(obj, event)
            
            self.global_edit_cancel_request.emit("global click-away")
        
        return super().eventFilter(obj, event)
    
    def show_context_menu(self, panel, selected):
        menu = QMenu(self)
        panel.populate_context_menu(menu, self, selected)
        menu.exec_(QCursor.pos())

    def _load_mod_to_gui(self, mod):
        self.mod = mod
        self.mod_panel._populate_tree(mod)
        self._load_file(mod.descriptor_object)
        self.topbar._enable_actions()

    def _apply_bulkable_operation(self, action, target):
        if bulk_operation_warning(self):
            for file in target.iter_files():
                action(file)
                file.has_been_modified = True
        self._refresh_contents()

    def _load_file(self, file):
        self.editor_session.cancel_request(reason="file switch")
        self.contents_panel._load_block(file.obj)

    def _refresh_contents(self):
        open_file = self.mod_panel.open_file
        
        if open_file:
            self._load_file(open_file)

    def _mutate_node(self, node, value):
        node.value = value
        self.mod_panel.open_file.has_been_modified = True

    def _save_files(self, modified_only:bool=True):
        for file in self.mod.iter_file():
            if modified_only and not file.has_been_modified:
                continue
            self._save_file(file)
    
    def _save_file(self, file):
        if self.config.safe_mode:
            file.obj._backup_file()
        file.obj._to_pdx_file()
