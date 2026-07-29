from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App import AppController

from PyQt5.QtCore import QPoint, Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication,
    QHeaderView,
    QStyle,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from App.Contexts import FileContext
from App.Contexts.Base import ParadoxContext
from App.Contracts.Enums import ChangeState
from App.GUI.Enums import QtStorage
from App.GUI.Menus.ContextMenus import GenericDirectoryMenu
from App.GUI.StyledDelegate import ParadoxFileDelegate
from App.Loading.Directories.Base import GenericDirectory
from App.Loading.LoadOrder import ParadoxLoadOrder
from App.Loading.Models import FileReference, UnloadedFile
from App.Loading.ParadoxSource import ParadoxMod, ParadoxSource, ParadoxVanilla


class ModPanel(QWidget):
    request_load_block = pyqtSignal(object, bool)
    load_file = pyqtSignal()
    def __init__(self, app_controller:AppController) -> None:
        super().__init__()
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

    def set_file_state(self, file:FileReference, status:ChangeState) -> None:
        file_item = self.node_to_item[file]
        file_item.setData(0, QtStorage.STATE, status)
        self._propagate_state(file_item.parent())
        self.tree.update()

    def add_file(self, directory:GenericDirectory, file:FileReference) -> None:
        item = self.node_to_item[directory]
        self._build_file_item(item, file, file.read_only)

    def _propagate_state(self, item:QTreeWidgetItem) -> None:
        if item is None:
            return 
        state = self._calculate_child_state(item)
        item.setData(0, QtStorage.STATE, state)
        self._propagate_state(item.parent())

    def _calculate_child_state(self, item:QTreeWidgetItem) -> None:
        for i in range(item.childCount()):
            child = item.child(i)
            if child.data(0, QtStorage.STATE) is not None:
                return ChangeState.MODIFIED
        return None

    def populate_tree(self, load_order:ParadoxLoadOrder) -> None:
        self.tree.clear()
        for source in load_order.sources:
            self._load_source_tree(source)

    def _load_source_tree(self, source:ParadoxSource) -> None:
        root = QTreeWidgetItem([source.source_name or "Unnamed Mod"])
        root.setData(0, QtStorage.NODE, source)
        self.tree.addTopLevelItem(root)

        if isinstance(source, ParadoxMod):
            descriptor_item = QTreeWidgetItem(["Descriptor"])
            descriptor_item.setData(0, QtStorage.NODE, source.descriptor_object)
            descriptor_item.setData(0, QtStorage.STATE, None)
            descriptor_item.setData(0, QtStorage.CONTEXT, ParadoxContext)
            descriptor_item.setData(0, QtStorage.READ_ONLY, False)
            self.node_to_item[source.descriptor_object.file] = descriptor_item

            root.addChild(descriptor_item)

        for entry in source.root.directories.values():
            self._build_directory_item(root, entry, isinstance(source, ParadoxVanilla))

    def _build_directory_item(self, parent_item:QTreeWidgetItem, directory:GenericDirectory, read_only:bool)-> None:
        read_only = read_only or directory.read_only
        item = QTreeWidgetItem([directory.path.name])
        self.node_to_item[directory] = item
        item.setData(0, QtStorage.NODE, directory)
        item.setData(0, QtStorage.READ_ONLY, read_only)
        item.setIcon(0, self.app_controller.style_manager.get_icon(GenericDirectory))
        parent_item.addChild(item)

        for child in directory.directories.values():
            self._build_directory_item(item, child, read_only)

        for file in directory.files.values():
            self._build_file_item(item, file, read_only)

    def _build_file_item(self, parent_item:QTreeWidgetItem, file:FileReference, read_only:bool) -> None:
        con_text = file.context.__name__ if file.context else None
    
        text = f"{file.file.filename}, {con_text}{'(ReadOnly)' if read_only else ''}"
        item = QTreeWidgetItem([text])
        self.node_to_item[file] = item
        if isinstance(file.file, UnloadedFile):
            item.setIcon(0, QApplication.style().standardIcon(QStyle.SP_MessageBoxWarning))
        item.setData(0, QtStorage.NODE, file)
        item.setData(0, QtStorage.STATE, None)
        item.setData(0, QtStorage.READ_ONLY, read_only)
        item.setIcon(0, self.app_controller.style_manager.get_icon(type(file.file)))
        parent_item.addChild(item)

    def _on_element_click(self, item:QTreeWidgetItem, column:int) -> None:
        file = item.data(0, QtStorage.NODE)
        if file:
            if isinstance(file, GenericDirectory) or isinstance(file, ParadoxSource):
                return
            self.request_load_block.emit(file, item.data(0, QtStorage.READ_ONLY))

    def _request_context_menu(self, pos:QPoint):
        selected = self.tree.itemAt(pos)
        if not selected:
            return
        item = selected.data(0, QtStorage.NODE)
        if not item:
            return
        context = item.context.get_file_context()
        
        self.context_menu.call(FileContext(target=item, context=context))
        self.context_menu.exec_(self.tree.viewport().mapToGlobal(pos))
