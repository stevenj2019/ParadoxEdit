from PyQt5.QtWidgets import QMainWindow, QToolBar, QMenu, QAction
from PyQt5.QtCore import pyqtSignal

from App.Contracts.Enums import SaveTarget
from App.GUI.Actions import ActionGroup, Action

class Topbar(QToolBar):
    request_load_mod = pyqtSignal()
    request_load_vanilla = pyqtSignal()
    request_load_workspace = pyqtSignal()
    request_workspace_save = pyqtSignal()
    request_settings_window = pyqtSignal()
    def __init__(self, parent, app_controller):
        super().__init__(parent)
        self.parent:QMainWindow = parent
        self.app_controller = app_controller
        self.actions:dict = {}
        self.menu_def:list = self._get_topbar_actions()

        self.setMovable(False)
        self._build_toolbar()

    def _get_topbar_actions(self):
        return [
            ActionGroup("File", [
                Action("Save Open", lambda:self.app_controller.request_save.emit(SaveTarget.OPEN), False),
                Action("Save All", lambda:self.app_controller.request_save.emit(SaveTarget.ALL), False)
            ]),
            ActionGroup("Workspace", [
                Action("Open Mod", self.request_load_mod.emit, True),
                Action("Load Vanilla to workspace", self.request_load_vanilla.emit, True), 
                Action("Load Workspace", self.request_load_workspace.emit, True), 
                Action("Save Workspace as File", self.request_workspace_save.emit, True)
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
        self.actions["Save All"].setEnabled(True)