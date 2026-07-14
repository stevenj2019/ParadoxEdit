import os

from ParadoxParser import ParadoxLocParser as PDXLocFile
from ParadoxParser.ParadoxNodes import GenericComment

from App.Loading.Directories.Base import GenericDirectory
from App.Contexts.Loc import LocalisationContext
from App.Enums import PDXMetadata

FILE_TYPES = {
    ".yml": LocalisationContext
}
class LocDirectory(GenericDirectory):
    def __init__(self, file_path:os.PathLike, read_only:bool):
        super().__init__(file_path, FILE_TYPES, PDXLocFile, read_only)

    def token_collection(self):
        return super().token_collection()
    
    #TODO: it is fucked.
    def metadata_collection(self, source):
        metadata = dict()
        for file in self.files.values():
            file = file.file
            if isinstance(file, PDXLocFile):
                for node in file.nodes:
                    if not isinstance(node, GenericComment):
                        metadata[node.key] = {"file":file, "node":node}
        return {PDXMetadata.LocKey:metadata}
    
    def resolve_context(self, file):
        if file.endswith("gfx"):
            return self.context
        else:
            return None