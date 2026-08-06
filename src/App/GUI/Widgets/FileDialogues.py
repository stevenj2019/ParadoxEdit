# TODO: come back to type hint
from pathlib import Path

from PyQt5.QtWidgets import QFileDialog, QMainWindow


def select_hoi4_install_directory(parent: QMainWindow) -> Path | None:
    options = QFileDialog.Options()
    options |= QFileDialog.ReadOnly
    filepath = QFileDialog.getExistingDirectory(
        parent, "Select Paradox Game install directory", "", QFileDialog.ShowDirsOnly
    )
    return Path(filepath) if filepath else None


def select_mod_directory(parent: QMainWindow) -> Path | None:
    options = QFileDialog.Option()
    options |= QFileDialog.ReadOnly
    filepath = QFileDialog.getExistingDirectory(
        parent, "Select Paradox game mod directory", "", QFileDialog.ShowDirsOnly
    )
    return Path(filepath) if filepath else None


def select_mod_file(parent: QMainWindow) -> Path | None:
    options = QFileDialog.Options()
    options |= QFileDialog.ReadOnly
    filepath, _ = QFileDialog.getOpenFileName(
        parent,
        "Select Paradox descriptor.mod file",
        ""
        if not parent.app_controller.configuration.appdata_path
        else str(parent.app_controller.configuration.appdata_path / "mod"),
        "Paradox Mod Files (*.mod);;All Files (*)",
        options=options,
    )
    return Path(filepath) if filepath else None


def gfx_files_folder_selector(parent: QMainWindow) -> Path | None:
    options = QFileDialog.Options()
    options |= QFileDialog.ReadOnly
    filepath = QFileDialog.getExistingDirectory(
        parent,
        "Select import images directory",
        str(Path.home()),
        QFileDialog.ShowDirsOnly,
    )
    return Path(filepath) if filepath else None


def gfx_files_file_selector(parent: QMainWindow) -> Path | None:
    options = QFileDialog.Options()
    options |= QFileDialog.ReadOnly
    filepath, _ = QFileDialog.getOpenFileName(
        parent, "Select import image", str(Path.home()), options=QFileDialog.ReadOnly
    )
    return Path(filepath) if filepath else None


def gfx_save_folder_selector(parent: QMainWindow, path: Path) -> Path | None:
    options = QFileDialog.Options()
    options |= QFileDialog.ReadOnly
    filepath = QFileDialog.getExistingDirectory(
        parent,
        "Select imported images save directory",
        str(path),
        QFileDialog.ShowDirsOnly,
    )
    return Path(filepath) if filepath else None


def workspace_selector(parent: QMainWindow) -> Path | None:
    options = QFileDialog.Options()
    options |= QFileDialog.ReadOnly
    filepath, _ = QFileDialog.getOpenFileName(
        parent,
        "Open Workspace",
        ""
        if not parent.app_controller.configuration.appdata_path
        else str(parent.app_controller.configuration.appdata_path / "mod"),
        "PDXEdit Workspace Files(*.json);;All Files (*)",
        options=options,
    )
    return Path(filepath) if filepath else None


def workspace_save_selector(parent: QMainWindow) -> Path | None:
    filepath, _ = QFileDialog.getSaveFileName(
        parent,
        "Save Workspace",
        ""
        if not parent.app_controller.configuration.appdata_path
        else str(parent.app_controller.configuration.appdata_path / "mod"),
        "PDXEdit Workspace Files(*.json);;All Files (*)",
    )
    if not filepath:
        return None

    path = Path(filepath)
    return path if path.suffix == ".json" else path.with_suffix(".json")
