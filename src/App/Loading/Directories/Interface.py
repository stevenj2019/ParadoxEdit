from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from App.Loading.ParadoxSource import ParadoxSource

import os
from pathlib import Path

from ParadoxParser import ParadoxScriptParser as PDXFile
from ParadoxParser.ParadoxNodes import GenericBlock, GenericKeyValue

from App.Loading.Directories.Base import GenericDirectory
from App.Contexts.Base import ParadoxContext
from App.Contexts.GFX import GFXContext
from App.Enums import PDXMetadata

FILE_TYPES = {
    '.gfx': GFXContext,
    '.gui': ParadoxContext
}
class InterfaceDirectory(GenericDirectory):
    def __init__(self, source:ParadoxSource, file_path:os.PathLike, read_only:bool):
        super().__init__(source, file_path, FILE_TYPES, PDXFile, read_only)
    
    def metadata_collection(self, source):
        metadata = dict()
        for file in self.files.values():
            if file.context is GFXContext:
                file = file.file
                if isinstance(file, PDXFile):
                    for node in file.nodes:
                        if isinstance(node, GenericBlock) and node.key.lower() == "spritetypes":
                            for node in node.nodes:
                                if isinstance(node, GenericBlock) and node.key.lower() == "spritetype":
                                    name = next((node.value.value for node in node.nodes
                                                 if isinstance(node, GenericKeyValue)
                                                 and node.key.lower() == "name"),None)
                                    texture = next((node.value.value for node in node.nodes
                                                    if isinstance(node, GenericKeyValue)
                                                    and node.key.lower() == "texturefile"), None)
                                    if name and texture:
                                        metadata[name] = Path(os.path.join(source.file_path, texture))
        return {PDXMetadata.GFXIcon:metadata}
    
    def resolve_context(self, file):
        if file.endswith("gfx"):
            return self.context
        else:
            return None