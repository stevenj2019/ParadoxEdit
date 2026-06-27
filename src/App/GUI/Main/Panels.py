from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHeaderView, QTreeWidget, QTreeWidgetItem)
from PyQt5.QtCore import Qt, pyqtSignal
# from PyQt5.QtGui import QCursor, QColor
from PyQt5.QtGui import QColor as QColour

from ParadoxParser import ParadoxScriptParser as PDXScript
from ParadoxParser.ParadoxNodes import GenericBlock, GenericKeyValue, GenericComment, GenericString, GenericToken

from App.Constants import ChangeState, FILE, NODE, IS_BLOCK, STATE, CATEGORY, IS_CATEGORY
from App.Enums import ExpansionMode
from App.GUI.Menus import GenericCategoryContextMenu, ParadoxNodesContextMenu
from App.GUI.StyledDelegate import ParadoxFileDelegate, NodeStateDelegate

class ModPanel(QWidget):
    request_load_block = pyqtSignal(object)
    # request_bulkable_operation = pyqtSignal(object, object)
    load_file = pyqtSignal()
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.node_to_item:dict = {}
        self.file_to_category:dict = {}

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.tree = QTreeWidget()
        self.tree.setColumnCount(1)

        header = self.tree.header()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        self.tree.setHeaderHidden(True)
        self.tree.setTextElideMode(Qt.ElideRight)
        self.tree.setItemDelegate(ParadoxFileDelegate(self.parent.app_controller.style_manager, self.tree))
        layout.addWidget(self.tree)

        self.tree.itemClicked.connect(self._on_element_click)

        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.build_context_menu)

        # self.parent.file_changed.connect(self.set_file_dirty)


    def set_file_dirty(self, file):
        file_item = self.node_to_item[file]
        state_ = self.parent.app_controller.change_tracker.get_file_state(file) #This returns True
        file_item.setData(0, STATE, state_)

        try:
            category_item = self.file_to_category[file]
            category_item.setData(0, STATE, ChangeState.MODIFIED)
        except KeyError:
            pass
        self.tree.update()

    def set_file_clean(self, file):
        file_item = self.node_to_item[file]
        file_item.setData(0, STATE, ChangeState.CLEAN)
        try:
            category_item = self.file_to_category[file]
            category = category_item.data(0, CATEGORY)
            if all(self.parent.app_controller.change_tracker.get_file_state(file) == ChangeState.CLEAN
                   for file in category.files):
                category_item.setData(0, STATE, ChangeState.CLEAN)
        except KeyError:
            pass


    def _populate_tree(self, mod):
        self.tree.clear()

        root = QTreeWidgetItem([mod.mod_name or "Unnamed Mod"])
        self.tree.addTopLevelItem(root)

        descriptor_item = QTreeWidgetItem(["Descriptor"])
        descriptor_item.setData(0, FILE, mod.descriptor_object)
        descriptor_item.setData(0, STATE, ChangeState.CLEAN)
        self.node_to_item[mod.descriptor_object] = descriptor_item
        root.addChild(descriptor_item)
        self.open_file = descriptor_item

        categories_parent = QTreeWidgetItem(["Categories"])
        root.addChild(categories_parent)

        for c_key, c_val in mod.categories.items():
            cat_sub = QTreeWidgetItem([c_key])
            cat_sub.setData(0, IS_CATEGORY, True)
            cat_sub.setData(0, CATEGORY, c_val)
            self.node_to_item[c_val] = cat_sub
            for file, obj in c_val.files.items():
                widget = QTreeWidgetItem([file])
                self.node_to_item[obj] = widget
                self.file_to_category[obj] = cat_sub
                widget.setText(0, file)
                widget.setData(0, FILE, obj)
                widget.setData(0, STATE, ChangeState.CLEAN)
                widget.setData(0, IS_CATEGORY, False)
                cat_sub.addChild(widget)

            categories_parent.addChild(cat_sub)
        
        root.setExpanded(True)
        categories_parent.setExpanded(True)

        if mod.error_categories:
            print("Failed categories:")
            for name in mod.error_categories:
                print(f" - {name}")

    def build_context_menu(self, pos):
        selected = self.tree.itemAt(pos)
        if not selected:
            return
        item = selected.data(0, FILE)
        if not item:
            return
        menu = GenericCategoryContextMenu(self, self.tree, selected, item)
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
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.node_to_item:dict = {}

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.tree = QTreeWidget()
        self.tree.setColumnCount(2)
        self.tree.setHeaderLabels(["Key", "Value"])
        self.tree_fully_expanded = False
        self.tree.setItemDelegate(NodeStateDelegate(self.parent.app_controller.style_manager, self.tree))
        self.tree.itemDoubleClicked.connect(self._on_item_double_click)
        
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.build_context_menu)
        
        layout.addWidget(self.tree)
        self.parent.node_changed.connect(self.refresh_node)


    def refresh_node(self, node):
        item = self.node_to_item[node]
        item.setText(1, node._get_value())
        state_ = self.parent.app_controller.change_tracker.get_node_state(node)
        item.setData(0, STATE, state_)
        self.tree.update()

    def set_file_clean(self, file):
        def _set_subtree_state(item):
            item.setData(0, STATE, ChangeState)

            for i in range(item.childCount()):
                child = item.child(i)
                _set_subtree_state(child)

        for node in file.nodes:
            item = self.node_to_item[node]
            _set_subtree_state(item)

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
                self._add_nodes(self.tree.invisibleRootItem(), block.nodes)
                # self._add_nodes(self.tree.invisibleRootItem(), block.obj.nodes)

        finally:
            self.tree.blockSignals(False)
            self.tree.setUpdatesEnabled(True)
        self.set_expansion_rule(ExpansionMode.DEPTH)
        self.tree.resizeColumnToContents(0)

    def _add_nodes(self, parent_item, nodes, inherited_state=None):
        for node in nodes:
            match node:
                case GenericBlock():
                    self._build_block(parent_item, node, inherited_state)
                case GenericComment():
                    self._build_row(parent_item, node, inherited_state, "Comment")
                case GenericString()|GenericToken():
                    self._build_row(parent_item, node, inherited_state, "Array Value")
                case GenericKeyValue():
                    self._build_row(parent_item, node, inherited_state)

    def _build_block(self, parent_item, node, inherited_state):
        item = QTreeWidgetItem([str(node.key), ""])
        self.node_to_item[node] = item
        item.setData(0, NODE, node)
        item.setData(0, IS_BLOCK, True)

        parent_item.addChild(item)

        effective_state = inherited_state or self.parent.app_controller.change_tracker.get_node_state(node)
        item.setData(0, STATE, effective_state)
        self._add_nodes(item, node.nodes, effective_state)

    def _build_row(self, parent_item, node, inherited_state=None, label=""):
        if isinstance(node, GenericKeyValue):
            value_label = node.key
            value_node = node.value
        else:
            value_node = node
            value_label = label or type(node).__name__

        item = QTreeWidgetItem([value_label, str(value_node._get_value())])
        self.node_to_item[node] = item
        self.node_to_item[value_node] = item 
        
        item.setData(0, NODE, node)
        parent_item.addChild(item)

        effective_state = inherited_state or self.parent.app_controller.change_tracker.get_node_state(node)
        item.setData(0, STATE, effective_state)

    def _on_item_double_click(self, item, column):
        if column == 1: #value was clicked.
            if not item.data(0, IS_BLOCK):
                node = item.data(0, NODE)
                if node:
                    self.edit_open_request.emit(self.tree, item, node)

    def build_context_menu(self, pos):
        selected = self.tree.itemAt(pos)
        if not selected:
            return
        item = selected.data(0, NODE)
        menu = ParadoxNodesContextMenu(self, self.tree, selected, item)
        menu.exec_(self.tree.viewport().mapToGlobal(pos))

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
