from PyQt5.QtWidgets import QMainWindow, QWidget, QTreeWidget, QTreeWidgetItem, QToolBar, QMenu, QLabel, QWidgetAction, QAction
from PyQt5.QtCore import pyqtSignal

from ParadoxParser.ParadoxNodes import GenericBlock, GenericKeyValue, GenericNode

from App.ModClasses.Categories import GenericCategory
from App.ModClasses.CategoryItems import GenericCategoryItem
from App.ModClasses.ActionModels import ActionGroup, Action
from App.SignalContexts import ExpansionMode, RequestExpansionContext
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

class GenericContextMenu(QMenu):
    def __init__(self, panel, parent, selected, node):
        super().__init__()
        self.panel = panel
        self.parent:QTreeWidget = parent
        self.selected:QTreeWidgetItem = selected
        self.selected_node = node
        self.menu_def:list = []

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
    def __init__(self, 
                 panel:QWidget,
                 parent:QTreeWidget, 
                 selected:QTreeWidgetItem, 
                 node:GenericCategory|GenericCategoryItem):
        super().__init__(panel, parent, selected, node)
        self.menu_def = self.selected_node.context_sections()
        self._build_menu()

class ParadoxNodesContextMenu(GenericContextMenu):
    request_expansion_all = pyqtSignal(str, int, object)
    request_expansion_this = pyqtSignal()
    request_collapse_all = pyqtSignal()
    
    def __init__(self, 
                 panel:QWidget,
                 parent:QTreeWidget, 
                 selected:QTreeWidgetItem, 
                 node:GenericBlock|GenericKeyValue|GenericNode):
        super().__init__(panel, parent, selected, node)
        self.menu_def = self._get_context_menu_options()
        self._build_menu()

    def _get_context_menu_options(self):
        return [
            ActionGroup("Tree Options", [
                Action("Expand All", lambda:self.panel.set_expansion_rule(ExpansionMode.ALL), True),
                Action("Collapse All", lambda:self.panel.set_expansion_rule(ExpansionMode.DEPTH, depth_limit=2), True),
                Action("Expand This", lambda:self.panel.set_expansion_rule(ExpansionMode.FROM_NODE, root_item=self.selected), True),
            ])
        ]
        RequestExpansionContext(ExpansionMode.ALL)
        RequestExpansionContext(ExpansionMode.DEPTH, depth_limit=2)
        RequestExpansionContext(ExpansionMode.FROM_NODE, root_item=self.selected)
        
