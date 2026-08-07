from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App import AppController

import copy

from PyQt5.QtWidgets import QComboBox, QDialog, QFormLayout, QLineEdit, QPushButton

from App.Contracts import FileMutationRequest
from App.Contracts.Enums import ChangeState
from App.Loading.Models import FileReference, IconFile
from App.Loading.ParadoxSource import ParadoxVanilla


class CopyFileForm(QDialog):
    def __init__(self, app_controller: AppController, file: FileReference) -> None:
        super().__init__()
        self.app_controller = app_controller
        self.file = file
        self.load_order = self.app_controller.file_system.load_order
        self.setWindowTitle("Copy file to source")

        self.resize(250, 100)
        self.setLayout(QFormLayout())
        self.form = self.layout()

        self.file_to_copy = QLineEdit(self.file.file.filename)
        self.file_to_copy.setEnabled(False)
        self.form.addRow("📄", self.file_to_copy)

        self.copy_to_source_combo = QComboBox()
        for source in self.load_order.sources:
            if not isinstance(source, ParadoxVanilla):
                self.copy_to_source_combo.addItem(source.source_name, source)
        self.form.addRow("📦", self.copy_to_source_combo)

        self.submit_button = QPushButton("Copy")
        self.submit_button.clicked.connect(self._submit)
        self.form.addRow(self.submit_button)
        self.exec_()

    def _submit(self) -> None:
        directory_key = next(
            key
            for key, directory in self.file.directory.source.directories.items()
            if directory is self.file.directory
        )
        source = self.copy_to_source_combo.currentData()
        target_directory = source._ensure_directory(directory_key)

        new_path = source.file_path / target_directory.path / self.file.file.filename
        if isinstance(self.file.file, IconFile):
            new_file = IconFile.add(source_path=self.file.file.filepath, save_path=new_path)
        else:
            new_file = copy.deepcopy(self.file.file)
            new_file.filepath = new_path

        new_file = FileReference(
            directory=target_directory, file=new_file, context=self.file.context, read_only=False
        )

        self.app_controller.request_file_mutation.emit(
            FileMutationRequest(target_directory, new_file, ChangeState.ADDED)
        )

        self.app_controller.request_file_unload.emit(self.file)

        self.app_controller.request_registry_cache_rebuild.emit()
        self.close()

class AddReplacePathForm(QDialog):
    def __init__(self, app_controller:AppController, file_reference:FileReference) -> None:
        super().__init__()
        self.app_controller = app_controller
        self.directory = file_reference.target
        self.load_order = self.app_controller.file_system.load_order
        self.setWindowTitle("Add replace_path to source.")

        self.resize(250, 100)
        self.setLayout(QFormLayout())
        self.form = self.layout()

        self.file_to_copy = QLineEdit(str(self.directory.path))
        self.file_to_copy.setEnabled(False)
        self.form.addRow("📁", self.file_to_copy)

        self.copy_to_source_combo = QComboBox()
        for source in self.load_order.sources:
            if not isinstance(source, ParadoxVanilla):
                self.copy_to_source_combo.addItem(source.source_name, source)
        self.form.addRow("📦", self.copy_to_source_combo)

        self.submit_button = QPushButton("Copy")
        self.submit_button.clicked.connect(self._submit)
        self.form.addRow(self.submit_button)
        self.exec_()

    def _submit(self) -> None:
        directory_key = next(
            key
            for key, directory in self.file.directory.source.directories.items()
            if directory is self.file.directory
        )
        source = self.copy_to_source_combo.currentData()
        #TODO: complete
        #mutate source.descriptor_object
        #unload everything within directory_key, and prune
        #update UI 
        #complete.