from PyQt5.QtWidgets import (QMainWindow, QWidget, QSplitter, QVBoxLayout, QToolBar, QAction, QTreeWidget, QTreeWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.Qt import QMenu
from PyQt5.QtGui import QCursor


from ModClasses.ParadoxMod import ParadoxMod
from ModClasses.ParadoxCategoryItem import GenericCategoryItem
from ParadoxParser import ParadoxScriptParser as PDXScript
from ParadoxParser.ParadoxNodes import GenericBlock

from gui.settings import SettingsWindow
from gui.warning_messages import toggle_safe_mode_warning
from gui.util import get_safe_mode_opposed_text, toggle_dark_mode, add_menu_heading, get_main_window, build_category_list
from traverse import apply_to_target

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
        descriptor_item.setData(0, Qt.UserRole, self.mod.descriptor_object)
        root.addChild(descriptor_item)

        categories_parent = QTreeWidgetItem(["Categories"])
        root.addChild(categories_parent)

        for c_key, c_val in self.mod.categories.items():            
            cat_sub = QTreeWidgetItem([c_key])
            cat_sub.setData(0, Qt.UserRole, c_val)
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
                obj = item.data(0, Qt.UserRole)
                if obj:
                    self.request_load_block.emit(obj)

        def on_tree_right_click(position):
            item = tree.itemAt(position)
            if not item:
                return

            obj = item.data(0, Qt.UserRole)
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

    def _connect_events(self):
        tree = self.tree

        def on_tree_right_click(item):
            self.request_context_menu.emit(self)

        tree.setContextMenuPolicy(Qt.CustomContextMenu)
        tree.customContextMenuRequested.connect(on_tree_right_click)
        
    def populate_context_menu(self, panel): #may need to re-add selected later
        # if isinstance(selected, PDXScript):
        #     return
        menu = QMenu()
        menu.addAction("Expand All", lambda:self.tree.expandAll())
        menu.addAction("Collapse All", lambda:self.tree.collapseAll())
        menu.exec_(QCursor.pos())
        # for section_name, actions in selected.context_sections().items():
        #     menu.addSection(section_name)
        #     add_menu_heading(menu, section_name)
        #     for action in actions:
        #         option = menu.addAction(
        #             action.text,
        #             lambda checked=False, a=action:
        #             apply_to_target(a.callback, parent, selected)
        #         )
        #         option.setEnabled(action.enabled)

    def load_block(self, block):
        """
        Load a GenericBlock into the tree for display.
        """
        self.current_block = block
        self.tree.clear()
        #descriptor
        if isinstance(block, PDXScript):
            self._add_nodes(self.tree.invisibleRootItem(), block.nodes)
        #categoryitem
        elif isinstance(block, GenericCategoryItem):
            self._add_nodes(self.tree.invisibleRootItem(), block.obj.nodes)
        #?????
        elif isinstance(block, GenericBlock):
            self._add_nodes(self.tree.invisibleRootItem(), block.children)
        #????
        elif isinstance(block, dict):
            self._add_nodes(self.tree.invisibleRootItem(), block)

        self.tree.expandAll()
        self.tree.resizeColumnToContents(0)
        
    def _add_nodes(self, parent_item, nodes):
        """
        Recursive helper to add nodes to the QTreeWidget.
        """
        for node in nodes:
            if node.__class__.__name__ == "GenericComment":
                value_str = self._value_to_str(node.value)
                item = QTreeWidgetItem(["Comment", value_str])
                parent_item.addChild(item)
            elif node.__class__.__name__ == "GenericKeyValue":
                value_str = self._value_to_str(node.value)
                item = QTreeWidgetItem([str(node.key), value_str])
                parent_item.addChild(item)

                if hasattr(node.value, "children"):
                    self._add_nodes(item, node.value.children)

            elif isinstance(node, GenericBlock) or isinstance(node, dict):
                item = QTreeWidgetItem([str(node.key), ""])
                parent_item.addChild(item)
                if isinstance(node, GenericBlock):
                    self._add_nodes(item, node.children)
                elif isinstance(node, dict):
                    self._add_nodes(item, node.values())
            else:
                value_str = self._value_to_str(node)
                item = QTreeWidgetItem(["", value_str])
                parent_item.addChild(item)

    def _value_to_str(self, node):
        """
        Convert a value node to string for display.
        """
        cls_name = node.__class__.__name__
        match cls_name:
            case "GenericString"|"GenericToken"|"GenericComment":
                return node.value
            case "GenericInt"|"GenericFloat":
                return str(node.value)
            case "GenericBool":
                return "yes" if node.value else "no"
            case "GenericKeyValue":
                return self._value_to_str(node.value)
            case "GenericComparator":
                return node._get_value()
            case _:
                return (str(getattr(node, "value", node)))