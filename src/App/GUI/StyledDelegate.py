from PyQt5.QtWidgets import QApplication, QStyle, QStyledItemDelegate, QToolTip
from PyQt5.QtCore import Qt, QRect, QEvent
from PyQt5.QtGui import QColor as QColour, QBrush, QPen

from ParadoxParser import ParadoxScriptParser as PDXScriptFile
from ParadoxParser import ParadoxLocParser as PDxLocFile

from App.GUI.Enums import QtStorage
from App.Contracts.Enums import ChangeState

from App.Contexts.Event import EventOptionContext #added for debug purposes

class ParadoxFileDelegate(QStyledItemDelegate):
    def __init__(self, app_controller, parent=None):
        super().__init__(parent)
        self.app_controller = app_controller

    def paint(self, painter, option, index):
        super().paint(painter, option, index)

        radius = 4
        painter.save()
        painter.setRenderHint(painter.Antialiasing, True)
        x = option.rect.right() - radius * 2 - 6
        y = option.rect.center().y()

        node = index.model().data(index, QtStorage.NODE)
        if isinstance(node, PDXScriptFile) or isinstance(node, PDxLocFile):
            state = index.model().data(index, QtStorage.STATE)
            if state in (ChangeState.ADDED, ChangeState.MODIFIED, ChangeState.DELETED):
                colour = self.app_controller.style_manager.get_node_state_colour(state)
                painter.setPen(Qt.NoPen)
                painter.setBrush(QColour(colour))
                painter.drawEllipse(x, y-radius, radius*2, radius*2)
        else:
            state = index.model().data(index, QtStorage.STATE)
            if state == ChangeState.MODIFIED:
                colour = self.app_controller.style_manager.get_node_state_colour(ChangeState.MODIFIED)
                painter.setBrush(Qt.NoBrush)
                painter.setPen(QPen(colour, 2))
                painter.drawEllipse(x, y - radius, radius * 2, radius * 2)
        painter.restore()
        
class NodeStateDelegate(QStyledItemDelegate):
    def __init__(self, app_controller, parent=None):
        super().__init__(parent)
        self.app_controller = app_controller

    def paint(self, painter, option, index):
        super().paint(painter, option, index)
        self.paint_change_state(painter, option, index)
        self.paint_error_icon(painter, option, index)

    def paint_change_state(self, painter, option, index):
        state = index.model().data(index, QtStorage.STATE)

        if state in (ChangeState.ADDED, ChangeState.MODIFIED, ChangeState.DELETED):
            colour = self.app_controller.style_manager.get_node_state_colour(state)

            view = option.widget
            viewport_rect = view.viewport().rect()

            rect = option.rect
            
            stripe_width = 5
            
            painter.save()
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(colour))
            painter.drawRect(viewport_rect.left(), rect.top(), stripe_width, rect.height())
            painter.restore()

    def paint_error_icon(self, painter, option, index):
        if index.column() != 1:
            return 
        
        source_index = index.sibling(index.row(), 0)
        is_block = source_index.model().data(source_index, QtStorage.IS_BLOCK)
        is_comparator = source_index.model().data(source_index, QtStorage.IS_COMPARATOR)
        if not (is_block or is_comparator):
            node = source_index.model().data(source_index, QtStorage.NODE)
            context = source_index.model().data(source_index, QtStorage.CONTEXT)
            error = context.errors(self.app_controller, node.value)
            if error:
                icon = QApplication.style().standardIcon(QStyle.SP_MessageBoxWarning)
                icon_size = 16

                font_metrics = option.fontMetrics
                text = index.data(Qt.DisplayRole)
                text_width = font_metrics.horizontalAdvance(str(text))

                rect = option.rect
                x = rect.left() + text_width + 10
                y = rect.center().y() - icon_size // 2
                icon.paint(
                    painter, 
                    QRect(x, y, icon_size, icon_size)
                )

    def helpEvent(self, event, view, option, index):
        if event.type() == QEvent.ToolTip:
            if index.column() == 1:
                source_index = index.sibling(index.row(), 0)
                node = source_index.model().data(source_index, QtStorage.NODE)
                context = source_index.model().data(source_index, QtStorage.CONTEXT)
                #debug block
                if isinstance(context, EventOptionContext):
                    print()
                #end of debug block
                error = context.errors(self.app_controller, node.value)
                if error:
                    QToolTip.showText(
                        event.globalPos(),
                        error, 
                        view
                    )
                    return True
        return super().helpEvent(event, view, option, index)