from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App.Loading.Models import FileReference
    from App.Loading.ParadoxSource import ParadoxSource

import os
from pathlib import Path

from App.Contexts.Base import ParadoxContext
from App.Contexts.GFX import GFXContext
from App.Enums import PDXMetadata
from App.Loading.Directories.Base import GenericDirectory
from ParadoxParser import ParadoxScriptParser as PDXScriptFile
from ParadoxParser.ParadoxNodes import GenericBlock, GenericKeyValue
from ParadoxParser.queries import find_node

FILE_TYPES = {
    "dir": {"context": ParadoxContext, "class": PDXScriptFile},
    ".gfx": {"context": GFXContext, "class": PDXScriptFile},
    ".gui": {"context": ParadoxContext, "class": PDXScriptFile},
}


class InterfaceDirectory(GenericDirectory):
    def __init__(self, source: ParadoxSource, file_path: Path, read_only: bool) -> None:
        super().__init__(source, file_path, FILE_TYPES, read_only)

    def metadata_collection(
        self, source: ParadoxSource, file: FileReference
    ) -> dict[PDXMetadata, dict]:
        metadata = dict()
        if file.context is GFXContext:
            file = file.file
            if isinstance(file, PDXScriptFile):
                for node in file.nodes:
                    if isinstance(node, GenericBlock) and node.key.lower() == "spritetypes":
                        for node in node.nodes:
                            if isinstance(node, GenericBlock) and node.key.lower() == "spritetype":
                                name = find_node(node, GenericKeyValue, "name")
                                texture = find_node(node, GenericKeyValue, "texturefile")

                                if name and texture:
                                    metadata[name.get_value()] = Path(
                                        os.path.join(source.file_path, texture.get_value())
                                    )
        return {PDXMetadata.GFXIcon: metadata}
