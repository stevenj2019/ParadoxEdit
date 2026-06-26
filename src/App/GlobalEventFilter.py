from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, QEvent, pyqtSignal

class GlobalEventFilter(QObject):
    def __init__(self, cancel_callback):
        super().__init__()
        self.cancel_callback = cancel_callback

    global_edit_cancel_request = pyqtSignal(str)
    def InlineEditEventFilter(self, obj, event):
        def _focus_inside_editor():
            editor = self.editor_session.editor
            if editor is None:
                return False
            widget = QApplication.focusWidget()
            while widget is not None:
                if widget is editor:
                    return True
                widget = widget.parent()

            return False
        
        if event.type() in (
            QEvent.MouseButtonPress, 
            QEvent.MouseButtonDblClick
        ):
            if _focus_inside_editor():
                return super().eventFilter(obj, event)
            
            self.cancel_callback("global click-away")
        
        return super().eventFilter(obj, event)
