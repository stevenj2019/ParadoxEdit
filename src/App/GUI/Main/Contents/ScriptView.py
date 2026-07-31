from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App import AppController
    from App.Loading.Models import FileReference
from PyQt5.QtCore import QPoint, Qt, pyqtSignal
from PyQt5.QtGui import QBrush, QKeySequence
from PyQt5.QtWidgets import (
    QApplication,
    QShortcut,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from App.Contexts import BlockContext, NodeContext
from App.Contexts.Base import ParadoxContext
from App.Contracts import InLineEditRequest, NodeMutationRequest
from App.Contracts.Enums import ChangeState, TargetProperty
from App.GUI.Enums import ExpansionMode, QtStorage
from App.GUI.Menus.ContextMenus import ParadoxNodesContextMenu
from App.GUI.StyledDelegate import NodeStateDelegate
from ParadoxParser import ParadoxScriptParser as PDXScript
from ParadoxParser.ParadoxNodes import (
    GenericBlock,
    GenericComparator,
    GenericKeyValue,
    GenericLegacyLocKey,
    GenericLocKey,
    GenericNode,
)


class ScriptView(QWidget):
    edit_open_request = pyqtSignal(object)

    def __init__(self, app_controller: AppController) -> None:
        super().__init__()
        self.app_controller = app_controller
        self.node_to_item: dict = {}
        self.read_only: bool = True

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.tree = QTreeWidget()
        self.tree.setColumnCount(2)
        self.tree.setHeaderLabels(["Key", "Value"])
        self.tree_fully_expanded = False
        self.tree.setItemDelegate(NodeStateDelegate(self.app_controller, self.tree))
        self.tree.itemDoubleClicked.connect(self._on_item_double_click)

        self.context_menu = ParadoxNodesContextMenu(self, app_controller)
        self.context_menu.request_expansion.connect(self.set_expansion_rule)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._request_context_menu)
        layout.addWidget(self.tree)

        self.copy_shortcut = QShortcut(QKeySequence("Ctrl+C"), self)
        self.copy_shortcut.activated.connect(self.copy_selected_item)

    def set_node_state(self, node: GenericNode, state: ChangeState) -> None:
        try:
            item = self.node_to_item[node]
        except KeyError:
            return
        item.setData(0, QtStorage.STATE, state)
        self.tree.update()

    def unload_block(self) -> None:
        self.node_to_item.clear()
        self.tree.clear()

    def load_block(self, file: FileReference) -> None:
        """
        Load a GenericBlock into the tree for display.
        """
        block = file.file
        self.read_only = file.read_only
        self.unload_block()
        self.tree.blockSignals(True)
        self.tree.setUpdatesEnabled(False)

        try:
            file_context = self.app_controller.file_system.open_file.context
            self._add_nodes(
                parent_item=self.tree.invisibleRootItem(),
                parent_node=block,
                nodes=block.nodes,
                open_file_context=file_context,
            )

        finally:
            self.tree.blockSignals(False)
            self.tree.setUpdatesEnabled(True)
        self.set_expansion_rule(ExpansionMode.DEPTH)
        self.tree.resizeColumnToContents(0)

    def _add_nodes(
        self,
        parent_item: QTreeWidgetItem,
        parent_node: PDXScript | GenericBlock,
        nodes: list,
        open_file_context: ParadoxContext,
        inherited_state: ChangeState = None,
    ) -> None:
        for index, node in enumerate(nodes):
            effective_state = (
                inherited_state
                or self.app_controller.file_system.change_tracker.get_node_state(node)
            )
            if isinstance(node, GenericBlock):
                self._build_block(
                    parent_item=parent_item,
                    parent_node=parent_node,
                    parent_index=index,
                    node=node,
                    open_file_context=open_file_context,
                    inherited_state=effective_state,
                )
            else:
                self._build_row(
                    parent_item=parent_item,
                    parent_node=parent_node,
                    parent_index=index,
                    node=node,
                    open_file_context=open_file_context,
                    inherited_state=effective_state,
                )

    def _build_block(
        self,
        parent_item: QTreeWidgetItem,
        parent_node: PDXScript | GenericBlock,
        parent_index: int,
        node: GenericKeyValue | GenericNode,
        open_file_context: ParadoxContext,
        inherited_state: ChangeState,
    ) -> None:
        item = QTreeWidgetItem([str(node.key), ""])
        self.node_to_item[node] = item
        effective_state = (
            inherited_state
            or self.app_controller.file_system.change_tracker.get_node_state(node)
        )
        context = open_file_context.get_block_context(node)

        item.setData(0, QtStorage.EDITABLE, True)
        item.setData(1, QtStorage.EDITABLE, False)
        item.setData(0, QtStorage.NODE, node)
        item.setData(0, QtStorage.IS_BLOCK, True)
        item.setData(0, QtStorage.STATE, effective_state)
        item.setData(0, QtStorage.CONTEXT, context)
        item.setData(0, QtStorage.PARENT, parent_node)
        item.setData(0, QtStorage.INDEX, parent_index)
        item.setData(0, QtStorage.IS_COMPARATOR, False)

        item.setForeground(0, QBrush(Qt.gray))

        parent_item.addChild(item)

        self._add_nodes(
            parent_item=item,
            parent_node=node,
            nodes=node.nodes,
            open_file_context=open_file_context,
            inherited_state=effective_state,
        )

    def _build_row(
        self,
        parent_item: QTreeWidgetItem,
        parent_node: PDXScript | GenericKeyValue,
        parent_index: int,
        node: GenericKeyValue | GenericNode,
        open_file_context: ParadoxContext,
        inherited_state: ChangeState = None,
    ) -> None:
        match node:
            case GenericKeyValue():
                key_editable = True
                value_label = node.key
                value_node = node.value
            case GenericLocKey():
                key_editable = True
                value_label = node.key
                value_node = node
            case GenericLegacyLocKey():
                key_editable = True
                value_label = f"{node.key}:{node.num}"
                value_node = node
            case _:
                key_editable = False
                value_label = ""
                value_node = node

        item = QTreeWidgetItem([value_label, str(value_node._get_value())])
        self.node_to_item[node] = item
        self.node_to_item[value_node] = item

        if inherited_state and inherited_state in (
            ChangeState.ADDED,
            ChangeState.DELETED,
        ):
            effective_state = inherited_state
        else:
            effective_state = (
                self.app_controller.file_system.change_tracker.get_node_state(node)
            )

        node_context = open_file_context.get_node_context(parent_node, node)
        block_context = open_file_context.get_block_context(parent_node)

        item.setData(0, QtStorage.EDITABLE, key_editable)
        item.setData(1, QtStorage.EDITABLE, True)

        item.setData(0, QtStorage.NODE, node)
        item.setData(1, QtStorage.NODE, value_node)

        item.setData(0, QtStorage.IS_BLOCK, False)
        item.setData(0, QtStorage.STATE, effective_state)
        item.setData(0, QtStorage.CONTEXT, node_context)
        item.setData(0, QtStorage.PARENT, parent_node)
        item.setData(0, QtStorage.PARENT_CONTEXT, block_context)
        item.setData(0, QtStorage.INDEX, parent_index)
        item.setData(0, QtStorage.IS_COMPARATOR, isinstance(node, GenericComparator))

        if not key_editable:
            item.setForeground(0, QBrush(Qt.gray))
        if self.read_only:
            item.setForeground(1, QBrush(Qt.gray))

        parent_item.addChild(item)

    def _on_item_double_click(self, item: QTreeWidgetItem, column: int) -> None:
        if not item.data(0, QtStorage.READ_ONLY) and item.data(
            column, QtStorage.EDITABLE
        ):
            target = TargetProperty.KEY if column == 0 else TargetProperty.VALUE
            node = item.data(column, QtStorage.NODE)
            self.edit_open_request.emit(
                InLineEditRequest(self.tree, item, node, target)
            )

    def _request_context_menu(self, pos: QPoint) -> None:
        #TODO should be passing through NullContext to these nodes on vanilla,
        ##### we arent, and i am over it lol
        if self.read_only:
            return
        pos = self.tree.viewport().mapFrom(self, pos)
        column = self.tree.columnAt(pos.x())
        item = self.tree.itemAt(pos)
        if not item:
            return

        node = item.data(0, QtStorage.NODE)
        node_context = NodeContext(
            key_node=item.data(0, QtStorage.NODE),
            selected_node=item.data(column, QtStorage.NODE),
            node_context=item.data(0, QtStorage.CONTEXT),
        )
        is_block = isinstance(node, GenericBlock)
        block_context = BlockContext(
            parent=item.data(0, QtStorage.PARENT),
            parent_index=item.data(0, QtStorage.INDEX),
            parent_context=item.data(0, QtStorage.CONTEXT)
            if is_block
            else item.data(0, QtStorage.PARENT_CONTEXT),
        )
        self.context_menu.call(block_context, node_context)
        self.context_menu.exec_(self.tree.viewport().mapToGlobal(pos))

    def request_node_mutation(self, request: NodeMutationRequest) -> None:
        self.app_controller.request_block_mutation.emit(request)

    def set_expansion_rule(
        self,
        mode: ExpansionMode,
        depth_limit: int = 1,
        root_item: QTreeWidgetItem = None,
    ) -> None:
        self.tree.setUpdatesEnabled(False)

        if isinstance(root_item, GenericBlock):
            root_item = self.node_to_item[root_item]
        elif isinstance(root_item, PDXScript) or not root_item:
            root_item = self.tree.invisibleRootItem()

        def recurse(item: QTreeWidgetItem, depth: int) -> None:
            for i in range(item.childCount()):
                child = item.child(i)
                match mode:
                    case ExpansionMode.ALL | ExpansionMode.FROM_NODE:
                        child.setExpanded(True)
                    case ExpansionMode.DEPTH:
                        child.setExpanded(depth < depth_limit)
                recurse(child, depth + 1)

        root_item.setExpanded(True)
        recurse(root_item, 0)
        self.tree.setUpdatesEnabled(True)
        self.tree.resizeColumnToContents(0)

    def reveal_item(self, item: QTreeWidgetItem) -> None:
        self.tree.setUpdatesEnabled(False)

        while item is not None:
            item.setExpanded(True)
            item = item.parent()

        self.tree.setUpdatesEnabled(True)

    def reveal_node(self, node: GenericNode) -> None:
        item = self.node_to_item.get(node)
        if item:
            self.reveal_item(node)

    def jump_to_node(self, node: QTreeWidgetItem) -> None:
        item = self.node_to_item[node]
        if item:
            self.reveal_item(item)
            self.tree.setCurrentItem(item)
            self.tree.scrollToItem(item)

    def copy_selected_item(self) -> None:
        item = self.tree.currentItem()
        if item is None:
            return

        node = item.data(0, QtStorage.NODE)
        if node is None:
            return
        clipboard = QApplication.clipboard()
        if isinstance(node, GenericBlock):
            clipboard.setText(node.key)
        else:
            clipboard.setText(node._to_string_literal().strip())
