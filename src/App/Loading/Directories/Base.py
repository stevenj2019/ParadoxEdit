from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App.Loading.ParadoxSource import ParadoxSource

import os
from pathlib import Path

from App.Contexts.Base import ParadoxContext
from App.Enums import PDXMetadata, PDXTokens
from App.Loading.Models import FileReference, UnloadedFile
from App.Services import AppLogger
from ParadoxParser import ParadoxLocParser as PDXLocFile
from ParadoxParser import ParadoxScriptParser as PDXScriptFile

from collections.abc import Iterator

FILE_TYPES = {".txt": ParadoxContext}


class GenericDirectory:
    def __init__(
        self,
        source: ParadoxSource,
        file_path: os.PathLike,
        context: dict = FILE_TYPES,
        parser: PDXScriptFile | PDXLocFile = PDXScriptFile,
        read_only: bool = True,
    ) -> None:
        self.source = source
        self.path = Path(file_path)
        self.context_resolver = context
        self.context = (
            self.source.context_override
            if self.source.context_override
            else context.get("dir", ParadoxContext)
        )

        self.parser = parser
        self.read_only = read_only
        self.directories: dict[str, GenericDirectory] = {}
        self.files: dict[str:FileReference] = {}

    def add_file(self, path, name, file_ref: FileReference = None) -> None:
        if path.suffix not in self.context_resolver.keys():
            AppLogger.warning(f"{path.absolute()} ignored: lacks context.")
            return
        if file_ref:
            self.files[name] = file_ref
        else:
            self.files[name] = FileReference(
                self,
                UnloadedFile(path, name, self.parser),
                self.source.context_override
                if self.source.context_override
                else self.context_resolver[path.suffix],
                self.read_only,
            )

    def delete_file(self, file) -> None:
        self.files.pop(file, None)

    def add_directory(self, directory: GenericDirectory) -> None:
        self.directories[directory.path] = directory

    def delete_directory(self) -> None:
        self.directories = {}
        self.files = {}

    def iter_files(self) -> Iterator[FileReference]:
        yield from self.files.values()

        for directory in self.directories.values():
            yield from directory.iter_files()

    def prune(self) -> None:
        for name, directory in list(self.directories.items()):
            if directory.prune():
                self.directories.pop(name)

        return not self.directories and not self.files

    def token_collection(self, source, file) -> dict[PDXTokens, set]:
        return {}

    def metadata_collection(self, source, file) -> dict[PDXMetadata, dict]:
        return {}
