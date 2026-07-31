import os
from pathlib import Path

from App.AppLogger import AppLogger
from App.Contexts.Base import ParadoxContext, ReadOnlyContext
from App.Loading.Directories import DIRECTORY_REGISTRY
from App.Loading.Directories.Base import GenericDirectory
from App.Loading.Models import FileReference
from ParadoxParser import ParadoxScriptParser
from ParadoxParser.ParadoxNodes import GenericBlock, GenericKeyValue

PARADOX_ROOT_DIRECTORIES = [
    "common",
    "events",
    "gfx",
    "history",
    "interface",
    "localisation",
    "map",
    "music",
    "portraits",
    "sound",
]

class ParadoxSource:
    def __init__(
        self,
        name: str,
        path: Path,
        context_override: ParadoxContext = None,
        read_only_override: bool = None,
    ) -> None:
        self.source_name = name
        self.file_path = path
        self.read_only = read_only_override

        self.context_override = context_override
        self.read_only_override = read_only_override

        self.context = (
            self.context_override if self.context_override else ParadoxContext
        )
        self.root = GenericDirectory(self, self.file_path, {})
        self.directories = {Path("."): self.root}
        self._build_tree()

    def _build_tree(self) -> None:
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
                directory = self._create_directory(
                    Path(os.path.join(root, directory_name))
                )

                parent.add_directory(directory)
                self.directories[directory_path] = directory

            for file_name in files:
                file_path = Path(os.path.join(root, file_name))
                if file_path.suffix != ".bak":
                    parent.add_file(file_path, file_name)

    def _ensure_directory(self, path:Path) -> None:
        # relative = path.relative_to(self.file_path)
        if path in self.directories:
            return self.directories[path]
        parent = self._ensure_directory(path.parent)
        directory = self._create_directory(self.file_path / path)
        parent.add_directory(directory)
        self.directories[path] = directory
        return directory
    
    def _create_directory(self, path: Path) -> None:
        matches = []
        rel_path = path.relative_to(self.file_path)

        for registered_path, directory_type in DIRECTORY_REGISTRY.items():
            registered_path = Path(registered_path)
            try:
                rel_path.relative_to(registered_path)
                matches.append((len(registered_path.parts), directory_type))
            except ValueError:
                pass

        directory = max(matches, default=(0, GenericDirectory))[1]

        return directory(
            source=self, file_path=path, read_only=isinstance(self, ParadoxVanilla)
        )

    def apply_replace_path(self, path: Path) -> None:
        try:
            removed = self.directories[Path(path)]
            removed.delete_directory()
            # AppLogger.info(f"{self.source_name} {path} removed {removed}")
        except KeyError:
            pass

    def apply_override(self, path: Path) -> None:
        try:
            removed = self.directories[path.parent]
            removed.delete_file(path.name)
            # AppLogger.info(f"{self.source_name} {path} removed")
        except KeyError:
            pass


class ParadoxVanilla(ParadoxSource):
    def __init__(self, path: Path) -> None:
        super().__init__("Vanilla", path, ReadOnlyContext, True)

    def _apply_dlc_files(self) -> None:
        dlc_path = Path(os.path.join(self.file_path, "dlc"))
        dlcs = [
            Path(os.path.join(dlc_path, f))
            for f in os.listdir(dlc_path)
            if os.path.ispath(os.path.join(dlc_path, f))
        ]
        for dlc in dlcs:
            for root, dirs, files in os.walk(dlc):
                for file in files:
                    path = Path(os.path.join(root, file))
                    relative_path = path.relative_to(dlc)
                    directory = self.directories[relative_path.parent]
                    directory.add_file(path, file)


class ParadoxMod(ParadoxSource):
    def __init__(self, path: Path) -> None:
        self.descriptor_file = path.name
        self.descriptor_object = FileReference(
            None, ParadoxScriptParser(path), ParadoxContext, False
        )
        self._collect_mod_info()
        super().__init__(self.mod_name, self.file_path)

    def _collect_mod_info(self) -> None:
        descriptor_file = self.descriptor_object.file
        self.mod_name = next(
            (
                node.value.value
                for node in descriptor_file.nodes
                if isinstance(node, GenericKeyValue) and node.key == "name"
            ),
            None,
        )
        self.file_path = next(
            (
                Path(node.value.value.strip('"'))
                for node in descriptor_file.nodes
                if isinstance(node, GenericKeyValue) and node.key == "path"
            ),
            None,
        )
        self.replace_paths = [
            node.value.value
            for node in descriptor_file.nodes
            if isinstance(node, GenericKeyValue) and node.key.lower() == "replace_path"
        ]
        self.dependencies = []
        for node in descriptor_file.nodes:
            if isinstance(node, GenericBlock) and node.key == "dependencies":
                self.dependencies = [node.value for node in node.nodes]

        AppLogger.info(f"loading {self.mod_name}@{self.file_path}")
