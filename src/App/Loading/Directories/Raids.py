from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App.Loading.ParadoxSource import ParadoxSource

import os

from App.Contexts.Base import ParadoxContext
from App.Enums import PDXTokens
from App.Loading.Directories.Base import GenericDirectory
from ParadoxParser import ParadoxScriptParser as PDXScriptFile
from ParadoxParser.ParadoxNodes import GenericBlock

FILE_TYPES = {".txt": ParadoxContext}


class RaidsDirectory(GenericDirectory):
    def __init__(
        self, source: ParadoxSource, file_path: os.PathLike, read_only: bool
    ) -> None:
        super().__init__(source, file_path, FILE_TYPES, PDXScriptFile, read_only)

    def token_collection(self, source, file) -> dict[PDXTokens, set]:
        tokens = set()
        file = file.file
        types_blocks = [
            block
            for block in file.nodes
            if isinstance(block, GenericBlock) and block.key.lower() == "types"
        ]
        for block in types_blocks:
            for node in block.nodes:
                if isinstance(node, GenericBlock):
                    tokens.add(node.key)
        return {PDXTokens.RAID: tokens}
