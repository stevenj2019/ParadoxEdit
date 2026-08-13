from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App import AppController

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QComboBox, QHBoxLayout, QPushButton, QWidget


# from App.Launcher import ParadoxProcess
class PlayGameWidget(QWidget):
    game_application_stopped = pyqtSignal()
    def __init__(self, app_controller:AppController) -> None:
        super().__init__()
        self.app_controller = app_controller
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.setLayout(self.layout)
        self.setAutoFillBackground(False)

        self.game_application_stopped.connect(self._stop)
        self.play_button = QPushButton()
        self.play_button.setStyleSheet("QPushButton {background: transparent;}")
        self.play_button.setFixedSize(20, 20)
        self.play_button.setIcon(self.app_controller.style_manager.get_play_icon())
        self.play_button.clicked.connect(self._toggle_running)
        self.layout.addWidget(self.play_button)

        self.selected_configuration = QComboBox()
        self.selected_configuration.addItem("Default", None)
        self.selected_configuration.setCurrentIndex(0)
        index = 1
        #add configuration items here
        #for each, add 1 to index
        self.selected_configuration.insertSeparator(index)
        self.selected_configuration.addItem("Create new", "create")
        self.selected_configuration.activated.connect(self._configuration_selected)
        self.layout.addWidget(self.selected_configuration)

        height = self.selected_configuration.sizeHint().height()
        self.play_button.setFixedSize(height, height)
        
    def _configuration_selected(self, index:int) -> None:
        selected = self.selected_configuration.itemData(index) 
        if selected == "create":
            #create configuration form
            self.selected_configuration.setCurrentIndex(self.selected_configuration_index)
        else:
            self.selected_configuration = selected

    def _toggle_running(self) -> None:
        if self.process: 
            self._stop()
        self._start()

    def _start(self) -> None:
        # self.process = ParadoxProcess(self.app_controller, 
        #                               self.selected_configuration, 
        #                               self.game_application_stopped )
        # self.process.watch_process()
        if self.process:
            self.play_button.setIcon(self.app_controller.style_manager.get_stop_icon())
        else:
            self.play_button.setIcon(self.app_controller.style_manager.get_play_icon())

    def _stop(self) -> None:
        self.process.stop()
        self.play_button.setIcon(self.app_controller.style_manager.get_play_icon())