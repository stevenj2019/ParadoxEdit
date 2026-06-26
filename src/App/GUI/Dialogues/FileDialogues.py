import os
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from pathlib import Path
from App.Services import ConfigurationManager

def select_hoi4_install_directory():
    options = QFileDialog.Options()
    options |= QFileDialog.ReadOnly
    return QFileDialog.getExistingDirectory(
        None,
        "Select Paradox Game install directory",
        "",
        QFileDialog.ShowDirsOnly
    )

def select_mod_directory():
    options = QFileDialog.Option()
    options |= QFileDialog.ReadOnly
    return QFileDialog.getExistingDirectory(
        None,
        "Select Paradox game mod directory",
        "",
        QFileDialog.ShowDirsOnly
    )

def select_mod_file(config:ConfigurationManager=None):
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
    return filepath
    
def gfx_files_folder_selector(parent):
    options = QFileDialog.Options()
    options |= QFileDialog.ReadOnly
    filepath = QFileDialog.getExistingDirectory(
        parent,
        "Select import images directory",
        str(Path.home()),
        QFileDialog.ShowDirsOnly
    )
    return filepath, Path(filepath).exists()

def gfx_save_folder_selector(parent):
    options = QFileDialog.Options()
    options |= QFileDialog.ReadOnly
    filepath = QFileDialog.getExistingDirectory(
        parent,
        "Select imported images save directory",
        str(parent.mod.mod_base_dir / "gfx"),
        QFileDialog.ShowDirsOnly
    )
    return filepath, Path(filepath).exists()