from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHeaderView, QTreeWidget, QTreeWidgetItem)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.Qt import QMenu
from PyQt5.QtGui import QCursor

from ParadoxParser import ParadoxScriptParser as PDXScript
from ParadoxParser.ParadoxNodes import GenericBlock, GenericKeyValue, GenericComment, GenericString, GenericToken

from gui.constants import FILE, NODE, IS_BLOCK
from gui.menus.context_menu import ContextMenu
from gui.menus import Action, ActionGroup

class ModPanel(QWidget):
    request_load_block = pyqtSignal(object)
    request_bulkable_operation = pyqtSignal(object, object)
    load_file = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.mod = None
        self.open_file = None

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.tree = QTreeWidget()

        self.tree.setColumnCount(1)

        header = self.tree.header()
        header.setSectionResizeMode(0, QHeaderView.Stretch)

        self.tree.setHeaderHidden(True)
        self.tree.setTextElideMode(Qt.ElideRight)
        
        layout.addWidget(self.tree)

        self.tree.itemClicked.connect(self._on_element_click)

        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.build_context_menu)

    def _populate_tree(self, mod):
        self.tree.clear()

        root = QTreeWidgetItem([mod.mod_name or "Unnamed Mod"])
        self.tree.addTopLevelItem(root)

        descriptor_item = QTreeWidgetItem(["Descriptor"])
        descriptor_item.setData(0, FILE, mod.descriptor_object)
        root.addChild(descriptor_item)
        self.open_file = descriptor_item

        categories_parent = QTreeWidgetItem(["Categories"])
        root.addChild(categories_parent)

        for c_key, c_val in mod.categories.items():
            cat_sub = QTreeWidgetItem([c_key])
            cat_sub.setData(0, FILE, c_val)
            for file, obj in c_val.files.items():
                widget = QTreeWidgetItem([file])
                widget.setText(0, file)
                widget.setData(0, FILE, obj)
                cat_sub.addChild(widget)

            categories_parent.addChild(cat_sub)
        
        root.setExpanded(True)
        categories_parent.setExpanded(True)

        if mod.error_categories:
            print("Failed categories:")
            for name in mod.error_categories:
                print(f" - {name}")

    def build_context_menu(self, pos):
        item = self.tree.itemAt(pos)
        if not item:
            return
        selected = item.data(0, FILE)
        if not selected:
            return
        menu = ContextMenu(self.tree, selected.context_sections())
        menu.exec_(self.tree.viewport().mapToGlobal(pos))

    def _on_element_click(self, item, column):
        if item.data(0, IS_BLOCK):
            return
        file = item.data(0, FILE)
        if file:
            self.open_file = file
            self.request_load_block.emit(file)

class ContentsPanel(QWidget):
    edit_open_request = pyqtSignal(object, object, object)
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.tree = QTreeWidget()
        self.tree.setColumnCount(2)
        self.tree.setHeaderLabels(["Key", "Value"])
        self.tree_fully_expanded = False
        layout.addWidget(self.tree)

        self.tree.itemDoubleClicked.connect(self._on_item_double_click)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.build_context_menu)

    def _load_block(self, block):
        """
        Load a GenericBlock into the tree for display.
        """
        self.tree.clear()
        self.tree.setUpdatesEnabled(False)
        self.tree.blockSignals(True)

        try:
            if isinstance(block, PDXScript):
                self._add_nodes(self.tree.invisibleRootItem(), block.nodes)
            else:
                self._add_nodes(self.tree.invisibleRootItem(), block.obj.nodes)

        finally:
            self.tree.blockSignals(False)
            self.tree.setUpdatesEnabled(True)
        self.set_expansion_rule(mode="depth", depth_limit=1)
        self.tree.resizeColumnToContents(0)

    def _add_nodes(self, parent_item, nodes):
        for node in nodes:
            match node:
                case GenericBlock():
                    self._build_block(parent_item, node)
                case GenericComment():
                    self._build_row(parent_item, node, "Comment")
                case GenericString()|GenericToken():
                    self._build_row(parent_item, node, "Array Value")
                case GenericKeyValue():
                    self._build_row(parent_item, node)

    def _build_block(self, parent_item, node):
        item = QTreeWidgetItem([str(node.key), ""])
        item.setData(0, NODE, node)
        item.setData(0, IS_BLOCK, True)
        parent_item.addChild(item)

        self._add_nodes(item, node.children)

    def _build_row(self, parent_item, node, label=""):
        if isinstance(node, GenericKeyValue):
            value_label = node.key
            value_node = node.value
        else:
            value_node = node
            value_label = label or type(node).__name__

        item = QTreeWidgetItem([value_label, str(value_node._get_value())])
        item.setData(0, NODE, node)
        parent_item.addChild(item)

    def _on_item_double_click(self, item, column):
        if column == 1: #value was clicked.
            if not item.data(0, IS_BLOCK):
                node = item.data(0, NODE)
                if node:
                    self.edit_open_request.emit(self.tree, item, node)

    def build_context_menu(self, pos):
        item = self.tree.itemAt(pos)
        if not item:
            return
        menu = ContextMenu(self.tree, self._get_context_menu_options(item))
        menu.exec_(self.tree.viewport().mapToGlobal(pos))

    def _get_context_menu_options(self, item):
        return [
            ActionGroup("Tree Options", [
                Action("Expand All", lambda:self.set_expansion_rule(mode="all"), True),
                Action("Collapse All", lambda:self.set_expansion_rule(mode="depth", depth_limit=1), True),
                Action("Expand This", lambda:self.set_expansion_rule(mode="all", root_item=item), True),
            ])
        ]

    def set_expansion_rule(self, mode="depth", depth_limit=1, root_item=None):
        self.tree.setUpdatesEnabled(False)
        if root_item is None:
            root_item = self.tree.invisibleRootItem()

        def recurse(item, depth):
            for i in range(item.childCount()):
                child = item.child(i)
                if mode == "all":
                    child.setExpanded(True)
                elif mode == "none":
                    child.setExpanded(False)
                elif mode == "depth":
                    child.setExpanded(depth < depth_limit)
                elif mode == "from_node":
                    child.setExpanded(True)
                recurse(child, depth+1)
        
        root_item.setExpanded(True)
        recurse(root_item, 0)
        self.tree.setUpdatesEnabled(True)
        self.tree.resizeColumnToContents(0)
