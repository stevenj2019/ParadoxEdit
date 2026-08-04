from textwrap import dedent

from platformdirs import user_log_dir
from PyQt5.QtWidgets import QMessageBox, QWidget

from App.AppData import APPNAME
from App.AppLogger import AppLogger


def could_not_load_mod_critical(
    parent: QWidget, exc: Exception, traceback: str
) -> None:
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle("Mod Could not be loaded")
    msg.setText("PDXEdit was unable to load your mod")

    msg.setDetailedText(traceback)
    msg.exec_()
    AppLogger.exception(traceback)

def unhandled_exception_popup(
    parent: QWidget, exc:Exception, traceback:str
) -> None:
    user_log_dir(APPNAME)
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle("Unhandlec Exception")
    msg.setText(dedent(
    f"""ParadoxEdit has encountered an unhandled exception, 
    you may continue, but it is reccomended to restart\n
    you can report this issue on the github.
    log located at {user_log_dir(APPNAME)}"""))

    msg.setDetailedText(traceback)
    msg.exec_()
    

def setup_process_cancelled(parent: QWidget) -> None:
    QMessageBox.critical(
        parent, "Startup Wizard Failed", "Startup Settings was aborted", QMessageBox.Ok
    )


def settings_error_critical(
    parent: QWidget, game_dir_error: bool, mod_dir_error: bool
) -> None:
    text = "The following Problems prevent saving:"
    if game_dir_error:
        text += "\nGame install directory could not find pdx_launcher, is invalid"
    if mod_dir_error:
        text += "\nMod folder does not contain any .mod files, is invalid"
    QMessageBox.critical(parent, "Error(s) in settings", text, QMessageBox.Ok)


def form_missing_value(parent: QWidget) -> None:
    QMessageBox.warning(
        parent, "Missing Value", "Form is missing essential values", QMessageBox.Ok
    )


# TODO: this should be used to make sure that GFX process doesnt copy into self
def GFX_load_and_store_are_same(parent: QWidget) -> None:
    QMessageBox.warning(
        parent,
        "Warning",
        "Source and Destination folders are identical, this operation will be terminated",
        QMessageBox.Ok,
    )


# TODO this should be used to make sure save_to is not malformed in GFX import
def invalid_GFX_file_warning(parent: QWidget) -> None:
    return QMessageBox.question(
        parent,
        "Invalid .gfx file provided",
        "This .gfx file lacks a SpriteTypes block, Syntax Error.",
        QMessageBox.Ok,
    )


def change_rejected_warning(parent: QWidget, message: str) -> None:
    AppLogger.warning(message)
    return QMessageBox.warning(parent, "Warning", message, QMessageBox.Ok)


def no_icon_available_warning(parent: QWidget, message: str) -> None:
    return QMessageBox.warning(parent, "Warning", message, QMessageBox.Ok)


def file_is_unsupported(parent: QWidget) -> None:
    QMessageBox.warning(
        parent, "Warning", "This File is currently unsupported", QMessageBox.Ok
    )

def form_is_read_only(parent:QWidget) -> None:
    QMessageBox.warning(
        parent, "Warning", 
        "This form is in read-only mode, localisation file belongs to a different source",
        QMessageBox.Ok
    )

def split_loc_file(parent:QWidget) -> None:
    QMessageBox.warning(
        parent, "Error",
        "localisation keys split across multiple files, exiting.",
        QMessageBox.Ok
    )