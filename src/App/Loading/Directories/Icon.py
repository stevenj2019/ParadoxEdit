from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App.Loading.ParadoxSource import ParadoxSource

import os

from App.Contexts.Base import ReadOnlyContext
from App.Loading.Directories.Base import GenericDirectory
from App.Loading.Models import IconFile

FILE_TYPES = {"dir": ReadOnlyContext, ".dds": ReadOnlyContext, ".png": ReadOnlyContext}


class IconDirectory(GenericDirectory):
    def __init__(
        self, source: ParadoxSource, file_path: os.PathLike, read_only: bool
    ) -> None:
        super().__init__(source, file_path, FILE_TYPES, IconFile, read_only)
