from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem
from PyQt5.QtCore import Qt, pyqtSignal

from ParadoxParser import ParadoxScriptParser as PDXScript
from ParadoxParser.ParadoxNodes import GenericBlock, GenericKeyValue, GenericComment, GenericString, GenericToken

from App.Enums import QtStorage, ExpansionMode, ChangeState
from App.GUI.Menus.ContextMenus import ParadoxNodesContextMenu
from App.GUI.StyledDelegate import NodeStateDelegate

class ContentsPanel(QWidget):
    edit_open_request = pyqtSignal(object, object, object)
    def __init__(self, parent, app_controller):
        super().__init__()
        self.parent = parent
        self.app_controller = app_controller
        self.node_to_item:dict = {}

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.tree = QTreeWidget()
        self.tree.setColumnCount(2)
        self.tree.setHeaderLabels(["Key", "Value"])
        self.tree_fully_expanded = False
        self.tree.setItemDelegate(NodeStateDelegate(self.app_controller.style_manager, self.tree))
        self.tree.itemDoubleClicked.connect(self._on_item_double_click)
        
        self.context_menu = ParadoxNodesContextMenu(self, app_controller)
        self.context_menu.request_expansion.connect(self.set_expansion_rule)
        
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._request_context_menu)
        
        layout.addWidget(self.tree)

    def set_node_state(self, node, state):
        item = self.node_to_item[node]
        if item is None:
            return
        # item.setText(1, node._get_value())
        item.setData(0, QtStorage.STATE, state)
        self.tree.update()

    def load_block(self, file):
        """
        Load a GenericBlock into the tree for display.
        """
        block = file.file
        self.node_to_item.clear()
        self.tree.clear()
        self.tree.blockSignals(True)
        self.tree.setUpdatesEnabled(False)

        try:
            file_context = self.app_controller.file_system.open_file.context #here is where we treieve currently open context
            if isinstance(block, PDXScript):
                self._add_nodes(self.tree.invisibleRootItem(), block.nodes, file_context)
            else:
                self._add_nodes(self.tree.invisibleRootItem(), block.nodes, file_context)

        finally:
            self.tree.blockSignals(False)
            self.tree.setUpdatesEnabled(True)
        self.set_expansion_rule(ExpansionMode.DEPTH)
        self.tree.resizeColumnToContents(0)

    def _add_nodes(self, parent_item, nodes, open_file_context, inherited_state=None):
        for node in nodes:
            effective_state = (
                inherited_state 
                or self.app_controller.file_system.change_tracker.get_node_state(node)
            )
            match node:
                case GenericBlock():
                    self._build_block(parent_item, node, open_file_context, effective_state)
                case GenericComment():
                    self._build_row(parent_item, node, open_file_context, effective_state, "Comment")
                case GenericString()|GenericToken():
                    self._build_row(parent_item, node, open_file_context, effective_state, "Array Value")
                case GenericKeyValue():
                    self._build_row(parent_item, node, open_file_context, effective_state)

    def _build_block(self, parent_item, node, open_file_context, inherited_state):
        item = QTreeWidgetItem([str(node.key), ""])
        self.node_to_item[node] = item

        effective_state = inherited_state or self.app_controller.file_system.change_tracker.get_node_state(node)
        context = open_file_context.derive_node_context(node)
        print(f"{open_file_context} {node.key} block with {context}") #and by here, it is already wrong.

        item.setData(0, QtStorage.NODE, node)
        item.setData(0, QtStorage.IS_BLOCK, True)
        item.setData(0, QtStorage.STATE, effective_state)
        item.setData(0, QtStorage.CONTEXT, context)

        parent_item.addChild(item)

        self._add_nodes(item, node.nodes, open_file_context, effective_state)

    def _build_row(self, parent_item, node, open_file_context, inherited_state=None, label=""):
        if isinstance(node, GenericKeyValue):
            value_label = node.key
            value_node = node.value
        else:
            value_node = node
            value_label = label or type(node).__name__

        item = QTreeWidgetItem([value_label, str(value_node._get_value())])
        self.node_to_item[node] = item
        self.node_to_item[value_node] = item 

        if inherited_state and inherited_state in (ChangeState.ADDED, ChangeState.DELETED):
            effective_state = inherited_state
        else:
            effective_state = self.app_controller.file_system.change_tracker.get_node_state(node)
        context = open_file_context.derive_node_context(node)
        
        item.setData(0, QtStorage.NODE, node)
        item.setData(0, QtStorage.STATE, effective_state)
        item.setData(0, QtStorage.CONTEXT, context)
        
        parent_item.addChild(item)

    def _on_item_double_click(self, item, column):
        if column == 1: #value was clicked.
            if not item.data(0, QtStorage.IS_BLOCK):
                node = item.data(0, QtStorage.NODE)
                if node:
                    self.edit_open_request.emit(self.tree, item, node)

    def _request_context_menu(self, pos):
        selected = self.tree.itemAt(pos)
        if not selected:
            return
        item = selected.data(0, QtStorage.NODE)
        context = selected.data(0, QtStorage.CONTEXT)
        # action_context = context.
        self.context_menu.call(item, context)
        self.context_menu.exec_(self.tree.viewport().mapToGlobal(pos))

    def request_node_mutation(self, request):
        self.app_controller.request_block_mutation.emit(request)

    def set_expansion_rule(self, mode, depth_limit=1, root_item=None):
        self.tree.setUpdatesEnabled(False)
        if root_item is None:
            root_item = self.tree.invisibleRootItem()
        root_item = root_item if root_item else self.tree.invisibleRootItem()

        def recurse(item, depth):
            for i in range(item.childCount()):
                child = item.child(i)
                match mode:
                    case ExpansionMode.ALL|ExpansionMode.FROM_NODE:
                        child.setExpanded(True)
                    case ExpansionMode.DEPTH:
                        child.setExpanded(depth < depth_limit)
                recurse(child, depth+1)
        
        root_item.setExpanded(True)
        recurse(root_item, 0)
        self.tree.setUpdatesEnabled(True)
        self.tree.resizeColumnToContents(0)

