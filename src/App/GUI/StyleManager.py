import sys
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor as QColour
from PyQt5.QtGui import QIcon, QPainter, QPixmap
from PyQt5.QtSvg import QSvgRenderer

from App.Contracts.Enums import ChangeState
from App.Loading.Directories.Base import GenericDirectory
from App.Loading.Models import FileReference, IconFile, UnloadedFile
from App.Loading.ParadoxSource import ParadoxSource
from App.Services import ConfigurationManager
from ParadoxParser import ParadoxLocParser, ParadoxScriptParser


class StyleManager:
    def __init__(self, configuration: ConfigurationManager) -> None:
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
            self.icon_directory = Path(__file__).parent / "Icons"
        self.reload_icons()

    def get_node_state_colour(self, state: ChangeState) -> None:
        if self.configuration.dark_mode:
            return self.dark_mode_palette.get(state)
        else:
            return self.light_mode_palette.get(state)

    # NOTE: Icons sourced from lucide (in case i need more, ever?)
    def reload_icons(self) -> None:
        colour = QColour("#FFFFFF") if self.configuration.dark_mode else QColour("#000000")
        self._icons = {
            ParadoxSource: self.load_icon(self.icon_directory / "package.svg", colour),
            GenericDirectory: self.load_icon(self.icon_directory / "folder.svg", colour),
            UnloadedFile: self.load_icon(self.icon_directory / "file-x.svg", colour),
            IconFile: self.load_icon(self.icon_directory / "file-image.svg", colour),
            ParadoxScriptParser: self.load_icon(self.icon_directory / "file-code.svg", colour),
            ParadoxLocParser: self.load_icon(self.icon_directory / "file-text.svg", colour),
        }

    def load_icon(self, path: Path, colour: QColour) -> QIcon:
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

    def icon_for(self, entry: ParadoxSource | GenericDirectory | FileReference) -> QIcon:
        match entry:
            case ParadoxSource():
                return self._icons[ParadoxSource]
            case GenericDirectory():
                return self._icons[GenericDirectory]
            case _:
                return self._icons[type(entry.file)]
