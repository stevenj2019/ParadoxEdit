from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App.Loading.Models import FileReference
    from App.Loading.ParadoxSource import ParadoxSource


from App.Contexts.Base import ParadoxContext
from App.Enums import PDXTokens
from App.Loading.Directories.Base import GenericDirectory
from App.Loading.Models import FileReference
from ParadoxParser import ParadoxScriptParser as PDXScriptFile
from ParadoxParser.ParadoxNodes import GenericBlock

FILE_TYPES = {"dir":{"context":ParadoxContext, "model":PDXScriptFile},
              ".txt":{"context":ParadoxContext, "model":PDXScriptFile}}


class StatesDirectory(GenericDirectory):
    def __init__(self, source: ParadoxSource, file_path: Path, read_only: bool) -> None:
        super().__init__(source, file_path, FILE_TYPES, read_only)

    def token_collection(
        self, source: ParadoxSource, file: FileReference
    ) -> dict[PDXTokens, set]:
        tokens = set()
        file = file.file
        for block in file.nodes:
            if isinstance(block, GenericBlock):
                tokens.add(block.key)
        return {PDXTokens.STATE: tokens}
