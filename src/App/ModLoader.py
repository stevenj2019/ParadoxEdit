from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout
from PyQt5.QtCore import QObject, pyqtSignal, Qt

from App.Modules import ParadoxMod
from App.PDXIndexers import get_scope_indices
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

class ModLoader(QObject):
    progress = pyqtSignal(str)
    finished = pyqtSignal(object)
    failed = pyqtSignal(Exception)

    def __init__(self, mod_file_path, game_install_path):
        super().__init__()
        self.descriptor_path = mod_file_path
        self.game_path = game_install_path

    def run(self):
        #open Loading prompt?
        try:
            self.progress.emit("Loading Mod")
            mod = ParadoxMod(self.descriptor_path)

            self.progress.emit("Gathering Tokens")
            tokens = get_scope_indices(self.game_path, mod.mod_base_dir)

            # self.progress.emit("Building Documentation")
            docs = {}

            self.finished.emit(ModLoaderResult(mod, tokens, docs))
        except Exception as e:
            self.failed.emit(e)
