import json
from pathlib import Path
from platformdirs import user_config_dir

from PyQt5.QtWidgets import (QTreeWidget, QTreeWidgetItem, QWidget)
from PyQt5.QtGui import QColor as QColour

from ParadoxParser.ParadoxNodes import (GenericKeyValue, GenericNode,
                                        GenericComment, GenericString, GenericToken, 
                                        GenericInt, GenericFloat, GenericBool)

from App.Constants import ChangeState
from App.ModClasses import ParadoxMod

from App.GUI.InLineWidgets import text_editor, bool_dropdown, int_editor, float_editor

class ConfigurationManager:
    def __init__(self):
        self.file_path:Path = Path(user_config_dir("PDXEdit"), "config.json")
        self.game_install_path:Path = ""
        self.mod_file_path:Path = ""
        self.safe_mode:bool = True
        self.dark_mode:bool = False

        if self.file_path.exists():
            self.initialised = True
            self.read_file()
        else:
            self.initialised = False
    
    def change_setting(self, **kwargs):
        for k, v in kwargs.items():
            if not hasattr(self, k):
                raise AttributeError(f"Unknown setting: {k}")
            setattr(self, k, v)

    def to_json(self):
        return {
            'safe_mode': self.safe_mode,
            'game_install_path': str(self.game_install_path),
            'mod_file_path': str(self.mod_file_path),
            'dark_mode': self.dark_mode
        }
    
    def read_file(self):
        settings = json.load(self.file_path.open())
        self.safe_mode = settings['safe_mode']
        self.game_install_path = Path(settings['game_install_path'])
        self.mod_file_path = Path(settings['mod_file_path'])
        self.dark_mode = settings['dark_mode']

    def create_file(self):
        self.safe_mode = True
        self.dark_mode = False
        self.file_path.parent.mkdir(exist_ok=True, parents=True)
        self.file_path.touch()

        self.initialised = True

    def write_file(self):
        with open(self.file_path, "w") as CONFIG_FILE:
            json.dump(self.to_json(), CONFIG_FILE)

class StyleManager:
    def __init__(self, controller):
        self.controller = controller
        self.dark_mode_palette = {
            ChangeState.MODIFIED: QColour("#545703"),
            ChangeState.ADDED: QColour("#04450c"),
            ChangeState.DELETED: QColour("#400308"),
        }
        self.light_mode_palette = {
            ChangeState.MODIFIED: QColour("yellow"),
            ChangeState.ADDED: QColour("green"),
            ChangeState.DELETED: QColour("red"),
        }

    def get_node_state_colour(self, state):
        if self.controller.config.dark_mode:
            return self.dark_mode_palette.get(state)
        else:
            return self.light_mode_palette.get(state)

class ChangeTracker:
    def __init__(self):
        self.node_changes = {}
        self.file_changes = {}

    def node_is_dirty(self, node):
        return self.get_node_state(node) is not ChangeState.CLEAN

    def set_node_state(self, node, state):
        self.node_changes[node] = state

    def get_node_state(self, node):
        return self.node_changes.get(node, ChangeState.CLEAN)

    def clear_node_state(self, node):
        self.node_changes.pop(node, None)

    def file_is_dirty(self, file):
        return self.get_file_state(file) is not ChangeState.CLEAN
    
    def set_file_state(self, file, state):
        self.file_changes[file] = state

    def get_file_state(self, file):
        return self.file_changes.get(file, ChangeState.CLEAN)

    def clear_file_state(self, file):
        self.file_changes.pop(file, None)

class FilesystemMananger:
    def __init__(self, controller):
        self.controller = controller
        self.mod = None
        self.open_file = None

    def load_mod(self, path):
        self.mod = ParadoxMod(path)

    def load_file(self, file):
        self.open_file = file

    def save_file(self, file):
        if self.controller.config.safe_mode:
            file.obj._backup_file()
        file.obj._to_pdx_file()