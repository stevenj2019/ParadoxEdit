import sys
from pathlib import Path
from PyQt5.QtGui import QColor as QColour, QIcon, QPixmap, QPainter
from PyQt5.QtCore import Qt
from PyQt5.QtSvg import QSvgRenderer

from App.Contracts.Enums import ChangeState
from App.Loading.Directories.Base import GenericDirectory
from App.Loading.Models import IconFile, UnloadedFile
from ParadoxParser import ParadoxScriptParser, ParadoxLocParser

class StyleManager:
    def __init__(self, configuration):
        self.configuration = configuration
        self.dark_mode_palette = {
            ChangeState.MODIFIED: QColour("#545703"),
            ChangeState.ADDED: QColour("#04450c"),
            ChangeState.DELETED: QColour("#400308"),
        }
        self.light_mode_palette = {
            ChangeState.MODIFIED: QColour("yellow"),
            ChangeState.ADDED: QColour("green"),
            ChangeState.DELETED: QColour("red"),
        }

        if getattr(sys, "frozen", False):
            self.icon_directory = Path(sys._MEIPASS) / "Icons"
        else:
            self.icon_directory = (Path(__file__).parent / "Icons")
        self.reload_icons()

    def get_node_state_colour(self, state):
        if self.configuration.dark_mode:
            return self.dark_mode_palette.get(state)
        else:
            return self.light_mode_palette.get(state)

    #NOTE: Icons sourced from lucide (in case i need more, ever?)
    def reload_icons(self):
        colour = QColour("#FFFFFF") if self.configuration.dark_mode else QColour("#000000")
        self._icons = {
            GenericDirectory: self.load_icon(self.icon_directory / "folder.svg", colour),
            UnloadedFile: self.load_icon(self.icon_directory / "file-x.svg", colour),
            IconFile: self.load_icon(self.icon_directory / "file-image.svg", colour),
            ParadoxScriptParser: self.load_icon(self.icon_directory / "file-code.svg", colour),
            ParadoxLocParser: self.load_icon(self.icon_directory / "file-text.svg", colour),
        }

    def load_icon(self, path, colour):
        renderer = QSvgRenderer(str(path))

        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        coloured = QPixmap(pixmap.size())
        coloured.fill(Qt.transparent)

        painter = QPainter(coloured)
        painter.setCompositionMode(QPainter.CompositionMode_Source)
        painter.fillRect(coloured.rect(), colour)

        painter.setCompositionMode(QPainter.CompositionMode_DestinationIn)
        painter.drawPixmap(0, 0, pixmap)

        painter.end()

        return QIcon(coloured)
        
    def get_icon(self, cls):
        return self._icons[cls]
