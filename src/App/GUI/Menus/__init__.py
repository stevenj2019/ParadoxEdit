from PyQt5.QtWidgets import QMainWindow, QWidget, QTreeWidget, QTreeWidgetItem, QToolBar, QMenu, QLabel, QWidgetAction, QAction
from PyQt5.QtCore import pyqtSignal

from App.Enums import ExpansionMode, SaveTarget, ChangeState
from App.Contracts import BlockMutationRequest
from App.ModClasses.ActionModels import ActionGroup, Action

class TopBar(QToolBar):
    request_load_mod = pyqtSignal()
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
                Action("Open Mod", self.request_load_mod.emit, True), 
                Action("Save Open", lambda:self.app_controller.request_save.emit(SaveTarget.OPEN), False),
                Action("Save All", lambda:self.app_controller.request_save.emit(SaveTarget.ALL), False)
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

class GenericContextMenu(QMenu):
    def __init__(self, parent, app_controller):
        super().__init__()
        self.parent:QTreeWidget = parent
        self.app_controller = app_controller
        self.menu_def:list = []
        self.selected:QTreeWidgetItem = None

    def call(self, selected):
        self.clear()
        self.selected = selected
        self.menu_def = self._get_context_menu_options(self.selected)
        self._build_menu()

    def _get_context_menu_options():
        return 
    
    def _build_menu(self):
        for item in self.menu_def:
            if isinstance(item, ActionGroup):
                self._build_subcategory(item)
            elif isinstance(item, Action):
                self._build_button(item)
    
    def _build_subcategory(self, group):
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

class GenericCategoryContextMenu(GenericContextMenu):
    def __init__(self, parent:QTreeWidget, app_controller):
        super().__init__(parent, app_controller)
        self.menu_def:list = []

    def _get_context_menu_options(self):
        #TODO
        return
    
class ParadoxNodesContextMenu(GenericContextMenu):
    request_expansion = pyqtSignal(object)
    def __init__(self, parent:QTreeWidget, app_controller):
        super().__init__(parent, app_controller)
        self.menu_def:list = []

    def _get_context_menu_options(self, selected):
        return [
            ActionGroup("Tree Options", [
                Action("Expand All", lambda:self.parent.set_expansion_rule(ExpansionMode.ALL), True),
                Action("Collapse All", lambda:self.parent.set_expansion_rule(ExpansionMode.DEPTH, depth_limit=2), True),
                Action("Expand This", lambda:self.parent.set_expansion_rule(ExpansionMode.FROM_NODE, root_item=selected), True),
            ]), 
            ActionGroup("File Options", [
                # ActionGroup("Add+")
                Action("Delete", lambda:self.app_controller.request_block_mutation.emit(BlockMutationRequest(file=None,
                                                                                                        target=selected, 
                                                                                                        value=None,
                                                                                                        state=ChangeState.DELETED)), True)
            ])
        ]
