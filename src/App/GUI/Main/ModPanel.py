from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHeaderView, QTreeWidget, QTreeWidgetItem, QStyle
from PyQt5.QtCore import Qt, pyqtSignal

from App.Loading.ParadoxSource import ParadoxMod
from App.Contexts import FileContext
from App.Loading.Directories.Base import GenericDirectory
from App.Loading.Models import UnloadedFile
from App.Contracts import OpenFile
from App.Contracts.Enums import ChangeState
from App.GUI.Enums import QtStorage
from App.Contexts.Base import ParadoxContext
from App.GUI.Menus.ContextMenus import GenericDirectoryMenu
from App.GUI.StyledDelegate import ParadoxFileDelegate

class ModPanel(QWidget):
    request_load_block = pyqtSignal(object)
    load_file = pyqtSignal()
    def __init__(self, parent, app_controller):
        super().__init__()
        self.parent = parent
        self.app_controller = app_controller
        self.node_to_item:dict = {}

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

        self.context_menu = GenericDirectoryMenu(self, app_controller)

        self.tree.itemClicked.connect(self._on_element_click)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._request_context_menu)

    def set_file_state(self, file, status):
        file_item = self.node_to_item[file]
        file_item.setData(0, QtStorage.STATE, status)
        self._propagate_state(file_item.parent())
        self.tree.update()

    def _propagate_state(self, item):
        if item is None:
            return 
        state = self._calculate_child_state(item)
        item.setData(0, QtStorage.STATE, state)
        self._propagate_state(item.parent())

    def _calculate_child_state(self, item):
        for i in range(item.childCount()):
            child = item.child(i)
            if child.data(0, QtStorage.STATE) is not None:
                return ChangeState.MODIFIED
        return None

    def populate_tree(self, load_order):
        self.tree.clear()
        for source in load_order.sources:
            self._load_source_tree(source)

    def _load_source_tree(self, source):
        root = QTreeWidgetItem([source.source_name or "Unnamed Mod"])
        root.setData(0, QtStorage.NODE, source)
        self.tree.addTopLevelItem(root)

        if isinstance(source, ParadoxMod):
            descriptor_item = QTreeWidgetItem(["Descriptor"])
            descriptor_item.setData(0, QtStorage.NODE, source.descriptor_object)
            descriptor_item.setData(0, QtStorage.STATE, None)
            descriptor_item.setData(0, QtStorage.CONTEXT, ParadoxContext)
            descriptor_item.setData(0, QtStorage.READ_ONLY, False)
            self.node_to_item[source.descriptor_object] = descriptor_item

            root.addChild(descriptor_item)
        for entry in source.root.directories.values():
            self._add_directory(root, entry, None, None)

    def _add_directory(self, parent_item, directory, context, read_only):
        context = directory.context if not context else context
        read_only = directory.read_only if not read_only else read_only
        con_text = context.__name__ if directory.context else None
        text = f"{directory.path.name}, {con_text}"
        item = QTreeWidgetItem([text])
        self.node_to_item[directory] = item
        item.setData(0, QtStorage.NODE, directory)
        item.setData(0, QtStorage.STATE, None) #i am unsure if this is needed here or not....
        item.setData(0, QtStorage.CONTEXT, context)
        item.setData(0, QtStorage.READ_ONLY, read_only)
        parent_item.addChild(item)

        for child in directory.directories.values():
            self._add_directory(item, child, context, read_only)

        for file in directory.files.values():
            self._add_file(item, file, context, read_only)

    def _add_file(self, parent_item, file, context, read_only):
        con_text = context.__name__ if context else None
        text = f"{file.filename}, {con_text}"
        item = QTreeWidgetItem([text])
        self.node_to_item[file] = item
        if isinstance(file, UnloadedFile):
            item.setIcon(0, QApplication.style().standardIcon(QStyle.SP_MessageBoxWarning))
        item.setData(0, QtStorage.NODE, file)
        item.setData(0, QtStorage.STATE, None)
        item.setData(0, QtStorage.CONTEXT, context)
        item.setData(0, QtStorage.READ_ONLY, read_only)
        parent_item.addChild(item)

    def _on_element_click(self, item, column):
        file = item.data(0, QtStorage.NODE)
        context = item.data(0, QtStorage.CONTEXT)
        if file:
            if isinstance(file, GenericDirectory):
                return
            self.request_load_block.emit(OpenFile(file, context))

    #TODO this is also shit housed lol
    def _request_context_menu(self, pos):
        selected = self.tree.itemAt(pos)
        if not selected:
            return
        # is_category = selected.data(0, QtStorage.IS_CATEGORY)
        # item = selected.data(0, QtStorage.CATEGORY) if is_category else selected.data(0, QtStorage.FILE)
        item = selected.data(0, QtStorage.NODE)
        if not item:
            return
        context = selected.data(0, QtStorage.CONTEXT)
        if not context:
            return 
        context = context.get_file_context()
        
        self.context_menu.call(FileContext(target=item, context=context))
        self.context_menu.exec_(self.tree.viewport().mapToGlobal(pos))
