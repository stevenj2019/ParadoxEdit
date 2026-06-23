from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QSplitter, QVBoxLayout, QToolBar, QAction, QTreeWidget, QTreeWidgetItem, QHeaderView, QComboBox, QLineEdit)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.Qt import QMenu
from PyQt5.QtGui import QCursor


from ModClasses.ParadoxMod import ParadoxMod
from ParadoxParser import ParadoxScriptParser as PDXScript
from ParadoxParser.ParadoxNodes import GenericBlock, GenericBool, GenericKeyValue, GenericComment, GenericString, GenericToken, GenericInt, GenericFloat

from gui.cell_editors import text_editor, bool_dropdown, int_editor, float_editor
from gui.settings import SettingsWindow
from gui.warning_messages import toggle_safe_mode_warning
from gui.util import get_safe_mode_opposed_text, toggle_dark_mode, add_menu_heading, get_main_window, build_category_list
from traverse import apply_to_target

NODE = Qt.UserRole
IS_BLOCK = Qt.UserRole + 1

class MainWindow(QMainWindow):
    def __init__(self, mod, config):
        super().__init__()
        self.mod = mod
        self.config = config
        self.safe_mode:bool = config.safe_mode
        self.bulk_warning_shown:bool = False

        self.setWindowTitle("ParadoxEdit")
        #TopBar
        topbar = MainTopBar(self)
        self.addToolBar(topbar)
        #Splitter
        splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(splitter)

        #ModPanel(left)
        self.mod_panel = ModPanel(mod)
        self.mod_panel.setMinimumWidth(150)
        splitter.addWidget(self.mod_panel)

        self.contents_panel = ContentsPanel(mod)
        self.contents_panel.setMinimumWidth(300)
        self.contents_panel.load_block(self.mod.descriptor_object)
        splitter.addWidget(self.contents_panel)
        
        self.mod_panel.request_load_block.connect(self.contents_panel.load_block)
        self.mod_panel.request_context_menu.connect(self.show_context_menu)
        self.contents_panel.request_context_menu.connect(self.contents_panel.populate_context_menu)
        splitter.setSizes([200, 600])

    def show_context_menu(self, panel, selected):
        menu = QMenu(self)

        add_menu_heading(menu, "Editor")
        menu.addAction("Toggle Dark Mode", lambda:toggle_dark_mode(self.config))
        menu.addAction(f"{get_safe_mode_opposed_text(self)} Safe Mode", lambda:toggle_safe_mode_warning(self))
        panel.populate_context_menu(menu, self, selected)

        menu.exec_(QCursor.pos())

class MainTopBar(QToolBar):
    def __init__(self, parent):
        super().__init__(parent)

        self.setMovable(False)

        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.open_settings_window)
        self.addAction(settings_action)

    def open_settings_window(self):
        settings = SettingsWindow("PDXEdit Settings", get_main_window().config)
        settings.exec_()


