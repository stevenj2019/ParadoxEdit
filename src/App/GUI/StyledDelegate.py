from PyQt5.QtWidgets import QStyledItemDelegate
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor as QColour, QBrush

from App.Constants import ChangeState, STATE

class NodeStateDelegate(QStyledItemDelegate):
    def __init__(self, style_manager, parent=None):
        super().__init__(parent)
        self.style_manager = style_manager

    # def _get_colour(self, dark, light):
    #     return QColour(dark if self.config.dark_mode else light)
    
    def paint(self, painter, option, index):
        view = option.widget
        viewport_rect = view.viewport().rect()
        state = index.model().data(index, STATE)

        if not state or state == ChangeState.CLEAN:
            return 
        colour = self.style_manager.state_colour(state)

        super().paint(painter, option, index)
        print(option.palette.color(option.palette.Text).name())
        print(option.palette.color(option.palette.Base).name())

        rect = option.rect
        stripe_width = 10
        painter.save()
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(colour))
        painter.drawRect(viewport_rect.left(), rect.top(), stripe_width, rect.height())
        # painter.drawRect(rect.left()-20, rect.top(), stripe_width, rect.height())
        painter.restore()