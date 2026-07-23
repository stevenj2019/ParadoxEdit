from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from App.Loading.ParadoxSource import ParadoxSource

import os
from pathlib import Path

from ParadoxParser import ParadoxScriptParser as PDXScriptFile
from ParadoxParser import ParadoxLocParser as PDXLocFile

from App.Services import AppLogger
from App.Loading.Models import FileReference, UnloadedFile

from App.Contexts.Base import ParadoxContext

FILE_TYPES = {".txt": ParadoxContext}
class GenericDirectory:
    def __init__(self, source:ParadoxSource, file_path:os.PathLike, context:dict=FILE_TYPES, parser:PDXScriptFile|PDXLocFile=PDXScriptFile, read_only:bool=True):
        self.source = source
        self.path = Path(file_path)
        self.context_resolver = context
        self.resolve_context("")

        self.parser = parser
        self.read_only = read_only
        self.directories:dict[str, GenericDirectory] = {}
        self.files:dict[str:FileReference] = {}

    def add_file(self, path, name, file_ref:FileReference=None):
        if not path.suffix in self.context_resolver.keys():
            AppLogger.warning(f"{path.absolute()} ignored: lacks context.")
            return
        if file_ref:
            self.files[name] = file_ref
        else:
            self.files[name] = FileReference(
                self,
                UnloadedFile(path, name, self.parser),
                self.context_resolver[path.suffix],
                self.read_only
            )

    def delete_file(self, file):
        self.files.pop(file, None)

    def add_directory(self, directory:GenericDirectory):
        self.directories[directory.path] = directory
        
    def delete_directory(self):
        self.directories = {}
        self.files = {}

    def parse_files(self):
        for key, file in self.files.items():
            self.files[key].file = file.file.load()
        for directory in self.directories.values():
            directory.parse_files()

    def iter_files(self):
        yield from self.files.values()

        for directory in self.directories.values():
            yield from directory.iter_files()

    def prune(self):
        for name, directory in list(self.directories.items()):
            if directory.prune():
                self.directories.pop(name)

        return not self.directories and not self.files

    def token_collection_traversal(self):
        tokens = self.token_collection()
        for directory in self.directories.values():
            child_tokens = directory.token_collection()
            for key, values in child_tokens.items():
                tokens.setdefault(key, set()).update(values)
        return tokens
    
    def token_collection(self):
        return {}    
    
    def metadata_collection_traversal(self, source):
        metadata = self.metadata_collection(source)
        for directory in self.directories.values():
            child_metadata = directory.metadata_collection(source)
            for key, values in child_metadata.items():
                metadata.setdefault(key, type(values)()).update(values)
        return metadata

    def metadata_collection(self, source):
        return {}
    
    def resolve_context(self, file):
        if len(self.context_resolver.keys()) == 1:
            self.context = next(iter(self.context_resolver.values()))
        else:
            self.context = ParadoxContext