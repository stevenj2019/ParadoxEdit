from PyQt5.QtWidgets import QLineEdit, QComboBox
from PyQt5.QtGui import QFontMetrics
from gui.warning_messages import change_rejected_warning
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