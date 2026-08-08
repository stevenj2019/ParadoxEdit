import os
from collections.abc import Iterator
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from App.AppLogger import AppLogger
from App.Contexts.Base import ParadoxContext, ReadOnlyContext
from App.Loading.Directories import DIRECTORY_REGISTRY
from App.Loading.Directories.Base import GenericDirectory
from App.Loading.Models import FileReference, ParadoxDLC
from App.Services import Workspace
from ParadoxParser import ParadoxScriptParser
from ParadoxParser.ParadoxNodes import GenericBlock, GenericKeyValue
from ParadoxParser.queries import all_nodes, find_node

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
        self.context = context_override if context_override else ParadoxContext

        self.context_override = context_override
        self.read_only_override = read_only_override

        self.context = self.context_override if self.context_override else ParadoxContext
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
                directory = self._create_directory(Path(os.path.join(root, directory_name)))

                parent.add_directory(directory)
                self.directories[directory_path] = directory

            for file_name in files:
                file_path = Path(os.path.join(root, file_name))
                if file_path.suffix != ".bak":
                    parent.add_file(file_path, file_name)

    def _ensure_directory(self, path: Path) -> None:
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

        return directory(source=self, file_path=path, read_only=isinstance(self, ParadoxVanilla))

    def apply_replace_path(self, path: Path) -> None:
        try:
            removed = self.directories[Path(path)]
            removed.delete_directory()
        except KeyError:
            pass

    def apply_override(self, path: Path) -> None:
        try:
            removed = self.directories[path.parent]
            removed.delete_file(path.name)
        except KeyError:
            pass

    def iter_files(self) -> Iterator[FileReference]:
        yield from self.root.iter_files()


class ParadoxVanilla(ParadoxSource):
    def __init__(self, path: Path, workspace: Workspace._VanillaWorkspace) -> None:
        super().__init__("Vanilla", path, ReadOnlyContext, True)
        self.dlcs: list[ParadoxDLC] = list()
        self.vanilla_workspace = workspace
        self.dlc_cache = TemporaryDirectory("paradoxedit_dlc_")
        self._process_dlcs()

    def _process_dlcs(self) -> None:
        def _read_dlc_descriptor(directory: Path) -> ParadoxDLC | None:
            def _extract_dlc_archive(dlc_identifier: str, archive_path: Path) -> Path:
                extract_path = Path(self.dlc_cache.name) / dlc_identifier
                extract_path.mkdir()
                with ZipFile(archive_path, "r") as archive:
                    archive.extractall(extract_path)

                return extract_path

            descriptor = next(directory.glob("*.dlc"), None)

            if not descriptor:
                return None

            descriptor_object = ParadoxScriptParser(str(descriptor))
            dlc_identifier = descriptor.stem
            dlc_name = find_node(descriptor_object, GenericKeyValue, "name")
            dlc_rel_path = find_node(descriptor_object, GenericKeyValue, "path")
            dlc_archive = find_node(descriptor_object, GenericKeyValue, "archive")
            enabled = self.vanilla_workspace.dlcs.setdefault(dlc_identifier, True)

            assert isinstance(dlc_name, GenericKeyValue), f"{dlc_identifier} has no 'name' value"
            has_content = isinstance(dlc_rel_path, GenericKeyValue) or isinstance(
                dlc_archive, GenericKeyValue
            )
            assert has_content, f"{dlc_identifier} has no 'path' or 'archive' value"

            if dlc_rel_path:
                dlc_path = self.file_path / dlc_rel_path.get_value()
            else:
                archive_path = self.file_path / dlc_archive.get_value()
                dlc_path = _extract_dlc_archive(dlc_identifier, archive_path)

            return ParadoxDLC(
                identifier=dlc_identifier, name=dlc_name.get_value(), path=dlc_path, enabled=enabled
            )

        def _load_dlc_files(directory: Path) -> None:
            for root, _, files in os.walk(directory):
                for file in files:
                    path = Path(os.path.join(root, file))
                    relative_path = path.relative_to(directory)
                    target_directory = self._ensure_directory(relative_path.parent)
                    target_directory.add_file(path, file)

        dlc_path = self.file_path / "dlc"
        for directory in sorted(path for path in dlc_path.iterdir() if path.is_dir()):
            AppLogger.info(f"loading {str(directory.name)}")
            dlc_obj = _read_dlc_descriptor(directory)
            if not dlc_obj:
                continue
            self.dlcs.append(dlc_obj)
            if dlc_obj.enabled:
                _load_dlc_files(dlc_obj.path)


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

        mod_name = find_node(descriptor_file, GenericKeyValue, "name")
        self.mod_name = mod_name.get_value() if mod_name else "Unnamed Mod"

        file_path = find_node(descriptor_file, GenericKeyValue, "path")
        self.file_path = Path(file_path.get_value()) if file_path else None

        self.replace_paths = []
        for node in all_nodes(descriptor_file, GenericKeyValue, "replace_path"):
            self.replace_paths.append(node.get_value())

        self.dependencies = []
        dependency_block = find_node(descriptor_file, GenericBlock, "dependencies")
        if dependency_block:
            self.dependencies = [node.value for node in dependency_block.nodes]
        AppLogger.info(f"loading {self.mod_name}@{self.file_path}")

    def iter_files(self) -> Iterator[FileReference]:
        yield self.descriptor_object
        yield from super().iter_files()