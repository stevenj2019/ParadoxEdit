from PyQt5.QtWidgets import QMainWindow, QToolBar, QMenu, QAction
from PyQt5.QtCore import pyqtSignal

from App.ModClasses.ActionModels import Action, ActionGroup

class TopBar(QToolBar):
    request_load_mod = pyqtSignal()
    request_settings_window = pyqtSignal()
    request_save_open_signal = pyqtSignal()
    request_save_all_changed_signal = pyqtSignal()
    request_save_all_signal = pyqtSignal()
    
    def __init__(self, parent):
        super().__init__(parent)
        self.controller:QMainWindow = parent
        self.actions:dict = {}
        self.menu_def:list = self._get_topbar_actions()

        self.setMovable(False)
        self._build_toolbar()

    def _get_topbar_actions(self):
        return [
            ActionGroup("File", [
                Action("Open Mod", self.request_load_mod.emit, True), 
                Action("Save Open", self.request_save_open_signal.emit, False),
                Action("Save All Changed", self.request_save_all_changed_signal.emit, False),
                Action("Save All", self.request_save_all_signal.emit, False)
            ]),
            Action("Settings", self.request_settings_window.emit, True)
        ]
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