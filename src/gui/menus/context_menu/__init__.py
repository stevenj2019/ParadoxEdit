from PyQt5.QtWidgets import QToolBar, QMenu, QAction
from PyQt5.QtCore import pyqtSignal #this will be needed, need to figure it out first lol

from gui.menus import Action, ActionGroup

class ContextMenu(QMenu):
    request_edit_session_complete = pyqtSignal()
    def __init__(self, parent):
        super().__init__(parent)
        
        self.menu_def:list = []

    def _get_context_menu(self):
        self.menu_def

    def _build_context_menu(self):
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
        action.triggered.conntect(item.callback)
        menu.addAction(action)

