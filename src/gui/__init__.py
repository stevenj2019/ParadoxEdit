from editor_session import InlineEditSession

from PyQt5.QtWidgets import QApplication, QMainWindow, QSplitter
from PyQt5.QtCore import Qt, pyqtSignal, QEvent
from PyQt5.Qt import QMenu
from PyQt5.QtGui import QCursor

from gui.menus.top_bar import MainTopBar
from gui.panels import ModPanel, ContentsPanel
from gui.dialogues.warning_messages import toggle_safe_mode_warning, bulk_operation_warning
from gui.util import get_safe_mode_opposed_text, toggle_dark_mode, add_menu_heading
from gui.constants import NODE, IS_BLOCK

class MainWindow(QMainWindow):
    request_global_cancel_edit = pyqtSignal()
    def __init__(self, config):
        super().__init__()
        self.mod = None
        self.config = config
        self.edit_session = InlineEditSession()
        self.safe_mode:bool = config.safe_mode
        self.bulk_warning_shown:bool = False

        self.setWindowTitle("ParadoxEdit")

        #TopBar
        self.topbar = MainTopBar(self)
        self.addToolBar(self.topbar)


        #Splitter
        self.splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(self.splitter)

        #ModPanel(left)
        self.mod_panel = ModPanel()
        self.mod_panel.setMinimumWidth(150)
        self.mod_panel.request_context_menu.connect(self.show_context_menu)
        self.splitter.addWidget(self.mod_panel)
        #ContentsPanel
        self.contents_panel = ContentsPanel()
        self.contents_panel.setMinimumWidth(300)
        self.contents_panel.request_context_menu.connect(self.contents_panel.populate_context_menu)
        self.splitter.addWidget(self.contents_panel)

        #Signal Connections
        self.request_global_cancel_edit.connect(self.contents_panel._close_editor)

        self.topbar.mod_loaded_signal.connect(self._load_mod_to_gui)
        # self.mod_panel.request_load_block.connect(self.contents_panel._load_block)
        self.mod_panel.request_load_block.connect(self._load_file)
        self.contents_panel.request_context_menu.connect(self.contents_panel.populate_context_menu)
        self.mod_panel.request_bulkable_operation.connect(self._apply_bulkable_operation)
        self.topbar.save_open_signal.connect(lambda:self._save_file(self.mod_panel.open_file))
        self.topbar.save_all_changed_signal.connect(lambda:self._save_files(True))
        self.topbar.save_all_signal.connect(lambda:self._save_files(False))
        
        self.splitter.setSizes([200, 600])
        self.showMaximized()
        QApplication.instance().installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() in (
            QEvent.MouseButtonPress, 
            QEvent.MouseButtonDblClick, 
            QEvent.KeyPress,
        ):
            self.request_global_cancel_edit.emit()
        return super().eventFilter(obj, event)
    def show_context_menu(self, panel, selected):
        menu = QMenu(self)
        panel.populate_context_menu(menu, self, selected)
        menu.exec_(QCursor.pos())

    def _load_mod_to_gui(self, mod):
        self.mod = mod
        self.mod_panel._populate_tree(mod)
        self.mod_panel.open_file
        self.contents_panel._load_block(mod.descriptor_object)
        self.topbar._enable_actions()

    def _apply_bulkable_operation(self, action, target):
        if bulk_operation_warning(self):
            for file in target.iter_files():
                action(file)
                file.has_been_modified = True
        self._refresh_contents()

    def _load_file(self, file):
        self.edit_session.cancel(reason="file_switch")
        self.contents_panel._load_block(file.obj)

    def _refresh_contents(self):
        open_file = self.mod_panel.open_file
        
        if open_file:
            self._load_file(open_file)
            # node = self.mod_panel.open_file.data(0, NODE)
            # self.contents_panel._load_block(node)

    def _on_inline_edit_request(self, node, widget):
        self.edit_session.start(node, widget)

    def _on_global_interaction(self, reason=None):
        if not hasattr(self, "edit_session"):
            return
        self.edit_session.cancel(reason)

    def _save_files(self, modified_only:bool=True):
        for file in self.mod.iter_file():
            if modified_only and not file.has_been_modified:
                continue
            self._save_file(file)
    
    def _save_file(self, file):
        if self.config.safe_mode:
            file.obj._backup_file()
        file.obj._to_pdx_file()
