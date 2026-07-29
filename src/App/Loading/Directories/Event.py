from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App.Loading.ParadoxSource import ParadoxSource

import os

from App.Contexts.Event import EventContext
from App.Enums import PDXTokens
from App.Loading.Directories.Base import GenericDirectory
from ParadoxParser import ParadoxScriptParser as PDXScriptFile
from ParadoxParser.ParadoxNodes import GenericBlock, GenericKeyValue

FILE_TYPES = {"dir": EventContext, ".txt": EventContext}


class EventDirectory(GenericDirectory):
    def __init__(
        self, source: ParadoxSource, file_path: os.PathLike, read_only: bool
    ) -> None:
        super().__init__(source, file_path, FILE_TYPES, PDXScriptFile, read_only)

    def token_collection(self, source, file) -> dict[PDXTokens, set]:
        tokens = set()
        file = file.file
        if isinstance(file, PDXScriptFile):
            for block in file.nodes:
                if isinstance(block, GenericBlock):
                    token = next(
                        (
                            node.value.value
                            for node in block.nodes
                            if isinstance(node, GenericKeyValue)
                            and node.key.lower() == "id"
                        ),
                        None,
                    )
                    if token:
                        tokens.add(token)
        return {PDXTokens.EVENT: tokens}
