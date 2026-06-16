import os
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from pathlib import Path
from Configuration import ConfigurationFile

def select_hoi4_install_directory(parent):
    options = QFileDialog.Options()
    options |= QFileDialog.ReadOnly
    filepath = QFileDialog.getExistingDirectory(
        parent,
        "Select Paradox Game install directory",
        "",
        QFileDialog.ShowDirsOnly
    )
    if not filepath:
        QMessageBox.warning(parent, "No folder selected", "You did not select an install folder")
        return
    path = Path(filepath)
    if not (path / "pdx_launcher").is_dir():
        QMessageBox.warning(parent, "Invalid folder selected", "This directory does not contain pdx_launcher")
        return
    return filepath

def select_mod_file(config:ConfigurationFile=None):
    """
    Opens a file dialog for selecting a .mod file,
    loads it into a ParadoxMod instance, and returns it.
    """
    options = QFileDialog.Options()
    options |= QFileDialog.ReadOnly
    filepath, _ = QFileDialog.getOpenFileName(
        None,
        "Select Paradox descriptor.mod file",
        "" if not config.mod_file_path else str(config.mod_file_path),
        "Paradox Mod Files (*.mod);;All Files (*)",
        options=options
    )

    if not filepath:
        QMessageBox.warning(None, "No file selected", "You did not select a mod file.")
        return None, None

    try:
        from ModClasses.ParadoxMod import ParadoxMod
        mod = ParadoxMod(filepath)
        return mod, filepath
    except Exception as e:
        QMessageBox.critical(None, "Failed to load mod", f"Error: {e}")
        return None, None
    
def gfx_files_folder_selector(parent):
    options = QFileDialog.Options()
    options |= QFileDialog.ReadOnly
    filepath = QFileDialog.getExistingDirectory(
        parent,
        "Select import images directory",
        str(Path.home()),
        QFileDialog.ShowDirsOnly
    )
    return filepath

def gfx_save_folder_selector(parent):
    options = QFileDialog.Options()
    options |= QFileDialog.ReadOnly
    filepath = QFileDialog.getExistingDirectory(
        parent,
        "Select imported images save directory",
        str(parent.mod.mod_base_dir / "gfx"),
        QFileDialog.ShowDirsOnly
    )
    return filepath