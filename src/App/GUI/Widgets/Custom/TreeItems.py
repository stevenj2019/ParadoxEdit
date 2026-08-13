from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QIcon
from PyQt5.QtWidgets import QTreeWidgetItem

from App.GUI.Enums import QtStorage, TreeItemType
from App.Loading.Directories.Base import GenericDirectory
from App.Loading.Models import FileReference
from App.Loading.ParadoxSource import ParadoxSource


class DirectoryTreeItem(QTreeWidgetItem):
    def __init__(
        self,
        name: str,
        item: ParadoxSource | GenericDirectory | FileReference,
        item_type: TreeItemType,
        icon: QIcon = None,
    ) -> None:
        super().__init__()
        self.setText(0, name)
        self.setData(0, QtStorage.NODE, item)
        self.setData(0, QtStorage.TYPE, item_type)
        if icon:
            self.setIcon(0, icon)
        if item.read_only:
            self.setForeground(0, QBrush(Qt.gray))

    def __lt__(self, other: QTreeWidgetItem) -> bool:
        self_type = self.data(0, QtStorage.TYPE)
        other_type = other.data(0, QtStorage.TYPE)

        return (
            self_type.value < other_type.value
            if self_type != other_type
            else self.text(0).casefold() < other.text(0).casefold()
        )


# re-use this for scriptview tree
# class FileTreeItem(CustomTreeItem):
#     def __init__(self, file:FileReference, icon:QIcon) -> None:
#         super().__init__()
#         self.setText(0, file.file.filename)
#         self.setData(0, QtStorage.NODE, file)
#         self.setData(0, QtStorage.STATE, None)
#         self.setIcon(0, icon)
#         if file.read_only:
#             self.setForeground(0, QBrush(Qt.gray))
