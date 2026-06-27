from PyQt5.QtWidgets import QStyledItemDelegate
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor as QColour, QBrush, QPen

from App.Constants import ChangeState, STATE, IS_CATEGORY

class ParadoxFileDelegate(QStyledItemDelegate):
    def __init__(self, style_manager, parent=None):
        super().__init__(parent)
        self.style_manager = style_manager

    def paint(self, painter, option, index):
        super().paint(painter, option, index)
        is_category = index.model().data(index, IS_CATEGORY)
        state = index.model().data(index, STATE)

        radius = 4
        painter.save()
        painter.setRenderHint(painter.Antialiasing, True)
        x = option.rect.right() - radius * 2 - 6
        y = option.rect.center().y()

        if is_category:
            state = index.model().data(index, STATE)
            if state == ChangeState.MODIFIED:
                colour = self.style_manager.get_node_state_colour(ChangeState.MODIFIED)
                painter.setBrush(Qt.NoBrush)
                painter.setPen(QPen(colour, 2))
                painter.drawEllipse(x, y - radius, radius * 2, radius * 2)
                # painter.restore()
        else:
            state = index.model().data(index, STATE)
            if state in (ChangeState.ADDED, ChangeState.MODIFIED, ChangeState.DELETED):
                colour = self.style_manager.get_node_state_colour(state)
                painter.setPen(Qt.NoPen)
                painter.setBrush(QColour(colour))
                painter.drawEllipse(x, y-radius, radius*2, radius*2)
                # painter.restore()
        painter.restore()

class NodeStateDelegate(QStyledItemDelegate):
    def __init__(self, style_manager, parent=None):
        super().__init__(parent)
        self.style_manager = style_manager

    def paint(self, painter, option, index):
        super().paint(painter, option, index)
        state = index.model().data(index, STATE)

        if state in (ChangeState.ADDED, ChangeState.MODIFIED, ChangeState.DELETED):
            colour = self.style_manager.get_node_state_colour(state)

            view = option.widget
            viewport_rect = view.viewport().rect()

            rect = option.rect
            
            stripe_width = 10
            
            painter.save()
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(colour))
            painter.drawRect(viewport_rect.left(), rect.top(), stripe_width, rect.height())
            painter.restore()