import os 

from ParadoxParser import ParadoxScriptParser as PDXScriptFile
from ParadoxParser.ParadoxNodes import GenericBlock, GenericKeyValue

from App.Loading.Directories.Base import GenericDirectoryContext
from App.Contexts.Event import EventContext
from App.Enums import PDXTokens

class EventDirectoryContext(GenericDirectoryContext):
    def __init__(self, file_path:os.PathLike):
        super().__init__(file_path, EventContext, PDXScriptFile, False)
        
    def token_collection(self):
        tokens = set()
        for file in self.files.values():
            for block in file.nodes:
                if isinstance(block, GenericBlock):
                    token = next((node.value.value for node in block.nodes 
                                  if isinstance(node, GenericKeyValue) 
                                  and node.key.lower()=="id"), None)
                    if token:
                        tokens.add(token)
        return {PDXTokens:tokens}