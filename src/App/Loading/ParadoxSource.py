from pathlib import Path
import os

from App.Services import AppLogger
from App.Loading.Directories.Base import GenericDirectoryContext
from App.Loading.Directories import DIRECTORY_REGISTRY
from ParadoxParser import ParadoxScriptParser
from ParadoxParser.ParadoxNodes import GenericBlock, GenericKeyValue

PARADOX_ROOT_DIRECTORIES = ["common", "events", "gfx", "history", "interface", "localisation", "map", "music", "portraits", "sound"]
EXCLUDE_FILES = [""]
class ParadoxSource:
    def __init__(self, name, path):
        self.source_name = name
        self.file_path = path
        self.root = GenericDirectoryContext(self.file_path, GenericDirectoryContext)
        self.directories = {
            Path("."): self.root
        }
        self._build_tree()

    def parse_files(self):
        self.root.parse_files()

    def _build_tree(self):
        for root, dirs, files in os.walk(self.file_path):
            root = Path(root)

            relative_root = root.relative_to(self.file_path)
            parent = self.directories[relative_root]
            
            if relative_root == Path("."):
                dirs[:] = [dir for dir in dirs if dir in PARADOX_ROOT_DIRECTORIES]
            dirs.sort()
            files.sort()
            for directory_name in dirs:
                directory_path = relative_root / directory_name
                directory = self._create_directory(Path(os.path.join(root, directory_name)))

                parent.add_directory(directory)
                self.directories[directory_path] = directory

            for file_name in files:
                file_path = Path(os.path.join(root, file_name))
                if file_path.suffix != ".bak":
                    parent.add_file(file_path, file_name)

    def _create_directory(self, path):
        rel_path = path.relative_to(self.file_path)
        category = DIRECTORY_REGISTRY.get(
            str(rel_path),
            GenericDirectoryContext
        )
        print(path, category)
        return category(path)
    
    def apply_replace_path(self, path):
        try:
            removed = self.directories[Path(path)]
            removed.delete_directory()
            AppLogger.info(f"Vanillas {path} removed {removed}")
        except KeyError:
            pass

    def apply_override(self, path):
        try:
            removed = self.directories[path.parent]
            removed.delete_file(path.name)
            AppLogger.info(f"Vanillas {path} removed")
        except KeyError:
            pass

    def token_collection(self):
        return self.root.token_collection_traversal()

class ParadoxVanilla(ParadoxSource):
    def __init__(self, path):
        super().__init__("Vanilla", path)

    def _apply_dlc_files(self):
        dlc_path = Path(os.path.join(self.file_path, "dlc"))
        dlcs = [Path(os.path.join(dlc_path, f)) for f in os.listdir(dlc_path) if os.path.ispath(os.path.join(dlc_path, f))]
        for dlc in dlcs:
            for root, dirs, files in os.walk(dlc):
                for file in files:
                    path = Path(os.path.join(root, file))
                    relative_path = path.relative_to(dlc)
                    directory = self.directories[relative_path.parent]
                    directory.add_file(path, file)


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
        self.replace_paths = [node.value.value for node in self.descriptor_object.nodes 
                              if isinstance(node, GenericKeyValue) 
                              and node.key.lower() == "replace_path"]
        self.dependencies = []
        for node in self.descriptor_object.nodes:
            if isinstance(node, GenericBlock) and node.key == "dependencies":
                self.dependencies = [node.value for node in node.nodes]

        AppLogger.info(f"loading {self.mod_name}@{self.file_path}")