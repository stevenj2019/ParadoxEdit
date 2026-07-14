from __future__ import annotations
import os
from pathlib import Path

from ParadoxParser import ParadoxScriptParser as PDXScriptFile
from ParadoxParser import ParadoxLocParser as PDXLocFile

from App.Services import AppLogger
from App.Loading.Models import FileReference, UnloadedFile

from App.Contexts.Base import ParadoxContext

ACCEPTED_TYPES = [".txt", ".gui", ".gfx"]
FILE_TYPES = {".txt": ParadoxContext}
class GenericDirectory:
    def __init__(self, file_path:os.PathLike, context:dict=FILE_TYPES, parser:PDXScriptFile|PDXLocFile=PDXScriptFile, read_only:bool=True):
        self.path = Path(file_path)
        self.context = context
        self.parser = parser
        self.read_only = read_only
        self.directories:dict[str, GenericDirectory] = {}
        self.files:dict[str:FileReference] = {}

    def add_file(self, path, name):
        if not path.suffix in self.context.keys():
            AppLogger.warning(f"{path.absolute()} ignored: lacks context.")
            return
        self.files[name] = FileReference(
            UnloadedFile(path, name, self.parser),
            self.context[path.suffix],
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
            if file.file.path.suffix in ACCEPTED_TYPES:
                self.files[key].file = file.file.load()
        for directory in self.directories.values():
            directory.parse_files()

    def iter_files(self):
        yield from self.files.values()

        for directory in self.directories.values():
            yield from directory.iter_files()

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
                metadata.setdefault(key, dict()).update(values)
        return metadata

    def metadata_collection(self, source):
        return {}
    
    def resolve_context(self, file):
        return None