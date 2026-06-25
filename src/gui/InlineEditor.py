from PyQt5.QtWidgets import (QMainWindow, QTreeWidget, QTreeWidgetItem, QWidget,
                             QLineEdit, QComboBox)
from PyQt5.QtGui import QFontMetrics

from ParadoxParser.ParadoxNodes import (GenericKeyValue, GenericNode,
                                        GenericComment, GenericString, GenericToken, 
                                        GenericInt, GenericFloat, GenericBool)

from gui.dialogues.warning_messages import change_rejected_warning
class InlineEditManager:
    def __init__(self, main_controller:QMainWindow):
        self.cell_editors = {
            GenericComment: text_editor,
            GenericString:  text_editor,
            GenericToken:   text_editor,
            GenericInt:     int_editor,
            GenericFloat:   float_editor,
            GenericBool:    bool_dropdown
        }
        self.main_controller = main_controller
        self.parent:QTreeWidget = None
        self.source:QTreeWidgetItem = None
        self.node:GenericNode = None
        self.editor:QWidget = None

    @property
    def active(self): return self.editor is not None

    def open_request(self,
                parent:QTreeWidget, 
                source:QTreeWidgetItem, 
                node:GenericNode|GenericKeyValue):
        if self.active:
            print("open_request when already open")
            pass #manage destruction pipeline
        self.parent = parent
        self.source = source
        self.node = node.value if isinstance(node, GenericKeyValue) else node
        self.editor = self._get_widget()
        print(f"{self.editor} created")
        self._create()

    def complete_request(self, new_value):
        print(f"{self.node}, {self.node.value} to {new_value}")
        if self.node.value != new_value:
            self.main_controller._mutate_node(self.node, new_value)
        self.source.setText(1, self.node._get_value())
        self._destroy()
        self._clear()

    def cancel_request(self, reason):
        if self.active:
            print(f"{self.editor} cancelled due to {reason}, value: {self.node.value}")
            self._destroy()
        self._clear()

    def _get_widget(self):
        def emit(value):
            self.complete_request(value)
        try:
            editor_fn = self.cell_editors.get(type(self.node))
        except Exception as e:
            print(e)
            return None
        return editor_fn(self.node, emit)

    def _create(self):
        self.parent.setItemWidget(self.source, 1, self.editor)
        self.editor.setFocus()

    def _destroy(self):
        self.parent.removeItemWidget(self.source, 1)
        self.editor.deleteLater()

    def _clear(self):
        self.parent = None
        self.source = None
        self.node = None
        self.editor = None

def text_editor(node, emit):
    widget = QLineEdit(str(node.value))
    width = QFontMetrics(widget.font()).horizontalAdvance(widget.text())+20
    widget.setFixedWidth(max(60, min(width, 500)))

    def on_change():
        emit(widget.text())

    widget.editingFinished.connect(on_change)
    return widget

def bool_dropdown(node, emit):
    widget = QComboBox()
    widget.addItems(["yes", "no"])
    widget.setCurrentIndex(0 if node.value else 1)
    widget.setFixedWidth(70)
    
    def on_change(index):
        emit(index == 0)

    widget.currentIndexChanged.connect(on_change)
    return widget

def int_editor(node, emit):
    widget = QLineEdit(str(node.value))
    width = QFontMetrics(widget.font()).horizontalAdvance(widget.text())+20
    widget.setFixedWidth(max(60, min(width, 500)))

    def on_change():
        try:
            output = int(widget.text())
        except ValueError:
            output = node.value
            change_rejected_warning(f"Input {widget.text()} is invalid, should be similar to {node.value}")
        emit(output)

    widget.editingFinished.connect(on_change)
    return widget

def float_editor(node, emit):
    widget = QLineEdit(str(node.value))
    width = QFontMetrics(widget.font()).horizontalAdvance(widget.text())+20
    widget.setFixedWidth(max(60, min(width, 500)))

    def on_change():
        try:
            output = float(widget.text())
        except ValueError:
            output = node.value
            change_rejected_warning(f"Input {widget.text()} is invalid, should be similar to {node.value}")
        emit(output)

    widget.editingFinished.connect(on_change)
    return widget