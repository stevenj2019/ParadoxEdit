from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App.Loading.Models import FileReference
    from App.Loading.ParadoxSource import ParadoxSource

from pathlib import Path

from App.Contexts.Loc import LocalisationContext
from App.Enums import PDXMetadata
from App.Loading.Directories.Base import GenericDirectory
from ParadoxParser import ParadoxLocParser as PDXLocFile
from ParadoxParser.ParadoxNodes import GenericLegacyLocKey, GenericLocKey

FILE_TYPES = {".yml": LocalisationContext}


class LocDirectory(GenericDirectory):
    def __init__(self, source: ParadoxSource, file_path: Path, read_only: bool) -> None:
        super().__init__(source, file_path, FILE_TYPES, PDXLocFile, read_only)

    def metadata_collection(
        self, source: ParadoxSource, file: FileReference
    ) -> dict[PDXMetadata, dict]:
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
                    "file": file,
                    "node": node,
                }
        return metadata
