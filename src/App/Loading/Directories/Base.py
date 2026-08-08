from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App.Loading.ParadoxSource import ParadoxSource

from collections.abc import Iterator
from pathlib import Path

from App.Contexts.Base import NullContext, ParadoxContext
from App.Enums import PDXMetadata, PDXTokens
from App.Loading.Models import FileReference, UnloadedFile
from ParadoxParser import ParadoxScriptParser as PDXScriptFile

FILE_TYPES = {
    "dir": {"context": ParadoxContext, "class": PDXScriptFile},
    ".txt": {"context": ParadoxContext, "class": PDXScriptFile},
}

NOT_IMPLEMENTED_FILE = {"context": NullContext, "class": None}


class GenericDirectory:
    def __init__(
        self,
        source: ParadoxSource,
        file_path: Path,
        definitions: dict = FILE_TYPES,
        read_only: bool = True,
    ) -> None:
        self.source = source
        self.path = Path(file_path)
        self.definitions = definitions
        if not definitions:
            self.definitions = FILE_TYPES
        self.parent: GenericDirectory = None
        self.context = self.definitions["dir"]["context"]
        self.read_only = read_only
        self.directories: dict[Path, GenericDirectory] = {}
        self.files: dict[str:FileReference] = {}

    def add_file(self, path: Path, name: str, file_ref: FileReference = None) -> None:
        definitions = self.definitions.get(path.suffix, NOT_IMPLEMENTED_FILE)
        if file_ref:
            self.files[name] = file_ref
        else:
            self.files[name] = FileReference(
                self,
                UnloadedFile(path, name, definitions["class"]),
                definitions["context"],
                self.read_only,
            )

    def delete_file(self, file: FileReference) -> None:
        self.files.pop(file, None)

    def add_directory(self, directory: GenericDirectory) -> None:
        directory.parent = self
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

    # def resolve_directory(self, path:Path) -> GenericDirectory:
    #     directory = self
    #     for i, parent in enumerate(path.parts):
    #         directory_path = self.path / parent
    #         if directory.path == directory_path:
    #             return directory
    #         directory = self.directories.get(directory_path)
    #     return None
        
    def resolve_directory(self, path: Path) -> GenericDirectory | None:
        directory = self

        for part in path.parts:
            directory_path = self.path / Path(*path.parts[:path.parts.index(part) + 1])
            directory = directory.directories.get(directory_path)
            if directory is None:
                return None

        return directory

    def token_collection(self, source: ParadoxSource, file: FileReference) -> dict[PDXTokens, set]:
        return {}

    def metadata_collection(
        self, source: ParadoxSource, file: FileReference
    ) -> dict[PDXMetadata, dict]:
        return {}
