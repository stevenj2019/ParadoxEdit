from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QMenu, QLabel, QWidgetAction, QAction
from PyQt5.QtCore import pyqtSignal

from ParadoxParser import ParadoxScriptParser as PDXScriptFile
from ParadoxParser.ParadoxNodes import GenericBlock

from App.Enums import ExpansionMode, ChangeState
from App.Contracts import BlockMutationRequest
from App.GUI.Actions import ActionGroup, ActionSubMenu, Action

def dummy(): return 
class GenericContextMenu(QMenu):
    def __init__(self, parent, app_controller):
        super().__init__()
        self.parent:QTreeWidget = parent
        self.app_controller = app_controller
        self.menu_def:list = []
        self.parent_node = None
        self.parent_index = None

    def _get_context_menu_options():
        return 
    
    def _build_menu(self):
        for item in self.menu_def:
            if isinstance(item, ActionGroup):
                self._build_subcategory(item)
            elif isinstance(item, ActionSubMenu):
                self._build_submenu(item)
            elif isinstance(item, Action):
                self._build_button(self, item)
    
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
            if isinstance(item, Action):
                self._build_button(self, item)
            elif isinstance(item, ActionSubMenu):
                self._build_submenu(item)

    def _build_submenu(self, group):
        _menu = QMenu(group.text, self)
        for item in group.actions:
            self._build_button(_menu, item)
        self.addMenu(_menu)

    def _build_button(self, menu, item):
        action = QAction(item.text, menu)
        action.triggered.connect(item.callback)
        action.setEnabled(item.enabled)
        menu.addAction(action)

class GenericCategoryContextMenu(GenericContextMenu):
    def __init__(self, parent:QTreeWidget, app_controller):
        super().__init__(parent, app_controller)
        self.menu_def:list = []

    # def call(self, file, context):
    def call(self, file_context):
        self.clear()
        self.menu_def = self._get_context_menu_options(file_context)
        self._build_menu()

    def _get_context_menu_options(self, file_context):
        return file_context.context.get_actions(self.app_controller, file_context.target)
    
class ParadoxNodesContextMenu(GenericContextMenu):
    request_expansion = pyqtSignal(object)
    def __init__(self, parent:QTreeWidget, app_controller):
        super().__init__(parent, app_controller)
        self.menu_def:list = []

    def call(self, parent, parent_idx, context):
        self.clear()
        self.menu_def = self._get_context_menu_options(node=parent, node_index=parent_idx, context=context)
        self._build_menu()

    def _get_context_menu_options(self, node, node_index, context):
        return [
            ActionGroup("Tree Options", [
                Action("Expand All", lambda:self.parent.set_expansion_rule(ExpansionMode.ALL), True),
                Action("Collapse All", lambda:self.parent.set_expansion_rule(ExpansionMode.DEPTH, depth_limit=1), True),
                Action("Expand This", lambda:self.parent.set_expansion_rule(ExpansionMode.FROM_NODE, root_item=node), (node_index == 0 and isinstance(node, GenericBlock))),
            ]),
            ActionGroup("File Options", [
                ActionSubMenu("Add", [
                    *context.node_actions(self.app_controller, node, node_index),
                ]),
                Action("Delete", 
                       lambda:self.app_controller.request_block_mutation.emit(
                           BlockMutationRequest(file=None,
                                                parent=node,
                                                index=node_index, 
                                                value=None,
                                                state=ChangeState.DELETED)), 
                    (not isinstance(node, PDXScriptFile))
                )
            ])
        ]
