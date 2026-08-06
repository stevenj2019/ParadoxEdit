from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App import AppController

from PyQt5.QtCore import QPoint, Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QHeaderView,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from App.Contexts import FileContext
from App.Contracts.Enums import ChangeState
from App.GUI.Enums import QtStorage, TreeItemType
from App.GUI.Menus.ContextMenus import GenericDirectoryMenu
from App.GUI.StyledDelegate import ParadoxFileDelegate
from App.GUI.Widgets.Custom.TreeItems import DirectoryTreeItem
from App.Loading.Directories.Base import GenericDirectory
from App.Loading.LoadOrder import ParadoxLoadOrder
from App.Loading.Models import FileReference
from App.Loading.ParadoxSource import ParadoxMod, ParadoxSource, ParadoxVanilla


class ModPanel(QWidget):
    request_load_block = pyqtSignal(object, bool)
    load_file = pyqtSignal()

    def __init__(self, app_controller: AppController) -> None:
        super().__init__()
        self.app_controller = app_controller
        self.node_to_item: dict = {}

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

    def populate_tree(self, load_order: ParadoxLoadOrder) -> None:
        self.tree.clear()
        for source in load_order.sources:
            self._load_source_tree(source)

    def _load_source_tree(self, source: ParadoxSource) -> None:
        root = DirectoryTreeItem(
            name=source.source_name or "Unnamed Mod",
            item=source,
            item_type=TreeItemType.SOURCE,
            icon=self.app_controller.style_manager.icon_for(source),
        )
        self.node_to_item[source] = root
        self.tree.addTopLevelItem(root)

        if isinstance(source, ParadoxMod):
            item = DirectoryTreeItem(
                name="Descriptor",
                item=source.descriptor_object,
                item_type=TreeItemType.DESCRIPTOR,
                icon=self.app_controller.style_manager.icon_for(source.descriptor_object),
            )
            self.node_to_item[source.descriptor_object] = item
            root.addChild(item)

        for entry in source.root.directories.values():
            self._build_directory_item(root, entry, isinstance(source, ParadoxVanilla))

    def _build_directory_item(
        self, parent_item: QTreeWidgetItem, directory: GenericDirectory, read_only: bool
    ) -> None:
        item = DirectoryTreeItem(
            name=directory.path.name,
            item=directory,
            item_type=TreeItemType.DIRECTORY,
            icon=self.app_controller.style_manager.icon_for(directory),
        )
        self.node_to_item[directory] = item
        parent_item.addChild(item)

        for child in directory.directories.values():
            self._build_directory_item(item, child, read_only)

        for file in directory.files.values():
            self._build_file_item(item, file, read_only)

    def _build_file_item(
        self, parent_item: QTreeWidgetItem, file: FileReference, read_only: bool
    ) -> None:
        item = DirectoryTreeItem(
            name=file.file.filename,
            item=file,
            item_type=TreeItemType.FILE,
            icon=self.app_controller.style_manager.icon_for(file),
        )
        self.node_to_item[file] = item
        parent_item.addChild(item)

    def set_file_state(self, file: FileReference, status: ChangeState) -> None:
        file_item = self.node_to_item[file]
        file_item.setData(0, QtStorage.STATE, status)
        self._propagate_state(file_item.parent())
        self.tree.update()

    def refresh_icons(self) -> None:
        for entry, item in self.node_to_item.items():
            item.setIcon(0, self.app_controller.style_manager.icon_for(entry))

    def add_folder(self, directory: GenericDirectory) -> None:
        print("ADDING FOLDER", directory.path)
        if directory in self.node_to_item.keys():
            return
        parent = directory.parent if directory.parent else directory.source

        if parent not in self.node_to_item:
            print("ADDING PARENT", parent.path)
            self.add_folder(parent)
        parent_item = self.node_to_item[parent]
        item = DirectoryTreeItem(
            name=directory.path.name,
            item=directory,
            item_type=TreeItemType.DIRECTORY,
            icon=self.app_controller.style_manager.icon_for(directory),
        )
        self.node_to_item[directory] = item
        parent_item.addChild(item)
        parent_item.sortChildren(0, Qt.AscendingOrder)

    def add_file(self, directory: GenericDirectory, file: FileReference) -> None:
        if directory not in self.node_to_item.keys():
            self.add_folder(directory)
        item = self.node_to_item[directory]
        self._build_file_item(item, file, file.read_only)
        item.sortChildren(0, Qt.AscendingOrder)

    def remove_file(self, obj: GenericDirectory | FileReference) -> None:
        if isinstance(obj, GenericDirectory):
            obj_parent = obj.parent if obj.parent else obj.source
            # parent = self.node_to_item[obj.parent if obj.parent else obj.source]
        else:
            # parent = self.node_to_item[obj.directory]
            obj_parent = obj.directory
        parent_item = self.node_to_item[obj_parent]
        item = self.node_to_item[obj]
        parent_item.removeChild(item)
        self.node_to_item.pop(obj)
        if obj_parent and parent_item.childCount() == 0:
            self.remove_file(obj.parent)

    def _propagate_state(self, item: QTreeWidgetItem) -> None:
        if item is None:
            return
        state = self._calculate_child_state(item)
        item.setData(0, QtStorage.STATE, state)
        self._propagate_state(item.parent())

    def _calculate_child_state(self, item: QTreeWidgetItem) -> None:
        for i in range(item.childCount()):
            child = item.child(i)
            if child.data(0, QtStorage.STATE) is not None:
                return ChangeState.MODIFIED
        return None

    def _on_element_click(self, item: QTreeWidgetItem, column: int) -> None:
        file = item.data(0, QtStorage.NODE)
        if file:
            if isinstance(file, GenericDirectory) or isinstance(file, ParadoxSource):
                return
            self.request_load_block.emit(file, file.read_only)

    def _request_context_menu(self, pos: QPoint) -> None:
        selected = self.tree.itemAt(pos)
        if not selected:
            return
        item = selected.data(0, QtStorage.NODE)
        if not item:
            return
        context = item.context.get_file_context()

        self.context_menu.call(FileContext(target=item, context=context))
        self.context_menu.exec_(self.tree.viewport().mapToGlobal(pos))