class ModPanel(QWidget):
    request_load_block = pyqtSignal(object)
    request_context_menu = pyqtSignal(object, object)
    def __init__(self, mod):
        super().__init__()
        self.mod = mod

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.tree = QTreeWidget()

        self.tree.setColumnCount(1)

        header = self.tree.header()
        header.setSectionResizeMode(0, QHeaderView.Stretch)

        self.tree.setHeaderHidden(True)
        self.tree.setTextElideMode(Qt.ElideRight)
        
        layout.addWidget(self.tree)

        self._populate_tree()
        self._connect_events()

    def _populate_tree(self):
        self.tree.clear()

        root = QTreeWidgetItem([self.mod.mod_name or "Unnamed Mod"])
        self.tree.addTopLevelItem(root)

        descriptor_item = QTreeWidgetItem(["Descriptor"])
        descriptor_item.setData(0, NODE, self.mod.descriptor_object)
        root.addChild(descriptor_item)

        categories_parent = QTreeWidgetItem(["Categories"])
        root.addChild(categories_parent)

        for c_key, c_val in self.mod.categories.items():            
            cat_sub = QTreeWidgetItem([c_key])
            cat_sub.setData(0, NODE, c_val)
            for file, obj in c_val.files.items():
                cat_sub.addChild(build_category_list(file, obj))

            categories_parent.addChild(cat_sub)
        
        root.setExpanded(True)        
        categories_parent.setExpanded(True)

        if self.mod.error_categories:
            print("Failed categories:")
            for name in self.mod.error_categories:
                print(f" - {name}")

    def populate_context_menu(self, menu, parent, selected):
        if isinstance(selected, PDXScript):
            return
        
        for section_name, actions in selected.context_sections().items():
            menu.addSection(section_name)
            add_menu_heading(menu, section_name)
            for action in actions:
                option = menu.addAction(
                    action.text,
                    lambda checked=False, a=action:
                    apply_to_target(a.callback, parent, selected)
                )
                option.setEnabled(action.enabled)

    def _connect_events(self):
        tree = self.tree

        def on_tree_click(item, column):
            if item.childCount() == 0:
                obj = item.data(0, NODE)
                if obj:
                    self.request_load_block.emit(obj)

        def on_tree_right_click(position):
            item = tree.itemAt(position)
            if not item:
                return

            obj = item.data(0, NODE)
            if not obj:
                return

            self.request_context_menu.emit(self, obj) 
            
        tree.itemClicked.connect(on_tree_click)

        tree.setContextMenuPolicy(Qt.CustomContextMenu)
        tree.customContextMenuRequested.connect(on_tree_right_click)
    
class ContentsPanel(QWidget):
    request_context_menu = pyqtSignal(object)
    def __init__(self, parent:ParadoxMod=None):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.tree = QTreeWidget()
        self.tree.setColumnCount(2)
        self.tree.setHeaderLabels(["Key", "Value"])
        self.tree_fully_expanded = False
        layout.addWidget(self.tree)

        self.current_block = None
        self._connect_events()

        self._node_to_item = dict()
        self._item_initialised = set()

        self.cell_editors = {
            GenericComment: text_editor,
            GenericString:  text_editor,
            GenericBool:    bool_dropdown,
            GenericInt:     int_editor,
            GenericFloat:   float_editor
        }

        self.tree.itemDoubleClicked.connect(self._on_item_double_click)

    def _connect_events(self):
        def _on_tree_right_click(item):
            self.request_context_menu.emit(self)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(_on_tree_right_click)
        
    def load_block(self, block):
        """
        Load a GenericBlock into the tree for display.
        """
        self.current_block = block
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
                case GenericBlock(): #works (kinda? headers are there, and some children)
                    self._build_block(parent_item, node)
                case GenericComment(): #works
                    self._build_row(parent_item, node, "Comment")
                case GenericString(): #works
                    self._build_row(parent_item, node, "Array Value")
                case GenericKeyValue(): #doesnt work
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
                if not node:
                    return
                node_value = node.value if isinstance(node, GenericKeyValue) else node
                def emit(raw):
                    self._commit_edit(item, node_value, raw)

                editor = self._create_editor(node_value, emit)

                self.tree.setItemWidget(item, 1, editor)
                editor.setFocus()

    def _commit_edit(self, item, node, raw):
        if raw:
            node.value = raw
            self.tree.removeItemWidget(item, 1)
            item.setText(1, str(node._get_value()))

    def _create_editor(self, node, fn):
        if isinstance(node, GenericKeyValue):
            node = node.value
        editor_fn = self.cell_editors.get(type(node))
        if not editor_fn: 
            print (f"{node} has no editor, correct?")
            return None
        return editor_fn(node, fn)

    def populate_context_menu(self, panel): #may need to re-add selected later
        selected = self.tree.currentItem()
        menu = QMenu()
        menu.addAction("Expand All", lambda:self.set_expansion_rule(mode="all")) #crashes(or rather hangs indefinitely)
        menu.addAction("Collapse All", lambda:self.set_expansion_rule(mode="depth", depth_limit=1)) 
        menu.addAction("Expand This", lambda:self.set_expansion_rule(mode="all", root_item=selected))
        menu.exec_(QCursor.pos())

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