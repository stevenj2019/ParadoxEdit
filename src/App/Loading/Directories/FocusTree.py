from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App.Loading.ParadoxSource import ParadoxSource

import os

from App.Contexts.Focus import FocusTreeContext
from App.Loading.Directories.Base import GenericDirectory
from ParadoxParser import ParadoxScriptParser as PDXScriptFile

FILE_TYPES = {"dir": FocusTreeContext, ".txt": FocusTreeContext}


class FocusTreeDirectory(GenericDirectory):
    def __init__(
        self, source: ParadoxSource, file_path: os.PathLike, read_only: bool
    ) -> None:
        super().__init__(source, file_path, FILE_TYPES, PDXScriptFile, read_only)
