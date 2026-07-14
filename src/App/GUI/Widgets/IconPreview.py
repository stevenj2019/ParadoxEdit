from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
from PIL import Image

class IconPreviewDialog(QDialog):
    def __init__(self, icon, path):
        super().__init__()
        self.setWindowTitle(path.name)

        label = QLabel()
        layout = QVBoxLayout(self)
        layout.addWidget(label)

        with Image.open(path) as img:
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
        label.setPixmap(pixmap)
        label.setAlignment(Qt.AlignCenter)
        self.resize(
            min(width, 800),
            min(height, 800)
        )
        layout.addWidget(QLabel(f"Icon Name:{icon.value}"))
        layout.addWidget(QLabel(f"File name:{path.name}"))
        layout.addWidget(QLabel(f"File size: {path.stat().st_size / 1024:.1f} KB"))
        layout.addWidget(QLabel(f"Size:{width}x{height}"))
        layout.addWidget(QLabel(f"Image Mode:{mode}"))
