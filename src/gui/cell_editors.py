from PyQt5.QtWidgets import QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox
from PyQt5.QtGui import QFontMetrics
def text_editor(node):
    widget = QLineEdit(str(node.value))

    def update(n=node, w=widget):
        n.value = w.text()

    widget.editingFinished.connect(update)
    width = QFontMetrics(widget.font()).horizontalAdvance(widget.text())+20
    widget.setFixedWidth(max(60, min(width, 500)))
    return widget

def bool_dropdown(node):
    widget = QComboBox()
    widget.addItems(["yes", "no"])
    widget.setCurrentIndex(0 if node.value else 1)
    
    def update(n=node, w=widget):
        n.value = w==0

    widget.currentIndexChanged.connect(update)
    widget.setFixedWidth(70)
    return widget

def int_editor(node):
    widget = QLineEdit(str(node.value))

    def update(n=node, w=widget):
        try:
            n.value = int(w.text())
        except ValueError:
            w.setText(str(node.value))

    widget.editingFinished.connect(update)
    width = QFontMetrics(widget.font()).horizontalAdvance(widget.text())+20
    widget.setFixedWidth(max(60, min(width, 500)))
    return widget

def float_editor(node):
    widget = QLineEdit(str(node.value))

    def update(n=node, w=widget):
        try:
            n.value = float(w.text())
        except ValueError:
            w.setText(str(node.value))

    widget.editingFinished.connect(update)
    width = QFontMetrics(widget.font()).horizontalAdvance(widget.text())+20
    widget.setFixedWidth(max(60, min(width, 500)))
    return widget