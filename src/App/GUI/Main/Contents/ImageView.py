from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App import AppController
    from App.Loading.Models import FileReference
from PIL import Image
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget


class IconView(QWidget):
    def __init__(self, app_controller:AppController) -> None:
        super().__init__()
        self.app_controller = app_controller

        self.icon_label = QLabel()
        layout = QVBoxLayout(self)
        layout.addWidget(self.icon_label,
                         alignment=Qt.AlignTop | Qt.AlignLeft )

    def load_image(self, file:FileReference) -> None:
        file_path = file.file.get_path()
        with Image.open(file_path) as img:
            img.load()
            mode = img.mode
            img = img.convert("RGBA")
            width, height = img.size

            qimage = QImage(
                img.tobytes(),
                width,
                height,
                QImage.Format_RGBA8888
            )
            pixmap = QPixmap.fromImage(qimage)

        self.icon_label.setPixmap(pixmap)