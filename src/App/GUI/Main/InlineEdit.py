from typing import Callable

from PyQt5.QtCore import QEvent, QObject
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QLineEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QWidget,
)

from App.Contracts import InLineEditRequest, NodeMutationRequest
from App.Contracts.Enums import TargetProperty
from App.GUI.Widgets.PopupModels import change_rejected_warning
from App.Services import AppLogger
from ParadoxParser.ParadoxNodes import (
    GenericBool,
    GenericComment,
    GenericFloat,
    GenericInt,
    GenericKeyValue,
    GenericNode,
    GenericString,
    GenericToken,
)


class InLineEditManager(QObject):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.cell_editors = {
            GenericKeyValue: text_editor,
            GenericComment: text_editor,
            GenericString: text_editor,
            GenericToken: text_editor,
            GenericInt: int_editor,
            GenericFloat: float_editor,
            GenericBool: bool_dropdown,
        }
        self.mutate_callback = parent.app_controller.request_node_mutation
        self.tree: QTreeWidget = None
        self.item: QTreeWidgetItem = None
        self.node: GenericNode = None
        self.editor: QWidget = None

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.FocusOut:
            if isinstance(self.editor, QComboBox) and self.editor.view().isVisible():
                return False

            next_widget = QApplication.focusWidget()

            if next_widget and (
                next_widget is self.editor or self.editor.isAncestorOf(next_widget)
            ):
                return False

            self.cancel_request("focus lost")
            return False

        return False

    @property
    def active(self) -> bool:
        return self.editor is not None

    def open_request(self, request: InLineEditRequest) -> None:
        self.tree = request.tree
        self.item = request.item
        self.node = request.node
        self.target = request.target

        self.column = 0 if self.target is TargetProperty.KEY else 1
        self.editor = self._get_widget()
        self._create()

    def complete_request(self, new_value: str) -> None:
        self.mutate_callback.emit(
            NodeMutationRequest(None, self.node, self.target, new_value)
        )
        self._destroy(new_value)
        self._clear()

    def cancel_request(self, reason: str) -> None:
        if self.active:
            value = (
                self.node.key if self.target is TargetProperty.KEY else self.node.value
            )
            AppLogger.info(f"{self.editor} cancelled due to {reason}, value: {value}")
            self._destroy(value)
        self._clear()

    def _get_widget(self) -> QWidget:
        def emit(value: str | bool) -> None:
            self.complete_request(value)

        try:
            editor_fn = self.cell_editors.get(type(self.node))
        except Exception as e:
            AppLogger.exception(e)
            return None
        value = (
            self.node.value if self.target is TargetProperty.VALUE else self.node.key
        )
        return editor_fn(self, self.node, emit, value)

    def _create(self) -> None:
        self.tree.setItemWidget(self.item, self.column, self.editor)
        self.editor.setFocus()

        self.editor.installEventFilter(self)
        AppLogger.info(f"{self.editor} created")

    def _destroy(self, value: str = None) -> None:
        self.tree.removeItemWidget(self.item, self.column)
        self.item.setText(self.column, value)
        self.editor.deleteLater()

    def _clear(self) -> None:
        self.tree = None
        self.item = None
        self.node = None
        self.editor = None


def text_editor(
    editor: QObject, node: GenericNode, emit: Callable, value: str
) -> QLineEdit:
    widget = QLineEdit(str(value))
    width = QFontMetrics(widget.font()).horizontalAdvance(widget.text()) + 20
    widget.setFixedWidth(max(60, min(width, 500)))

    def on_change() -> None:
        emit(widget.text())

    widget.editingFinished.connect(on_change)
    return widget


def bool_dropdown(
    editor: QObject, node: GenericNode, emit: Callable, value: str
) -> QComboBox:
    widget = QComboBox()
    widget.addItems(["yes", "no"])
    widget.setCurrentIndex(0 if value else 1)
    widget.setFixedWidth(70)

    def on_change(index: int) -> None:
        emit(index == 0)

    widget.currentIndexChanged.connect(on_change)
    return widget


def int_editor(
    editor: QObject, node: GenericNode, emit: Callable, value: str
) -> QLineEdit:
    widget = QLineEdit(str(value))
    width = QFontMetrics(widget.font()).horizontalAdvance(widget.text()) + 20
    widget.setFixedWidth(max(60, min(width, 500)))

    def on_change() -> None:
        try:
            output = int(widget.text())
        except ValueError:
            output = node.value
            change_rejected_warning(
                editor.parent(),
                f"Input {widget.text()} is invalid, should be similar to {node.value}",
            )
        emit(output)

    widget.editingFinished.connect(on_change)
    return widget


def float_editor(
    editor: QObject, node: GenericNode, emit: Callable, value: str
) -> QLineEdit:
    widget = QLineEdit(str(value))
    width = QFontMetrics(widget.font()).horizontalAdvance(widget.text()) + 20
    widget.setFixedWidth(max(60, min(width, 500)))

    def on_change() -> None:
        try:
            output = float(widget.text())
        except ValueError:
            output = node.value
            change_rejected_warning(
                editor.parent(),
                f"Input {widget.text()} is invalid, should be similar to {node.value}",
            )
        emit(output)

    widget.editingFinished.connect(on_change)
    return widget
