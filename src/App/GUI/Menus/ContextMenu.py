from PyQt5.QtWidgets import QMainWindow, QMenu, QLabel, QWidgetAction, QTreeWidgetItem, QAction
from PyQt5.QtCore import pyqtSignal

from App.GUI.menus import ActionGroup, Action


class ContextMenu(QMenu):
    request_expansion = pyqtSignal(str, int, object)
    def __init__(self, parent:QMainWindow, item:QTreeWidgetItem):
        super().__init__(parent)
        self.controller = parent
        self.menu_def:list = self._get_context_menu_options()
        self._build_context_menu(item)

    def _get_context_menu_options(self, item):
        return [
            ActionGroup("Tree Options", [
                Action("Expand All", self.request_expansion.emit("all", 1, None), True),
                Action("Collapse All", self.request_expansion.emit("depth", 1, None), True),
                Action("Expand This", self.request_expansion.emit("all", 1, item), True),
            ])
        ]

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

