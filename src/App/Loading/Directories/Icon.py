from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App.Loading.ParadoxSource import ParadoxSource


from pathlib import Path

from App.Contexts.Base import ParadoxContext, ReadOnlyContext
from App.Loading.Directories.Base import GenericDirectory
from App.Loading.Models import IconFile
from ParadoxParser import ParadoxScriptParser as PDXScriptFile

FILE_TYPES = {
    "dir": {"context": ReadOnlyContext, "class": IconFile},
    ".dds": {"context": ReadOnlyContext, "class": IconFile},
    ".png": {"context": ReadOnlyContext, "class": IconFile},
    ".asset": {"context": ParadoxContext, "class": PDXScriptFile},
}


class IconDirectory(GenericDirectory):
    def __init__(self, source: ParadoxSource, file_path: Path, read_only: bool) -> None:
        super().__init__(source, file_path, FILE_TYPES, read_only)
