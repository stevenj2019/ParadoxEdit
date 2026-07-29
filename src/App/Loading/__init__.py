import traceback
from pathlib import Path

from PyQt5.QtCore import QObject, Qt, pyqtSignal
from PyQt5.QtWidgets import QDialog, QLabel, QProgressBar, QVBoxLayout

from App.Contracts import ModLoaderResult
from App.Loading.LoadOrder import ParadoxLoadOrder
from App.Loading.Models import FileReference
from App.Loading.ParadoxSource import ParadoxSource
from App.Services import Workspace


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

    def __init__(self, workspace: Workspace, game_path: Path) -> None:
        super().__init__()
        self.workspace = workspace
        self.game_path = game_path

    def run(self) -> None:
        try:
            load_order = ParadoxLoadOrder(True)
            if self.workspace.vanilla_loaded:
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
            self.finished.emit(
                ModLoaderResult(self.workspace, load_order, self.tokens, self.metadata)
            )
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
        self._merge_registry(
            self.tokens, file.directory.token_collection(source, file))
        self._merge_registry(
            self.metadata, file.directory.metadata_collection(source, file)
        )

    def _merge_registry(self, target: dict, insertions: dict | set) -> None:
        for key, value in insertions.items():
            if key not in target:
                target[key] = type(value)()

            if isinstance(value, dict):
                self._merge_dict(target[key], value)
            else:
                target[key].update(value)


    def _merge_dict(self, target: dict, source: dict) -> None:
        for key, value in source.items():
            if (
                isinstance(value, dict)
                and isinstance(target.get(key), dict)
            ):
                self._merge_dict(target[key], value)
            else:
                target[key] = value