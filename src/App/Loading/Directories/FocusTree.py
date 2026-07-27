from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from App.Loading.ParadoxSource import ParadoxSource

import os 

from ParadoxParser import ParadoxScriptParser as PDXScriptFile
from ParadoxParser.ParadoxNodes import GenericBlock, GenericKeyValue

from App.Loading.Directories.Base import GenericDirectory
from App.Contexts.Focus import FocusTreeContext
from App.Enums import PDXTokens

FILE_TYPES = {
    'dir': FocusTreeContext,
    '.txt': FocusTreeContext
}
class FocusTreeDirectory(GenericDirectory):
    def __init__(self, source:ParadoxSource, file_path:os.PathLike, read_only:bool):
        super().__init__(source, file_path, FILE_TYPES, PDXScriptFile, read_only)