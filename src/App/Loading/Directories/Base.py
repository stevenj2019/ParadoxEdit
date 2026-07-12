from __future__ import annotations
import os
from pathlib import Path

from ParadoxParser import ParadoxScriptParser as PDXScriptFile
from ParadoxParser import ParadoxLocParser as PDXLocFile
from App.Loading.Models import UnloadedFile

from App.Contexts.Base import ParadoxContext

class GenericDirectoryContext:
    def __init__(self, base_path:os.PathLike, context:ParadoxContext=None, parser:PDXScriptFile|PDXLocFile=None, read_only:bool=True):
        self.path = Path(base_path)
        self.context = context
        self.parser = parser
        self.read_only = True
        self.directories:dict[str, GenericDirectoryContext] = {}
        self.files:dict[str:UnloadedFile|PDXScriptFile|PDXLocFile] = {}

    def add_file(self, path, name):
        self.files[name] = UnloadedFile(path, name, self.parser)

    def add_directory(self, directory:GenericDirectoryContext):
        self.directories[directory.path] = directory
        
    def parse_files(self):
        for key, file in self.files.items():
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