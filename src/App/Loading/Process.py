from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App.Loading.Models import FileReference
    from App.Loading.ParadoxSource import ParadoxSource

import traceback
from pathlib import Path

from PyQt5.QtCore import QObject, Qt, pyqtSignal
from PyQt5.QtWidgets import QDialog, QLabel, QProgressBar, QVBoxLayout

from App.Contracts import ModLoaderResult
from App.Services import ParadoxRegistry, Workspace

from App.Loading.LoadOrder import ParadoxLoadOrder


class LoadingDialog(QDialog):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Loading Mod")
        self.setModal(True)
        self.setFixedSize(350, 100)

        self.label = QLabel("Starting...")
        self.label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

    def update_message(self, message: str) -> None:
        self.label.setText(message)

    def start_progress_bar(self, n_files: int) -> None:
        self.progress_bar.setRange(0, n_files)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)

    def update_progress_bar(self, n_progress: int) -> None:
        self.progress_bar.setValue(n_progress)

    def end_progress_bar(self) -> None:
        self.progress_bar.setVisible(False)


class LoadProcess(QObject):
    progress_message = pyqtSignal(str)
    progress_bar_start = pyqtSignal(int)
    progress_bar_update = pyqtSignal(int)
    progress_bar_end = pyqtSignal()
    finished = pyqtSignal(object)
    failed = pyqtSignal(Exception, str)

    def __init__(self, workspace: Workspace, registry: ParadoxRegistry, game_path: Path) -> None:
        super().__init__()
        self.workspace = workspace
        self.registry = registry
        self.game_path = game_path

    def run(self) -> None:
        try:
            load_order = ParadoxLoadOrder(self.workspace)
            if self.workspace.vanilla.loaded:
                self.progress_message.emit("Loading Vanilla Files")
                load_order.load_vanilla(self.game_path)

            self.progress_message.emit("Loading Mod Files")
            for mod in self.workspace.mods:
                load_order.load_mod(mod)

            self.progress_message.emit("Resolving Load Order")
            load_order.resolve()

            self.tokens: dict = {}
            self.metadata: dict = {}

            self._process_files(load_order)

            self.progress_message.emit("Finishing Up")
            self.registry._build_registry_cache()
            self.finished.emit(ModLoaderResult(self.workspace, load_order))
        except Exception as e:
            self.failed.emit(e, traceback.format_exc())

    def _process_files(self, load_order: ParadoxLoadOrder) -> None:
        self.progress_message.emit("Preparing Files")
        files = list()
        processed = 0
        for source in load_order.sources:
            for file in source.root.iter_files():
                files.append((source, file))
        self.progress_message.emit(f"Processing Files ({processed}/{len(files)})")
        self.progress_bar_start.emit(len(files))
        for source, file in files:
            self.progress_message.emit(f"Processing Files ({processed}/{len(files)})")
            self.progress_bar_update.emit(processed)
            self._file_processing(source, file)
            processed += 1
        self.progress_bar_end.emit()

    def _file_processing(self, source: ParadoxSource, file: FileReference) -> None:
        file.file = file.file.load()
        self.registry.load_file_data(source, file)
