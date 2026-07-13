import os

from ParadoxParser import ParadoxScriptParser as PDXFile
from ParadoxParser.ParadoxNodes import GenericKeyValue

from App.Loading.Directories.Base import GenericDirectory
from App.Contexts.GFX import GFXContext
from App.Enums import PDXMetadata

class GFXDirectory(GenericDirectory):
    def __init__(self, file_path:os.PathLike):
        super().__init__(file_path, GFXContext, PDXFile, False)

    def token_collection(self):
        return super().token_collection()
    
    def metadata_collection(self):
        metadata = dict()
        for file in self.files.values():
            for node in file.nodes:
                if isinstance(node, GenericKeyValue):
                    metadata[node.key] = {"file":file, "node":node}
        return {PDXMetadata.GFXIcon:metadata}
    
    def resolve_context(self, file):
        if file.endswith("gfx"):
            return self.context
        else:
            return None