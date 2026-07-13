from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QObject, pyqtSignal

from App.Loading.LoadOrder import ParadoxLoadOrder
from App.Contracts import ModLoaderResult

class LoadingDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Loading Mod")
        self.setModal(True)
        self.setFixedSize(350, 100)

        self.label = QLabel("Starting...")
        self.label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.label)

        self.setLayout(layout)

    def update_message(self, message):
        self.label.setText(message)

class LoadProcess(QObject):
    progress = pyqtSignal(str)
    finished = pyqtSignal(object)
    failed = pyqtSignal(Exception)

    def __init__(self, workspace, game_path):
        super().__init__()
        self.workspace = workspace
        self.game_path = game_path

    def run(self):
        try:
            load_order = ParadoxLoadOrder(True)
            if self.workspace.vanilla_loaded:
                self.progress.emit("Loading Vanilla Files")
                load_order.load_vanilla(self.game_path)

            self.progress.emit("Loading Mod Files")
            for mod in self.workspace.mods:
                load_order.load_mod(mod)
            
            self.progress.emit("Resolving Load Order")
            load_order.resolve()
            
            self.progress.emit("Parsing Files")
            load_order.parse_files()
            
            self.progress.emit("Preparing Tokens")
            tokens = load_order.token_collection()

            self.progress.emit("Preparing Metadata")
            #TODO: 1. get metadata

            self.progress.emit("Finishing Up")
            self.finished.emit(ModLoaderResult(self.workspace, load_order, tokens, {}))
        except Exception as e:
            self.failed.emit(e)
