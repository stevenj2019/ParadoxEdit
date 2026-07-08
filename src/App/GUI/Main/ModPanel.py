from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHeaderView, QTreeWidget, QTreeWidgetItem
from PyQt5.QtCore import Qt, pyqtSignal

from ParadoxParser import ParadoxScriptParser as PDXScript

from App.Contracts import OpenFile, FileContext
from App.Enums import QtStorage, ChangeState
from App.Modules.Base import ParadoxContext
from App.GUI.Menus.ContextMenus import GenericCategoryContextMenu
from App.GUI.StyledDelegate import ParadoxFileDelegate

class ModPanel(QWidget):
    request_load_block = pyqtSignal(object)
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
        self.tree.setItemDelegate(ParadoxFileDelegate(self.app_controller, self.tree))
        layout.addWidget(self.tree)

        self.context_menu = GenericCategoryContextMenu(self, app_controller)

        self.tree.itemClicked.connect(self._on_element_click)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._request_context_menu)

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
        if all(self.app_controller.file_system.change_tracker.get_file_state(file) == None
                for file in category.files.values()):
            category_item.setData(0, QtStorage.STATE, None)
        else:
            category_item.setData(0, QtStorage.STATE, ChangeState.MODIFIED)

    def _populate_tree(self, mod):
        self.tree.clear()

        root = QTreeWidgetItem([mod.mod_name or "Unnamed Mod"])
        self.tree.addTopLevelItem(root)

        descriptor_item = QTreeWidgetItem(["Descriptor"])

        descriptor_item.setData(0, QtStorage.FILE, mod.descriptor_object)
        descriptor_item.setData(0, QtStorage.STATE, ChangeState.CLEAN)
        descriptor_item.setData(0, QtStorage.CONTEXT, ParadoxContext)
        
        self.node_to_item[mod.descriptor_object] = descriptor_item
        root.addChild(descriptor_item)

        categories_parent = QTreeWidgetItem(["Categories"])
        root.addChild(categories_parent)

        for c_key, c_val in mod.categories.items():
            cat_sub = QTreeWidgetItem([c_key])
            context = c_val.context
            cat_sub.setData(0, QtStorage.IS_CATEGORY, True)
            cat_sub.setData(0, QtStorage.CATEGORY, c_val)
            cat_sub.setData(0, QtStorage.CONTEXT, context)

            self.node_to_item[c_val] = cat_sub
            for file, obj in c_val.files.items():
                widget = QTreeWidgetItem([file])
                self.node_to_item[obj] = widget
                self.file_to_category[obj] = cat_sub

                widget.setText(0, file)

                widget.setData(0, QtStorage.FILE, obj)
                widget.setData(0, QtStorage.STATE, None)
                widget.setData(0, QtStorage.IS_CATEGORY, False)
                widget.setData(0, QtStorage.CONTEXT, context)

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
        context = item.data(0, QtStorage.CONTEXT)
        if file:
            self.request_load_block.emit(OpenFile(file, context))

    def _request_context_menu(self, pos):
        selected = self.tree.itemAt(pos)
        if not selected:
            return
        is_category = selected.data(0, QtStorage.IS_CATEGORY)
        item = selected.data(0, QtStorage.CATEGORY) if is_category else selected.data(0, QtStorage.FILE)
        if not item:
            return
        context = selected.data(0, QtStorage.CONTEXT).get_file_context()
        
        self.context_menu.call(FileContext(target=item, context=context))
        self.context_menu.exec_(self.tree.viewport().mapToGlobal(pos))
