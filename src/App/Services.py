from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App.Loading.LoadOrder import ParadoxLoadOrder
    from App.Loading.ParadoxSource import ParadoxSource

import json
import sys
from pathlib import Path

from platformdirs import user_config_dir

from App.AppLogger import AppLogger
from App.Contracts import OpenFile
from App.Contracts.Enums import ChangeState
from App.Enums import PDXMetadata, PDXTokens
from App.Loading.Models import FileReference
from ParadoxParser import ParadoxLocParser as PDXLocFile
from ParadoxParser import ParadoxScriptParser as PDXScriptFile
from ParadoxParser.ParadoxNodes import GenericBlock, GenericNode

app_name = "PDXEdit"


class ConfigurationManager:
    def __init__(self) -> None:
        self.file_path: Path = Path(user_config_dir(app_name), "configuration.json")
        self.game_install_path: Path = ""
        self.mod_file_path: Path = ""
        self.safe_mode: bool = True
        self.dark_mode: bool = False
        self.initialised = False

        if self.file_path.exists():
            self.initialised = True
            self.read_file()

    def change_setting(self, **kwargs: Path | bool) -> None:
        for k, v in kwargs.items():
            if not hasattr(self, k):
                raise AttributeError(f"Unknown setting: {k}")
            setattr(self, k, v)

    def to_json(self) -> dict:
        return {
            "safe_mode": self.safe_mode,
            "game_install_path": str(self.game_install_path),
            "mod_file_path": str(self.mod_file_path),
            "dark_mode": self.dark_mode,
        }

    def read_file(self) -> None:
        try:
            settings = json.load(self.file_path.open())
        except json.decoder.JSONDecodeError as e:
            AppLogger.error(f"Invalid file at {str(self.file_path)}")
            AppLogger.exception(e)
            sys.exit()

        self.safe_mode = settings["safe_mode"]
        self.game_install_path = Path(settings["game_install_path"])
        self.mod_file_path = Path(settings["mod_file_path"])
        self.dark_mode = settings["dark_mode"]

    def create_file(self) -> None:
        self.safe_mode = True
        self.dark_mode = False
        self.file_path.parent.mkdir(exist_ok=True, parents=True)
        self.file_path.touch()

    def write_file(self) -> None:
        with open(self.file_path, "w") as CONFIG_FILE:
            json.dump(self.to_json(), CONFIG_FILE)
        self.initialised = True

class ChangeTracker:
    def __init__(self) -> None:
        self.node_changes = {}
        self.file_changes = {}

    def node_is_dirty(self, node: GenericNode) -> bool:
        return self.get_node_state(node) is not None

    def set_node_state(self, node: GenericNode, state: ChangeState) -> None:
        AppLogger.mutation(node, state)
        self.node_changes[node] = state

    def get_node_state(self, node: GenericNode) -> ChangeState:
        return self.node_changes.get(node, None)

    def clear_node_state(self, node: GenericNode) -> None:
        self.node_changes.pop(node, None)

    def file_is_dirty(self, file: FileReference) -> bool:
        return self.get_file_state(file) is not None

    def set_file_state(self, file: FileReference, state: ChangeState) -> None:
        AppLogger.mutation(file, state)
        self.file_changes[file] = state

    def get_file_state(self, file: FileReference) -> ChangeState:
        return self.file_changes.get(file, None)

    def clear_file_state(self, file: FileReference) -> None:
        def recurse(node: GenericNode) -> None:
            self.clear_node_state(node)
            if isinstance(node, GenericBlock):
                for _node in node.nodes:
                    recurse(_node)

        self.file_changes.pop(file, None)
        if file:
            try:
                for node in file.file.nodes:
                    recurse(node)
            except AttributeError:
                pass


class Workspace:
    def __init__(self) -> None:
        self.vanilla_loaded: bool = False
        self.mods: list[str] = []

    def set_vanilla_status(self, enabled: bool) -> None:
        self.vanilla_loaded = enabled

    def add_mod_to_workspace(self, descriptor_path: Path) -> None:
        if descriptor_path not in self.mods:
            self.mods.append(descriptor_path)

    def _to_json(self) -> dict:
        return {"vanilla_loaded": self.vanilla_loaded, "mods": [str(mod) for mod in self.mods]}

    def read_file(self, path: Path) -> None:
        with path.open("r", encoding="UTF-8") as FILE:
            config = json.load(FILE)

        self.vanilla_loaded = config["vanilla_loaded"]
        # self.mods = config["mods"]
        for mod in config["mods"]:
            mod_path = Path(mod)
            self.mods.append(mod_path)

    def write_file(self, path: Path) -> None:
        # file_path = Path(path)
        path.touch()
        with path.open("w", encoding="UTF-8") as CONFIG_FILE:
            json.dump(self._to_json(), CONFIG_FILE)


