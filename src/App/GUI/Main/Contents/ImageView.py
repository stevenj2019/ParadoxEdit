from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
from PIL import Image

class IconView(QWidget):
    def __init__(self, app_controller):
        super().__init__()
        self.app_controller = app_controller

        self.icon_label = QLabel()
        layout = QVBoxLayout(self)
        layout.addWidget(self.icon_label,
                         alignment=Qt.AlignTop | Qt.AlignLeft )

    def load_image(self, file):
        with Image.open(file.file.filepath) as img:
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