from PyQt5.QtWidgets import QToolBar, QMenu, QAction
from PyQt5.QtCore import pyqtSignal

from gui.menus.top_bar.actions import build_topbar_actions
from gui.menus import Action, ActionGroup

class MainTopBar(QToolBar):
    request_edit_session_complete = pyqtSignal()
    mod_loaded_signal = pyqtSignal(object)
    save_open_signal = pyqtSignal()
    save_all_changed_signal = pyqtSignal()
    save_all_signal = pyqtSignal()
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setMovable(False)
        self.actions = {}
        self.menu_def = build_topbar_actions(self)
        self._build_toolbar()

    def _build_toolbar(self):
        for item in self.menu_def:
            if isinstance(item, ActionGroup):
                self._build_menu(item)
            elif isinstance(item, Action):
                self._build_button(self, item)

    def _build_menu(self, group):
        menu = QMenu(group.text, self)
        for item in group.actions:
            self._build_button(menu, item)
        self.addAction(menu.menuAction())

    def _build_button(self, menu, item):
        action = QAction(item.text, self)
        action.triggered.connect(item.callback)
        action.setEnabled(item.enabled)
        self.actions[item.text] = action
        menu.addAction(action)

    def _enable_actions(self):
        self.actions["Save Open"].setEnabled(True)
        self.actions["Save All Changed"].setEnabled(True)
        self.actions["Save All"].setEnabled(True)