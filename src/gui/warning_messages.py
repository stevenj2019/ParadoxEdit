from PyQt5.QtWidgets import QMessageBox

def bulk_operation_warning(parent):
    if not parent.bulk_warning_shown:
        mode_text = (
            "SAFE MODE ENABLED (recommended)"
            if parent.safe_mode
            else "SAFE MODE DISABLED (risky)"
        )

        msg = (
            "You are performing a bulk operation.\n\n"
            f"Current mode: {mode_text}\n\n"
            "Bulk edits can modify many files at once.\n"
            "This warning will only appear once per session."
        )

        reply = QMessageBox.question(
            parent,
            "Bulk Operation Warning",
            msg,
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            parent.bulk_warning_shown = True
            return True
    else:
        return True

def toggle_safe_mode_warning(parent):
    if parent.safe_mode:
        reply = QMessageBox.question(
            parent, 
            "Warning", 
            "This will disable safe mode, which allows for .bak generation on files modified.", 
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            parent.safe_mode = not parent.safe_mode
    else:
        parent.safe_mode = not parent.safe_mode

def GFX_file_copying_warn(parent):
    reply = QMessageBox.question(
        parent, 
        "Warning",
        "Wether or not you save the file, the code will not delete source files, you must do this manually if you proceed.",
        QMessageBox.Yes | QMessageBox.No
    )
    return reply == QMessageBox.Yes

def GFX_is_focus_upload(parent):
    reply = QMessageBox.question(
        parent, 
        "Generate _shines",
        "Are these icons intended for use in Focus Trees?",
        QMessageBox.Yes | QMessageBox.No
    )
    return reply == QMessageBox.Yes