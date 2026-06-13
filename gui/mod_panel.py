# gui/mod_panel.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QHeaderView
from PyQt5.QtCore import Qt
from ParadoxParser import ParadoxScriptParser
# from gui.widgets import ModPanelClickableItem
from gui.util import build_category_list

class ModPanel(QWidget):
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
        # self.tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tree.setTextElideMode(Qt.ElideRight)
        
        layout.addWidget(self.tree)

        self._populate_tree()

    def _populate_tree(self):
        self.tree.clear()

        # Root: Mod name
        root = QTreeWidgetItem([self.mod.mod_name or "Unnamed Mod"])
        self.tree.addTopLevelItem(root)

        # Descriptor node
        descriptor_item = QTreeWidgetItem(["Descriptor"])
        descriptor_item.setData(0, Qt.UserRole, self.mod.descriptor_object)
        root.addChild(descriptor_item)

        # Categories parent
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

        # i will place this elsewhere eventually
        # Debug-only error visibility
        if self.mod.error_categories:
            print("Failed categories:")
            for name in self.mod.error_categories:
                print(f" - {name}")