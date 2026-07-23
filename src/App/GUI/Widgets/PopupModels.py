from App.Services import AppLogger
from PyQt5.QtWidgets import QMessageBox

def could_not_load_mod_critical(exc: Exception, traceback:str):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle("Mod Could not be loaded")
    msg.setText("PDXEdit was unable to load your mod")

    msg.setDetailedText(traceback)
    msg.exec_()
    AppLogger.exception(traceback)


def setup_process_cancelled():
    return QMessageBox.critical(None, "Startup Wizard Failed", "Startup Settings was aborted", QMessageBox.Ok)
    
def settings_error_critical(game_dir_error:bool, mod_dir_error:bool):
    text = "The following Problems prevent saving:"
    if game_dir_error:
        text += "\nGame install directory could not find pdx_launcher, is invalid"
    if mod_dir_error:
        text += "\nMod folder does not contain any .mod files, is invalid"
    return QMessageBox.critical(
        None, 
        "Error(s) in settings",
        text,
        QMessageBox.Ok
    )

def form_missing_value(parent):
    return QMessageBox.warning(
        parent, "Missing Value", "Form is missing essential values", QMessageBox.Ok
    )

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
        "Wether or not you save the file, the code will not delete source files, you must do this manually if you proceed, but change your mind",
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

def GFX_load_and_store_are_same():
    return QMessageBox.warning(
        None, 
        "Warning",
        "Source and Destination folders are identical, this operation will be terminated",
        QMessageBox.Ok
    )

def invalid_GFX_file_warning(parent):
    return QMessageBox.question(
        parent, 
        "Invalid .gfx file provided",
        "This .gfx file lacks a SpriteTypes block, Syntax Error.", 
        QMessageBox.Ok
    )

def change_rejected_warning(message):
    AppLogger.warning(message)
    return QMessageBox.warning(
        None, 
        "Warning",
        message,
        QMessageBox.Ok
    )

def no_icon_available_warning(message):
    return QMessageBox.warning(
        None, "Warning", message, QMessageBox.Ok
    )

def file_is_unsupported():
    return QMessageBox.warning(
        None, "Warning", "This File is currently unsupported", QMessageBox.Ok
    )