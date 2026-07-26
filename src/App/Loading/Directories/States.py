from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from App.Loading.ParadoxSource import ParadoxSource

import os 

from ParadoxParser import ParadoxScriptParser as PDXScriptFile
from ParadoxParser.ParadoxNodes import GenericBlock, GenericKeyValue

from App.Loading.Directories.Base import GenericDirectory
from App.Contexts.Base import ParadoxContext
from App.Enums import PDXTokens

FILE_TYPES = {
    '.txt': ParadoxContext
}
class StatesDirectory(GenericDirectory):
    def __init__(self, source:ParadoxSource, file_path:os.PathLike, read_only:bool):
        super().__init__(source, file_path, FILE_TYPES, PDXScriptFile, read_only)

    def token_collection(self, source, file):
        tokens = set()
        file = file.file
        for block in file.nodes:
            if isinstance(block, GenericBlock):
                tokens.add(block.key)
        return {PDXTokens.STATE:tokens}
