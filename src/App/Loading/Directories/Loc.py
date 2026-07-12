import os

from ParadoxParser import ParadoxLocParser as PDXLocFile
from ParadoxParser.ParadoxNodes import GenericComment

from App.Loading.Directories.Base import GenericDirectoryContext
from App.Contexts.Loc import LocalisationContext
from App.Enums import PDXMetadata

class LocDirectoryContext(GenericDirectoryContext):
    def __init__(self, file_path:os.PathLike):
        super().__init__(file_path, LocalisationContext, PDXLocFile, False)

    def token_collection(self):
        return super().token_collection()
    
    def metadata_collection(self):
        metadata = dict()
        for file in self.files.values():
            for node in file.nodes:
                if not isinstance(node, GenericComment):
                    metadata[node.key] = {"file":file, "node":node}
        return {PDXMetadata.LocKey:metadata}
    
    def resolve_context(self, file):
        if file.endswith("gfx"):
            return self.context
        else:
            return None