from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App import AppController

import copy

from PyQt5.QtWidgets import QDialog, QFormLayout, QGridLayout, QCheckBox, QPushButton

class ConfigureLoadedDLCForm(QDialog):
    def __init__(self, app_controller: AppController) -> None:
        super().__init__()
        self.app_controller = app_controller
        self.vanilla_source = self.app_controller.file_system.load_order.sources[0] #this can be safely assumed
        self.workspace = self.app_controller.file_system.workspace

        self.setWindowTitle("Configure Loaded DLC")
        self.setLayout(QFormLayout())
        self.form = self.layout()
        self.dlc_elements = list()

        self.dlc_grid = QGridLayout()
        for index, dlc in enumerate(self.vanilla_source.dlcs.values()):
            checkbox = QCheckBox(dlc.name)
            checkbox.setChecked(dlc.enabled)
            checkbox.dlc = dlc

            self.dlc_elements.append(checkbox)
            row = index // 2
            col = index % 2

            self.dlc_grid.addWidget(checkbox, row, col)
        self.form.addRow(self.dlc_grid)
        self.submit_button = QPushButton("Accept")
        self.submit_button.clicked.connect(self._submit)
        self.form.addRow(self.submit_button)
        self.exec_()

    def _submit(self) -> None:
        workspace_candidate = copy.deepcopy(self.workspace)
        for checkbox in self.dlc_elements:
            workspace_candidate.set_dlc_status(
                checkbox.dlc.identifier, 
                checkbox.isChecked()
            )
        self.accept()
        self.app_controller.reload_workspace(workspace_candidate)