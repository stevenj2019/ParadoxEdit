from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHeaderView, QTreeWidget, QTreeWidgetItem)
from PyQt5.QtCore import Qt, pyqtSignal
# from PyQt5.QtGui import QCursor, QColor
from PyQt5.QtGui import QColor as QColour

from ParadoxParser import ParadoxScriptParser as PDXScript
from ParadoxParser.ParadoxNodes import GenericBlock, GenericKeyValue, GenericComment, GenericString, GenericToken

from App.Enums import QtStorage, ChangeState, ExpansionMode
from App.Contexts.FileContexts import ParadoxFileContext
from App.GUI.Menus.ContextMenus import GenericCategoryContextMenu, ParadoxNodesContextMenu
from App.GUI.StyledDelegate import ParadoxFileDelegate, NodeStateDelegate

class ModPanel(QWidget):
    request_load_block = pyqtSignal(object, object)
    load_file = pyqtSignal()
    def __init__(self, parent, app_controller):
        super().__init__()
        self.parent = parent
        self.app_controller = app_controller
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
        self.tree.setItemDelegate(ParadoxFileDelegate(self.app_controller.style_manager, self.tree))
        layout.addWidget(self.tree)

        self.tree.itemClicked.connect(self._on_element_click)

        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.tree.customContextMenuRequested.connect(self.build_context_menu)

    def set_file_state(self, file, status):
        file_item = self.node_to_item[file]
        file_item.setData(0, QtStorage.STATE, status)
        try:
            self._set_category_state(file)
        except KeyError:
            pass
        self.tree.update()

    def _set_category_state(self, file):
        category_item = self.file_to_category[file]
        category = category_item.data(0, QtStorage.CATEGORY)
        if all(self.app_controller.file_system.change_tracker.get_file_state(file) == ChangeState.CLEAN
                for file in category.files.values()):
            category_item.setData(0, QtStorage.STATE, ChangeState.CLEAN)
        else:
            category_item.setData(0, QtStorage.STATE, ChangeState.MODIFIED)

    def _populate_tree(self, mod):
        self.tree.clear()

        root = QTreeWidgetItem([mod.mod_name or "Unnamed Mod"])
        self.tree.addTopLevelItem(root)

        descriptor_item = QTreeWidgetItem(["Descriptor"])

        descriptor_item.setData(0, QtStorage.FILE, mod.descriptor_object)
        descriptor_item.setData(0, QtStorage.STATE, ChangeState.CLEAN)
        descriptor_item.setData(0, QtStorage.CONTEXT, ParadoxFileContext)
        
        self.node_to_item[mod.descriptor_object] = descriptor_item
        root.addChild(descriptor_item)

        categories_parent = QTreeWidgetItem(["Categories"])
        root.addChild(categories_parent)

        def set_category_data(category_item, category_class, context):
            category_item.setData(0, QtStorage.IS_CATEGORY, True)
            category_item.setData(0, QtStorage.CATEGORY, category_class)
            category_item.setData(0, QtStorage.CONTEXT, context)

        def set_file_data(file_item, file, context):
            file_item.setData(0, QtStorage.FILE, file)
            file_item.setData(0, QtStorage.STATE, ChangeState.CLEAN)
            file_item.setData(0, QtStorage.IS_CATEGORY, False)
            file_item.setData(0, QtStorage.CONTEXT, context)

        for c_key, c_val in mod.categories.items():
            cat_sub = QTreeWidgetItem([c_key])
            category_context = c_val.context
            print(f"{c_val} with {category_context}") #it is correct here
            set_category_data(cat_sub, c_val, category_context)

            self.node_to_item[c_val] = cat_sub
            for file, obj in c_val.files.items():
                widget = QTreeWidgetItem([file])
                self.node_to_item[obj] = widget
                self.file_to_category[obj] = cat_sub

                widget.setText(0, file)
                print(f"{file} {category_context}") #and here
                set_file_data(widget, obj, category_context)
                cat_sub.addChild(widget)

            categories_parent.addChild(cat_sub)
        
        root.setExpanded(True)
        categories_parent.setExpanded(True)

        if mod.error_categories:
            print("Failed categories:")
            for name in mod.error_categories:
                print(f" - {name}")

    def _on_element_click(self, item, column):
        if item.data(0, QtStorage.IS_BLOCK):
            return
        file = item.data(0, QtStorage.FILE)
        context = item.data(0, QtStorage.CONTEXT) #but fucking None Here.
        print(file, context)
        if file:
            self.request_load_block.emit(file, context)

    # def build_context_menu(self, pos):
    #     selected = self.tree.itemAt(pos)
    #     if not selected:
    #         return
    #     item = selected.data(0, QtStorage.FILE)
    #     if not item:
    #         return
    #     menu = GenericCategoryContextMenu(self, self.tree, selected, item)
    #     menu.exec_(self.tree.viewport().mapToGlobal(pos))

class ContentsPanel(QWidget):
    # request_expansion = pyqtSignal(object)
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
        self.tree.customContextMenuRequested.connect(self.request_context_menu)
        
        layout.addWidget(self.tree)

    def set_node_state(self, node, state):
        item = self.node_to_item[node]
        if item is None:
            return
        # item.setText(1, node._get_value())
        item.setData(0, QtStorage.STATE, state)
        self.tree.update()

    def load_block(self, block):
        """
        Load a GenericBlock into the tree for display.
        """
        self.node_to_item.clear()
        self.tree.clear()
        self.tree.blockSignals(True)
        self.tree.setUpdatesEnabled(False)
        try:
            file_context = self.app_controller.file_system.open_file_context #here is where we treieve currently open context
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
            match node:
                case GenericBlock():
                    self._build_block(parent_item, node, open_file_context, inherited_state)
                case GenericComment():
                    self._build_row(parent_item, node, open_file_context, inherited_state, "Comment")
                case GenericString()|GenericToken():
                    self._build_row(parent_item, node, open_file_context, inherited_state, "Array Value")
                case GenericKeyValue():
                    self._build_row(parent_item, node, open_file_context, inherited_state)

    def _build_block(self, parent_item, node, open_file_context, inherited_state):
        item = QTreeWidgetItem([str(node.key), ""])
        self.node_to_item[node] = item

        effective_state = inherited_state or self.app_controller.file_system.change_tracker.get_node_state(node)
        context = open_file_context.derive_node_context(None, node)
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

        effective_state = self.app_controller.file_system.change_tracker.get_node_state(node)
        context = open_file_context.derive_node_context(None, node)
        
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

    def request_context_menu(self, pos):
        selected = self.tree.itemAt(pos)
        if not selected:
            return
        item = selected.data(0, QtStorage.NODE)
        context = selected.data(0, QtStorage.CONTEXT)
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

