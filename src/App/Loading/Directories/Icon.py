from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from App.Loading.ParadoxSource import ParadoxSource

import os

from App.Loading.Models import IconFile
from App.Loading.Directories.Base import GenericDirectory
from App.Contexts.Base import ParadoxContext

FILE_TYPES = {
    '.dds': ParadoxContext,
    '.png': ParadoxContext
}
class IconDirectory(GenericDirectory):
    def __init__(self, source:ParadoxSource, file_path:os.PathLike, read_only:bool):
        super().__init__(source, file_path, FILE_TYPES, IconFile, read_only)
