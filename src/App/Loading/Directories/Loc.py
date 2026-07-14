import os

from ParadoxParser import ParadoxLocParser as PDXLocFile
from ParadoxParser.ParadoxNodes import GenericComment, GenericLegacyLocKey, GenericLocKey

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
    
    def metadata_collection(self, source):
        metadata = dict()
        metadata[PDXMetadata.LanguageKey] = set()
        metadata[PDXMetadata.LocKey] = dict()
        for directory in self.directories.values():
            language_key = directory.path.parts[-1]
            metadata[PDXMetadata.LanguageKey].add(language_key)
            for file in directory.files.values():
                file = file.file
                for node in file.nodes:
                    if isinstance(node, (GenericLocKey, GenericLegacyLocKey)):
                        metadata[PDXMetadata.LocKey].setdefault(node.key, dict())
                        metadata[PDXMetadata.LocKey][node.key][language_key] = {
                            "file":file, "node":node
                        }
        return metadata
    
    def resolve_context(self, file):
        if file.endswith("gfx"):
            return self.context
        else:
            return None