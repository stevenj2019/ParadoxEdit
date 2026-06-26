from PyQt5.QtWidgets import QStyledItemDelegate
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor as QColour, QBrush

from App.Constants import ChangeState, STATE

class NodeStateDelegate(QStyledItemDelegate):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config

    def _get_colour(self, dark, light):
        return QColour(dark if self.config.dark_mode else light)
    
    def paint(self, painter, option, index):
        view = option.widget
        viewport_rect = view.viewport().rect()
        state = index.model().data(index, STATE)
        
        print(f"painting {index.row()}, {index.column()}, {state}")
        super().paint(painter, option, index)

        # if state is not ChangeState.CLEAN or state is not None:
        # if state == (ChangeState.CLEAN or None):
        # if state is not ChangeState.CLEAN or None:
        match state:
            case ChangeState.MODIFIED:
                colour = self._get_colour("#545703", "yellow")
            case ChangeState.ADDED:
                colour = self._get_colour("#04450c", "green")
            case ChangeState.DELETED:
                colour = self._get_colour("#400308", "red")
            case ChangeState.CLEAN|None:
                return 
        rect = option.rect
        stripe_width = 10
        painter.save()
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(colour))
        painter.drawRect(viewport_rect.left(), rect.top(), stripe_width, rect.height())
        # painter.drawRect(rect.left()-20, rect.top(), stripe_width, rect.height())
        painter.restore()