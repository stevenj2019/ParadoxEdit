from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App.Loading.Models import FileReference
    from App.Loading.ParadoxSource import ParadoxSource

from pathlib import Path

from App.Contexts.Base import ParadoxContext
from App.Enums import PDXTokens
from App.Loading.Directories.Base import GenericDirectory
from ParadoxParser import ParadoxScriptParser as PDXScriptFile
from ParadoxParser.ParadoxNodes import GenericKeyValue, GenericString

FILE_TYPES = {
    "dir": {"context": ParadoxContext, "class": PDXScriptFile},
    ".txt": {"context": ParadoxContext, "class": PDXScriptFile},
}


class CountryTagDirectory(GenericDirectory):
    def __init__(self, source: ParadoxSource, file_path: Path, read_only: bool) -> None:
        super().__init__(source, file_path, FILE_TYPES, read_only)

    def token_collection(self, source: ParadoxSource, file: FileReference) -> dict[PDXTokens, set]:
        tokens = set()
        file = file.file
        for node in file.nodes:
            if isinstance(node, GenericKeyValue):
                value_node = node.value
                if isinstance(value_node, GenericString):
                    tokens.add(node.key)
        return {PDXTokens.COUNTRY: tokens}
