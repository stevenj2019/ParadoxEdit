from PyQt5.QtWidgets import QMessageBox

def edit_warning_if_clean(parent, func, text:str="This will modify your files, if you save it this will be irreversible."):
    """
    Returns a callable that shows a warning dialog before running func.
    
    Usage:
    menu.addAction(
        "Clear Comments",
        edit_warning_if_clean(   parent, 
                        lambda: clear_all_comments(category), 
                        text="This will remove all comments!")
        )
    """
    def wrapper():
        if parent.safe_mode == False or parent.been_modified == False:
            reply = QMessageBox.question(
                parent,
                "Warning",
                text,
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                return func()
        else:
            return func()
    return wrapper


def toggle_safe_mode_warning(parent):
    if parent.safe_mode:
        reply = QMessageBox.question(
            parent, 
            "warning", 
            "This will disable safe mode, which allows for .bak generation on files modified.", 
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            parent.safe_mode = not parent.safe_mode
    else:
        parent.safe_mode = not parent.safe_mode

