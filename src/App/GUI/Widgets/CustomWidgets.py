from typing import Any

from PyQt5.QtCore import QEvent, QModelIndex, QObject, QSize, Qt, pyqtSignal
from PyQt5.QtGui import QFontMetrics, QStandardItem
from PyQt5.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from App.GUI.Widgets.FileDialogues import (
    gfx_files_file_selector,
    gfx_files_folder_selector,
)


class FileFolderSelectorWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._file_list = list()

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.file_list_item = QTreeWidget()
        self.file_list_item.setColumnCount(1)
        self.file_list_item.setHeaderLabel("Folder(s)")
        self.layout.addWidget(self.file_list_item)

        self.buttons = QHBoxLayout()
        self.add_folder_button = QPushButton("Add Folder", self)
        self.add_folder_button.clicked.connect(self._add_folder_to_input_list)
        self.buttons.addWidget(self.add_folder_button)
        self.add_file_button = QPushButton("Add File", self)
        self.add_file_button.clicked.connect(self._add_file_to_input_list)
        self.buttons.addWidget(self.add_file_button)
        self.remove_entry_button = QPushButton("Delete Selected", self)
        self.remove_entry_button.clicked.connect(self._remove_selected_from_input_list)
        self.buttons.addWidget(self.remove_entry_button)
        self.layout.addLayout(self.buttons)

    @property
    def file_list(self) -> list[str]:
        return self._file_list

    def _add_folder_to_input_list(self) -> None:
        path, exists = gfx_files_folder_selector(self)
        if exists:
            self._file_list.append(path)
            item = QTreeWidgetItem([path])
            self.file_list_item.invisibleRootItem().addChild(item)

    def _add_file_to_input_list(self) -> None:
        path, exists = gfx_files_file_selector(self)
        if exists:
            self._file_list.append(path)
            item = QTreeWidgetItem([path])
            self.file_list_item.invisibleRootItem().addChild(item)

    def _remove_selected_from_input_list(self) -> None:
        item = self.file_list_item.currentItem()
        if item is None:
            return
        index = self.file_list_item.indexOfTopLevelItem(item)
        if index == -1:
            return
        self._file_list.pop(index)
        self.file_list_item.takeTopLevelItem(index)


class CheckableComboBox(QComboBox):
    class Delegate(QStyledItemDelegate):
        def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:
            size = super().sizeHint(option, index)
            size.setHeight(20)
            return size

    def __init__(self) -> None:
        super().__init__()

        self.setEditable(True)
        self.lineEdit().setReadOnly(True)

        self.setItemDelegate(CheckableComboBox.Delegate())

        self.model().dataChanged.connect(self.updateText)

        self.lineEdit().installEventFilter(self)
        self.closeOnLineEditClick = False

        self.view().viewport().installEventFilter(self)

    def resizeEvent(self, event: QEvent):
        self.updateText()
        super().resizeEvent(event)

    def eventFilter(self, object: QObject, event: QEvent) -> bool:
        if object == self.lineEdit():
            if event.type() == QEvent.MouseButtonRelease:
                if self.closeOnLineEditClick:
                    self.hidePopup()
                else:
                    self.showPopup()
                return True
            return False

        if object == self.view().viewport():
            if event.type() == QEvent.MouseButtonRelease:
                index = self.view().indexAt(event.pos())
                item = self.model().item(index.row())

                if item.checkState() == Qt.Checked:
                    item.setCheckState(Qt.Unchecked)
                else:
                    item.setCheckState(Qt.Checked)
                return True
        return False

    def showPopup(self) -> None:
        super().showPopup()
        self.closeOnLineEditClick = True

    def hidePopup(self) -> None:
        super().hidePopup()
        self.startTimer(100)
        self.updateText()

    def timerEvent(self, event: QEvent) -> None:
        self.killTimer(event.timerId())
        self.closeOnLineEditClick = False

    def updateText(self) -> None:
        texts = []
        checked = 0
        total = self.model().rowCount()

        for i in range(self.model().rowCount()):
            if self.model().item(i).checkState() == Qt.Checked:
                texts.append(self.model().item(i).text())
                checked += 1

        text = "All" if checked == 0 or checked is total else ", ".join(texts)
        metrics = QFontMetrics(self.lineEdit().font())
        elidedText = metrics.elidedText(text, Qt.ElideRight, self.lineEdit().width())
        self.lineEdit().setText(elidedText)

    def addItem(self, text: str, data: Any = None) -> None:
        item = QStandardItem()
        item.setText(text)
        if data is None:
            item.setData(text)
        else:
            item.setData(data)
        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
        item.setData(Qt.Unchecked, Qt.CheckStateRole)
        self.model().appendRow(item)

    def currentData(self) -> None:
        res = []
        for i in range(self.model().rowCount()):
            if self.model().item(i).checkState() == Qt.Checked:
                res.append(self.model().item(i).data())
        return res


class SearchLineEdit(QLineEdit):
    caseChanged = pyqtSignal(bool)
    regexChanged = pyqtSignal(bool)

    def __init__(self) -> None:
        super().__init__()
        self.buttons = list()

        self.case_button = QPushButton("Aa", self)
        self.case_button.setCheckable(True)
        self.case_button.setToolTip("Case-Sensitive")
        self.case_button.toggled.connect(self.caseChanged.emit)
        self.buttons.append(self.case_button)

        self.regex_button = QPushButton(".*", self)
        self.regex_button.setCheckable(True)
        self.regex_button.setToolTip("Regex")
        self.regex_button.toggled.connect(self.regexChanged.emit)
        self.buttons.append(self.regex_button)

    def resizeEvent(self, event: QEvent) -> None:
        super().resizeEvent(event)
        button_width = 32
        margin = 2
        spacing = 2
        x = self.width() - margin
        for button in self.buttons:
            x -= button_width
            button.setGeometry(x, margin, button_width, self.height() - (margin * 2))
            x -= spacing
            button.raise_()
        button_space = (
            len(self.buttons) * button_width
            + max(0, len(self.buttons) - 1) * spacing
            + margin
        )
        self.setTextMargins(0, 0, button_space, 0)
