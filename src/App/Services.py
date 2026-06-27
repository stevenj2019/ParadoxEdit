import json
from pathlib import Path
from platformdirs import user_config_dir

from PyQt5.QtGui import QColor as QColour

from ParadoxParser.ParadoxNodes import GenericBlock

from App.Enums import ChangeState
from App.ModClasses import ParadoxMod

class Services:
    def __init__(self, app):
        self.configuration = app.configuration
        self.file_system =   app.file_system
        self.style_manager = app.style_manager

class ConfigurationManager:
    def __init__(self):
        self.file_path:Path = Path(user_config_dir("PDXEdit"), "configuration.json")
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
    def __init__(self, configuration):
        self.configuration = configuration
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
        if self.configuration.dark_mode:
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
        def recurse(node):
            self.clear_node_state(node)
            if isinstance(node, GenericBlock):
                for _node in node.nodes:
                    recurse(_node)
        self.file_changes.pop(file, None)
        if file:
            for node in file.nodes:
                recurse(node)
            
class FilesystemMananger:
    def __init__(self, configuration):
        self.configuration = configuration
        self.change_tracker = ChangeTracker()
        self.mod = None
        self.open_file = None

    def load_mod(self, path):
        self.mod = ParadoxMod(path)

    def load_file(self, file):
        self.open_file = file

    def changed_file(self, file, node, status):
        self.change_tracker.set_file_state(file, status)
        self.change_tracker.set_node_state(node, status)

    def save_file(self, file=None):
        if self.change_tracker.file_is_dirty(file):
            self.change_tracker.clear_file_state(file)
            if self.configuration.safe_mode:
                file.backup_file()
            file.to_pdx_file()
            return True
        else:
            return False