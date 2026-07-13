from __future__ import annotations
import os
from pathlib import Path

from ParadoxParser import ParadoxScriptParser as PDXScriptFile
from ParadoxParser import ParadoxLocParser as PDXLocFile
from App.Loading.Models import UnloadedFile

from App.Contexts.Base import ParadoxContext

ACCEPTED_TYPES = [".txt", ".gui", ".gfx"]
class GenericDirectory:
    def __init__(self, base_path:os.PathLike, context:ParadoxContext=None, parser:PDXScriptFile|PDXLocFile=None, read_only:bool=True):
        self.path = Path(base_path)
        self.context = context
        self.parser = parser
        self.read_only = read_only
        self.directories:dict[str, GenericDirectory] = {}
        self.files:dict[str:UnloadedFile|PDXScriptFile|PDXLocFile] = {}

    def add_file(self, path, name):
        self.files[name] = UnloadedFile(path, name, self.parser)

    def delete_file(self, file):
        self.files.pop(file, None)

    def add_directory(self, directory:GenericDirectory):
        self.directories[directory.path] = directory
        
    def delete_directory(self):
        self.directories = {}
        self.files = {}

    def parse_files(self):
        for key, file in self.files.items():
            if file.path.suffix in ACCEPTED_TYPES:
                self.files[key] = file.load()
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
        
    def metadata_collection(self):
        return {}
    
    def token_collection(self):
        return {}
    
    def resolve_context(self, file):
        return None