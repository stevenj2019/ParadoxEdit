from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem
from PyQt5.QtCore import Qt, pyqtSignal

from ParadoxParser import ParadoxScriptParser as PDXScript
from ParadoxParser.ParadoxNodes import GenericBlock, GenericKeyValue, GenericNode, GenericComment, GenericString, GenericToken

from App.Enums import QtStorage, ExpansionMode, ChangeState
from App.Contexts.FileContexts import ParadoxFileContext
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
        
        # self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.tree.customContextMenuRequested.connect(self._request_context_menu)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._request_context_menu)
        layout.addWidget(self.tree)

    def set_node_state(self, node, state):
        try:
            item = self.node_to_item[node]
        except KeyError:
            return
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
            file_context = self.app_controller.file_system.open_file.context
            self._add_nodes(parent_item=self.tree.invisibleRootItem(),
                            parent_node=block,
                            nodes=block.nodes, 
                            open_file_context=file_context)

        finally:
            self.tree.blockSignals(False)
            self.tree.setUpdatesEnabled(True)
        self.set_expansion_rule(ExpansionMode.DEPTH)
        self.tree.resizeColumnToContents(0)

    def _add_nodes(self, 
                   parent_item:QTreeWidgetItem, 
                   parent_node:PDXScript|GenericBlock,
                   nodes:list, 
                   open_file_context:ParadoxFileContext, 
                   inherited_state:ChangeState=None):
        for index, node in enumerate(nodes):
            effective_state = (
                inherited_state 
                or self.app_controller.file_system.change_tracker.get_node_state(node)
            )
            if isinstance(node, GenericBlock):
                self._build_block(parent_item=parent_item,
                                  parent_node=parent_node,
                                  parent_index=index,
                                  node=node,
                                  open_file_context=open_file_context,
                                  inherited_state=effective_state)
            else:
                self._build_row(parent_item=parent_item,
                                parent_node=parent_node,
                                parent_index=index,
                                node=node,
                                open_file_context=open_file_context,
                                inherited_state=effective_state)

    def _build_block(self, 
                     parent_item:QTreeWidgetItem,
                     parent_node:PDXScript|GenericBlock,
                     parent_index:int,
                     node:GenericKeyValue|GenericNode, 
                     open_file_context:ParadoxFileContext, 
                     inherited_state:ChangeState
    ):
        item = QTreeWidgetItem([str(node.key), ""])
        self.node_to_item[node] = item
        effective_state = inherited_state or self.app_controller.file_system.change_tracker.get_node_state(node)
        context = open_file_context.derive_node_context(node)

        item.setData(0, QtStorage.NODE, node)
        item.setData(0, QtStorage.IS_BLOCK, True)
        item.setData(0, QtStorage.STATE, effective_state)
        item.setData(0, QtStorage.CONTEXT, context)
        item.setData(0, QtStorage.PARENT, parent_node)
        item.setData(0, QtStorage.INDEX, parent_index)

        parent_item.addChild(item)

        self._add_nodes(parent_item=item, 
                        parent_node=node,
                        nodes=node.nodes, 
                        open_file_context=open_file_context, 
                        inherited_state=effective_state)

    def _build_row(self, 
                   parent_item:QTreeWidgetItem,
                   parent_node:PDXScript|GenericKeyValue,
                   parent_index:int,
                   node:GenericKeyValue|GenericNode, 
                   open_file_context:ParadoxFileContext, 
                   inherited_state:ChangeState=None
    ):
        if isinstance(node, GenericKeyValue):
            value_label = node.key
            value_node = node.value
        else:
            value_label = ""
            value_node = node

        item = QTreeWidgetItem([value_label, str(value_node._get_value())])
        self.node_to_item[node] = item
        self.node_to_item[value_node] = item 

        if inherited_state and inherited_state in (ChangeState.ADDED, ChangeState.DELETED):
            effective_state = inherited_state
        else:
            effective_state = self.app_controller.file_system.change_tracker.get_node_state(node)
        node_context = open_file_context.derive_node_context(parent_node)
        item.setData(0, QtStorage.NODE, node)
        item.setData(0, QtStorage.STATE, effective_state)
        item.setData(0, QtStorage.CONTEXT, node_context)
        item.setData(0, QtStorage.PARENT, parent_node)
        item.setData(0, QtStorage.INDEX, parent_index)
        
        parent_item.addChild(item)

    def _on_item_double_click(self, item, column):
        if column == 1: #value was clicked.
            if not item.data(0, QtStorage.IS_BLOCK):
                node = item.data(0, QtStorage.NODE)
                if node:
                    self.edit_open_request.emit(self.tree, item, node)

    def _request_context_menu(self, pos):
        pos = self.tree.viewport().mapFrom(self, pos)
        selected = self.tree.itemAt(pos)
        if selected:
            node = selected.data(0, QtStorage.NODE)
            context = selected.data(0, QtStorage.CONTEXT)
            if isinstance(node, GenericBlock):
                parent = node
                index = 0
                context = selected.data(0, QtStorage.CONTEXT)
            else:
                parent = selected.data(0, QtStorage.PARENT)
                index = selected.data(0, QtStorage.INDEX)+1
        else:
            open_file = self.app_controller.file_system.open_file
            file_context = open_file.context

            parent = open_file.file
            index = len(open_file.file.nodes)+1
            context = file_context.derive_node_context(None)

        self.context_menu.call(parent, index, context)
        self.context_menu.exec_(self.tree.viewport().mapToGlobal(pos))

    def request_node_mutation(self, request):
        self.app_controller.request_block_mutation.emit(request)

    def set_expansion_rule(self, mode, depth_limit=1, root_item=None):
        self.tree.setUpdatesEnabled(False)
        if isinstance(root_item, PDXScript) or not root_item:
            root_item = self.tree.invisibleRootItem()

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

