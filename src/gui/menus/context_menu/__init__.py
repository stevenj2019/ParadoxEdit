from PyQt5.QtWidgets import QMainWindow, QMenu, QLabel, QWidgetAction, QAction
from PyQt5.QtCore import pyqtSignal #this will be needed, need to figure it out first lol

from gui.menus import Action, ActionGroup

class ContextMenu(QMenu):
    request_edit_session_complete = pyqtSignal()
    def __init__(self, parent:QMainWindow, menu_def:list):
        super().__init__(parent)
        self.controller = parent
        self.menu_def:list = menu_def
        self._build_context_menu()

    def _build_context_menu(self):
        for item in self.menu_def:
            if isinstance(item, ActionGroup):
                self._build_menu(item)
            elif isinstance(item, Action):
                self._build_button(self, item)

    def _build_menu(self, group):
        label = QLabel(group.text)
        label.setStyleSheet("""
            font-weight:bold;
            padding: 4px 12px;
        """)
        action = QWidgetAction(self)
        action.setDefaultWidget(label)
        self.addAction(action)
        self.addSeparator()
        for item in group.actions:
            self._build_button(item)

    def _build_button(self, item):
        action = QAction(item.text, self)
        action.triggered.connect(item.callback)
        self.addAction(action)

