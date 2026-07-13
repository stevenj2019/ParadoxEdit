from PyQt5.QtWidgets import QFileDialog
from pathlib import Path

def select_hoi4_install_directory(parent):
    options = QFileDialog.Options()
    options |= QFileDialog.ReadOnly
    return QFileDialog.getExistingDirectory(
        parent,
        "Select Paradox Game install directory",
        "",
        QFileDialog.ShowDirsOnly
    )

def select_mod_directory(parent):
    options = QFileDialog.Option()
    options |= QFileDialog.ReadOnly
    return QFileDialog.getExistingDirectory(
        parent,
        "Select Paradox game mod directory",
        "",
        QFileDialog.ShowDirsOnly
    )

def select_mod_file(parent):
    options = QFileDialog.Options()
    options |= QFileDialog.ReadOnly
    filepath, _ = QFileDialog.getOpenFileName(
        parent,
        "Select Paradox descriptor.mod file",
        "" if not parent.app_controller.configuration.mod_file_path else str(parent.app_controller.configuration.mod_file_path),
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

def gfx_files_file_selector(parent):
    options = QFileDialog.Options()
    options |= QFileDialog.ReadOnly
    filepath, _ = QFileDialog.getOpenFileName(
        parent, 
        "Select import image",
        str(Path.home()),
        options=QFileDialog.ReadOnly
    )
    return filepath, Path(filepath).exists()

def gfx_save_folder_selector(parent, path):
    options = QFileDialog.Options()
    options |= QFileDialog.ReadOnly
    filepath = QFileDialog.getExistingDirectory(
        parent,
        "Select imported images save directory",
        path,
        QFileDialog.ShowDirsOnly
    )
    return filepath, Path(filepath).exists()

def workspace_selector(parent):
    options = QFileDialog.Options()
    options |= QFileDialog.ReadOnly
    filepath, _ = QFileDialog.getOpenFileName(
        parent,
        "Open Workspace",
        "" if not parent.app_controller.configuration.mod_file_path else str(parent.app_controller.configuration.mod_file_path),
        "PDXEdit Workspace Files(*.json);;All Files (*)",
        options=options
    )
    return filepath

def workspace_save_selector(parent):
    filepath, _ = QFileDialog.getSaveFileName(
        parent, 
        "Save Workspace",
        "" if not parent.app_controller.configuration.mod_file_path else str(parent.app_controller.configuration.mod_file_path),
        "PDXEdit Workspace Files(*.json);;All Files (*)"
    )
    return filepath if filepath.endswith(".json") else f"{filepath}.json"