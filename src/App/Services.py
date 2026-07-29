from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App.Loading.LoadOrder import ParadoxLoadOrder

import json
import logging
import sys
from datetime import datetime
from pathlib import Path

from platformdirs import user_config_dir, user_log_dir

from App.Contracts import OpenFile
from App.Contracts.Enums import ChangeState
from ParadoxParser import ParadoxLocParser as PDXLocFile
from ParadoxParser import ParadoxScriptParser as PDXScriptFile
from ParadoxParser.ParadoxNodes import GenericBlock, GenericKeyValue, GenericNode

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


class AppLogger:
    _logger = logging.getLogger(app_name)

    @classmethod
    def initialise(cls) -> None:
        log_directory = Path(user_log_dir(app_name))
        log_directory.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_file = log_directory / f"{app_name}-{timestamp}.log"

        cls._logger.setLevel(logging.DEBUG)
        if cls._logger.handlers:
            return

        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        # file out
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        cls._logger.addHandler(file_handler)
        # console out
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        cls._logger.addHandler(console_handler)
        cls.info(f"Logging initialised: {log_file}")

    @classmethod
    def debug(cls, message: str) -> None:
        cls._logger.debug(cls._format(message))

    @classmethod
    def info(cls, message: str) -> None:
        cls._logger.info(cls._format(message))

    @classmethod
    def warning(cls, message: str) -> None:
        cls._logger.warning(cls._format(message))

    @classmethod
    def error(cls, message: str) -> None:
        cls._logger.error(cls._format(message))

    @classmethod
    def exception(cls, exc: Exception) -> None:
        cls._logger.exception(exc)

    @classmethod
    def mutation(cls, node: GenericNode, state: ChangeState) -> None:
        cls.info(f"Setting {cls._format(node)} -> {state}")

    @staticmethod
    def _format(obj: GenericNode | PDXScriptFile | PDXLocFile) -> None:
        if isinstance(obj, (PDXScriptFile, PDXLocFile)):
            return f"{obj.filename}"

        if isinstance(obj, GenericBlock):
            return f"{obj.key} {{...}}"

        if isinstance(obj, GenericKeyValue):
            return f"{obj.key} = {obj.value}"

        if isinstance(obj, GenericNode):
            return str(obj.value)

        return str(obj)


class ChangeTracker:
    def __init__(self) -> None:
        self.node_changes = {}
        self.file_changes = {}

    def node_is_dirty(self, node) -> bool:
        return self.get_node_state(node) is not None

    def set_node_state(self, node, state) -> None:
        AppLogger.mutation(node, state)
        self.node_changes[node] = state

    def get_node_state(self, node) -> ChangeState:
        return self.node_changes.get(node, None)

    def clear_node_state(self, node) -> None:
        self.node_changes.pop(node, None)

    def file_is_dirty(self, file) -> bool:
        return self.get_file_state(file) is not None

    def set_file_state(self, file, state) -> None:
        AppLogger.mutation(file, state)
        self.file_changes[file] = state

    def get_file_state(self, file) -> ChangeState:
        return self.file_changes.get(file, None)

    def clear_file_state(self, file) -> None:
        def recurse(node) -> None:
            self.clear_node_state(node)
            if isinstance(node, GenericBlock):
                for _node in node.nodes:
                    recurse(_node)

        self.file_changes.pop(file, None)
        if file:
            try:
                for node in file.nodes:
                    recurse(node)
            except AttributeError:
                pass


class Workspace:
    def __init__(self) -> None:
        self.vanilla_loaded: bool = False
        self.mods: list[str] = []

    def set_vanilla_status(self, enabled: bool) -> None:
        self.vanilla_loaded = enabled

    def add_mod_to_workspace(self, descriptor_path: str) -> None:
        if descriptor_path not in self.mods:
            self.mods.append(descriptor_path)

    def _to_json(self) -> dict:
        return {"vanilla_loaded": self.vanilla_loaded, "mods": self.mods}

    def read_file(self, file_path) -> None:
        with open(str(file_path)) as FILE:
            file_path = json.load(FILE)

        self.vanilla_loaded = file_path["vanilla_loaded"]
        self.mods = file_path["mods"]

    def write_file(self, path) -> None:
        file_path = Path(path)
        file_path.touch()
        with open(file_path, "w") as CONFIG_FILE:
            json.dump(self._to_json(), CONFIG_FILE)


class FilesystemMananger:
    def __init__(self, configuration) -> None:
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

    def changed_file(self, file, node, status) -> None:
        self.change_tracker.set_file_state(file, status)
        self.change_tracker.set_node_state(node, status)

    def collect_deletion_nodes(self, file) -> None:
        deletions = []

        def recurse(parent, node) -> None:
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

    def cleanup_deletion_nodes(self, file) -> None:
        deletions = self.collect_deletion_nodes(file)
        try:
            for parent, index, node in sorted(
                deletions, key=lambda x: x[1], reverse=True
            ):
                self.change_tracker.clear_node_state(node)
                parent.nodes.pop(index)
        except TypeError:
            return

    def save_file(self, file=None) -> bool:
        self.cleanup_deletion_nodes(file.file)
        if self.change_tracker.file_is_dirty(file) and not file.read_only:
            self.change_tracker.clear_file_state(file)
            file.commit(self.configuration.safe_mode)
            return True
        else:
            return False


class ParadoxRegistry:
    def __init__(self) -> None:
        self.tokens: dict[str, set] = {}
        self.metadata: dict[str, dict] = {}

    def load_tokens(self, tokens: dict) -> None:
        self.tokens = tokens

    def get_tokens(self, key) -> None:
        return self.tokens.get(key, set())

    # def add_tokens(self, key, tokens:set):
    # def remove_tokens(self, key, tokens:set):

    def load_metadata(self, metadata: dict) -> None:
        self.metadata = metadata

    def get_metadata(self, key) -> None:
        return self.metadata.get(key, dict())

    # def add_metadata():
    # def remove_metadata():
