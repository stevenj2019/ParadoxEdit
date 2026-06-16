# gui/mod_panel.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QHeaderView
from PyQt5.QtCore import Qt, pyqtSignal
from ParadoxParser import ParadoxScriptParser as PDXScript
from gui.util import build_category_list, add_menu_heading
from traverse import apply_to_target

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
    