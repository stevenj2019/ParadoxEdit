from pathlib import Path
import os

from App.Services import AppLogger
from App.Loading.Models import UnloadedFile
from App.Loading.Directories.Base import GenericDirectoryContext
from App.Loading.Directories import DIRECTORY_REGISTRY
from ParadoxParser import ParadoxScriptParser
from ParadoxParser.ParadoxNodes import GenericKeyValue

class ParadoxSource:
    def __init__(self, name, path):
        self.source_name = name
        self.file_path = path
        self.root = GenericDirectoryContext(self.file_path, GenericDirectoryContext)
        self.directories = {
            self.file_path: self.root
        }
        self.tree:dict[str, GenericDirectoryContext|UnloadedFile] = {}
        self._build_tree()

    def parse_files(self):
        self.root.parse_files()

    def _build_tree(self):
        for root, dirs, files in os.walk(self.file_path):
            root = Path(root)
            parent = self.directories[root]

            for directory_name in dirs:
                directory_path = Path(os.path.join(root, directory_name))
                directory = self._create_directory(directory_path)
                parent.add_directory(directory)
                self.directories[directory_path] = directory

            for file_name in files:
                file_path = Path(os.path.join(root, file_name))
                parent.add_file(file_path, file_name)

    def _create_directory(self, path):
        rel_path = path.relative_to(self.file_path)
        category = DIRECTORY_REGISTRY.get(
            str(rel_path),
            GenericDirectoryContext
        )
        print(path, category)
        return category(path)
    
    def _apply_overrides(self):
        return NotImplementedError

    def token_collection(self):
        return self.root.token_collection_traversal()

class ParadoxVanilla(ParadoxSource):
    def __init__(self, path):
        super().__init__("Vanilla", path)

class ParadoxMod(ParadoxSource):
    def __init__(self, path):
        path = Path(path)
        self.descriptor_file = path.name
        self.descriptor_object = ParadoxScriptParser(path)
        self._collect_mod_info()
        super().__init__(self.mod_name, self.file_path)

    def _collect_mod_info(self):
        self.mod_name = next(
            (node.value.value for node in self.descriptor_object.nodes
            if isinstance(node, GenericKeyValue) and node.key == "name"), None
        )
        self.file_path = next(
            (Path(node.value.value.strip('"')) for node in self.descriptor_object.nodes
            if isinstance(node, GenericKeyValue) and node.key == "path"), None
        )
        AppLogger.info(f"loading {self.mod_name}@{self.file_path}")