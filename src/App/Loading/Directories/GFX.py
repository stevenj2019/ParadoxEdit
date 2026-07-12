import os

from ParadoxParser import ParadoxScriptParser as PDXFile

from App.Loading.Directories.Base import GenericDirectoryContext
from App.Contexts.GFX import GFXContext

class GFXDirectoryContext(GenericDirectoryContext):
    def __init__(self, file_path:os.PathLike):
        super().__init__(file_path, GFXContext, PDXFile, False)

    def token_collection(self):
        return super().token_collection()
    
    def metadata_collection(self):
        metadata = dict()
        for file in self.files.values():
            for node in file.nodes:
                if not isinstance(node, GenericComment): #TODO figure out what this is actually supposed to be lmao
                    metadata[node.key] = {"file":file, "node":node}
        return metadata
    
    def resolve_context(self, file):
        if file.endswith("gfx"):
            return self.context
        else:
            return None