from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from App.Loading.ParadoxSource import ParadoxSource

import os
from pathlib import Path
from ParadoxParser import ParadoxLocParser as PDXLocFile
from ParadoxParser.ParadoxNodes import GenericLegacyLocKey, GenericLocKey

from App.Loading.Directories.Base import GenericDirectory
from App.Contexts.Loc import ParadoxContext, LocalisationContext
from App.Enums import PDXMetadata

FILE_TYPES = {
    '.yml': LocalisationContext
}
class LocDirectory(GenericDirectory):
    def __init__(self, source:ParadoxSource,file_path:os.PathLike, read_only:bool):
        super().__init__(source, file_path, FILE_TYPES, PDXLocFile, read_only)
    
    def metadata_collection(self, source, file):
        metadata = dict()
        metadata[PDXMetadata.LanguageKey] = set()
        metadata[PDXMetadata.LocKey] = dict()
        file = file.file
        if "_l_" not in file.filename:
            return metadata
        language = Path(file.filename).stem.rsplit("_l_", 1)[1]
        language_key = f"l_{language}"
        metadata[PDXMetadata.LanguageKey].add(language_key)
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