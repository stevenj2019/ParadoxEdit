from PyQt5.QtWidgets import QStyledItemDelegate
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor as QColour, QBrush

from App.Constants import ChangeState, STATE

class NodeStateDelegate(QStyledItemDelegate):
    def __init__(self, style_manager, parent=None):
        super().__init__(parent)
        self.style_manager = style_manager

    def paint(self, painter, option, index):
        super().paint(painter, option, index)
        state = index.model().data(index, STATE)

        if not state or state == ChangeState.CLEAN:
            return 
        colour = self.style_manager.get_state_colour(state)

        print(option.palette.color(option.palette.Text).name())
        print(option.palette.color(option.palette.Base).name())

        view = option.widget
        viewport_rect = view.viewport().rect()
        rect = option.rect
        stripe_width = 10
        painter.save()
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(colour))
        painter.drawRect(viewport_rect.left(), rect.top(), stripe_width, rect.height())
        painter.restore()