class FilesystemMananger:
    def __init__(self, configuration: ConfigurationManager) -> None:
        self.workspace: Workspace = Workspace()
        self.load_order: ParadoxLoadOrder = None

        self.configuration = configuration
        self.change_tracker = ChangeTracker()

        self.open_file: OpenFile = None

    def load_workspace(
        self, workspace: Workspace, load_order: ParadoxLoadOrder
    ) -> None:
        self.workspace = workspace
        self.load_order = load_order

    def load_file(self, file: OpenFile) -> None:
        self.open_file = file

    def changed_file(
        self, file: FileReference, node: GenericNode, status: ChangeState
    ) -> None:
        self.change_tracker.set_file_state(file, status)
        self.change_tracker.set_node_state(node, status)

    def collect_deletion_nodes(self, file: PDXScriptFile | PDXLocFile) -> None:
        deletions = []

        def recurse(
            parent: PDXScriptFile | PDXLocFile | GenericBlock, node: GenericNode
        ) -> None:
            if self.change_tracker.get_node_state(node) == ChangeState.DELETED:
                index = parent.nodes.index(node)
                deletions.append((parent, index, node))
                return
            if isinstance(node, GenericBlock):
                for child in node.nodes:
                    recurse(node, child)

        try:
            for node in file.nodes:
                recurse(file, node)
        except AttributeError:
            return deletions

    def cleanup_deletion_nodes(self, file: FileReference) -> None:
        deletions = self.collect_deletion_nodes(file)
        try:
            for parent, index, node in sorted(
                deletions, key=lambda x: x[1], reverse=True
            ):
                self.change_tracker.clear_node_state(node)
                parent.nodes.pop(index)
        except TypeError:
            return

    def save_file(self, file: FileReference = None) -> bool:
        self.cleanup_deletion_nodes(file.file)
        if self.change_tracker.file_is_dirty(file) and not file.read_only:
            file.file.filepath.parent.mkdir(parents=True, exist_ok=True)
            self.change_tracker.clear_file_state(file)
            file.commit(self.configuration.safe_mode)
            return True
        else:
            return False


class ParadoxRegistry:
    def __init__(self) -> None:
        self.tokens: dict[PDXTokens, dict[FileReference, set]] = {}
        self.metadata: dict[PDXMetadata, dict[FileReference, dict]] = {}

        self.tokens_cache: dict[PDXTokens, set] = {}
        self.metadata_cache: dict[PDXTokens, dict] = {}

    def get_tokens(self, key: PDXTokens) -> None:
        return self.tokens_cache.get(key, set())

    # def add_tokens(self, key, tokens:set):
    # def remove_tokens(self, key, tokens:set):

    def get_metadata(self, key: PDXMetadata) -> None:
        return self.metadata_cache.get(key, dict())
    # def add_metadata():
    # def remove_metadata():

    def invalidate(self) -> None:
        self.tokens.clear()
        self.metadata.clear()

    def load_file_data(self, source:ParadoxSource, file:FileReference) -> None:
        self._merge_registry(
            self.tokens, file, file.directory.token_collection(source, file)
        )
        self._merge_registry(
            self.metadata, file, file.directory.metadata_collection(source, file)
        )

    def _merge_registry(self, target: dict, file:FileReference, insertions: dict | set) -> None:
        for key, value in insertions.items():
            if key not in target:
                target[key] = dict()
            target[key][file] = value

    def purge_file_data(self, file:FileReference) -> None:
        for file_data in self.tokens.values():
            file_data.pop(file, None)
        for file_data in self.metadata.values():
            file_data.pop(file, None)

    def _build_registry_cache(self) -> None:
        self.tokens_cache.clear()
        self.metadata_cache.clear()

        for key, token in self.tokens.items():
            merged = set()
            for data in token.values():
                merged.update(data)
            self.tokens_cache[key] = merged

        for key, metadata in self.metadata.items():
            merged = type(next(iter(metadata.values())))()

            for data in metadata.values():
                if isinstance(data, dict):
                    merged.update(data)
                else:
                    merged.update(data)

            self.metadata_cache[key] = merged