from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App import AppController
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QAction, QMenu, QToolBar

from App.Contracts.Enums import SaveTarget
from App.GUI.Actions import Action, ActionGroup, ActionsResult
from App.GUI.Help import HelpDialog
from App.Loading.ParadoxSource import ParadoxVanilla

class Topbar(QToolBar):
    request_load_mod = pyqtSignal()
    request_load_vanilla = pyqtSignal()
    request_load_workspace = pyqtSignal()
    request_workspace_save = pyqtSignal()
    request_settings_window = pyqtSignal()
    request_dlc_change = pyqtSignal()

    def __init__(self, app_controller: AppController) -> None:
        super().__init__()
        self.app_controller = app_controller
        self.actions: dict = {}
        self.menu_def: list = self._get_topbar_actions()

        self.setMovable(False)
        self._build_toolbar()

    def _get_topbar_actions(self) -> ActionsResult:
        return [
            ActionGroup(
                "File",
                [
                    Action(
                        "Save Open",
                        lambda: self.app_controller.request_save.emit(SaveTarget.OPEN),
                        False,
                    ),
                    Action(
                        "Save All",
                        lambda: self.app_controller.request_save.emit(SaveTarget.ALL),
                        False,
                    ),
                ],
            ),
            ActionGroup(
                "Workspace",
                [
                    Action("Load Vanilla to Workspace", self.request_load_vanilla.emit, True),
                    Action("Configure Loaded DLC", self.request_dlc_change.emit, False),
                    Action("Load Mod to Workspace", self.request_load_mod.emit, True),
                    Action("Load Workspace", self.request_load_workspace.emit, True),
                    Action("Save Workspace as File", self.request_workspace_save.emit, True),
                ],
            ),
            Action("Settings", self.request_settings_window.emit, True),
            Action("Help", HelpDialog, True),
        ]

    def _build_toolbar(self) -> None:
        for item in self.menu_def:
            if isinstance(item, ActionGroup):
                self._build_menu(item)
            elif isinstance(item, Action):
                self._build_button(self, item)

    def _build_menu(self, group: ActionGroup) -> None:
        menu = QMenu(group.text, self)
        for item in group.actions:
            self._build_button(menu, item)
        self.addAction(menu.menuAction())

    def _build_button(self, menu: ActionGroup, item: Action) -> None:
        action = QAction(item.text, self)
        action.triggered.connect(item.callback)
        action.setEnabled(item.enabled)
        self.actions[item.text] = action
        menu.addAction(action)

    def _enable_actions(self) -> None:
        vanilla_loaded = any(isinstance(source, ParadoxVanilla) 
                             for source in self.app_controller.file_system.load_order.sources)
        self.actions["Save Open"].setEnabled(True)
        self.actions["Save All"].setEnabled(True)
        self.actions["Configure Loaded DLC"].setEnabled(vanilla_loaded)
