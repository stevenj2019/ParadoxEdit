from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from App.Loading.ParadoxSource import ParadoxSource

import os 

from ParadoxParser import ParadoxScriptParser as PDXScriptFile
from ParadoxParser.ParadoxNodes import GenericBlock, GenericKeyValue

from App.Loading.Directories.Base import GenericDirectory
from App.Contexts.Event import EventContext
from App.Enums import PDXTokens

FILE_TYPES = {
    ".txt": EventContext
}
class EventDirectory(GenericDirectory):
    def __init__(self, source:ParadoxSource, file_path:os.PathLike, read_only:bool):
        super().__init__(source, file_path, FILE_TYPES, PDXScriptFile, read_only)
        
    def token_collection(self):
        tokens = set()
        for file in self.files.values():
            file = file.file
            if isinstance(file, PDXScriptFile):
                for block in file.nodes:
                    if isinstance(block, GenericBlock):
                        token = next((node.value.value for node in block.nodes 
                                    if isinstance(node, GenericKeyValue) 
                                    and node.key.lower()=="id"), None)
                        if token:
                            tokens.add(token)
        return {PDXTokens:tokens}
    
    def metadata_collection(self, source):
        return super().metadata_collection(source)