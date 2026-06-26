import json
from pathlib import Path
from platformdirs import user_config_dir

from PyQt5.QtWidgets import (QTreeWidget, QTreeWidgetItem, QWidget)
from PyQt5.QtGui import QColor as QColour

from ParadoxParser.ParadoxNodes import (GenericKeyValue, GenericNode,
                                        GenericComment, GenericString, GenericToken, 
                                        GenericInt, GenericFloat, GenericBool)

from App.Constants import ChangeState
from App.GUI.Widgets import text_editor, bool_dropdown, int_editor, float_editor
from App.ModClasses import ParadoxMod

class ConfigurationManager:
    def __init__(self):
        self.file_path:Path = Path(user_config_dir("PDXEdit"), "config.json")
        self.game_install_path:Path = ""
        self.mod_file_path:Path = ""
        self.safe_mode:bool = True
        self.dark_mode:bool = False

        if self.file_path.exists():
            self.initalised = True
            self.read_file()
        else:
            self.initalised = False
    
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

        self.initalised = True

    def write_file(self):
        with open(self.file_path, "w") as CONFIG_FILE:
            json.dump(self.to_json(), CONFIG_FILE)

class StyleManager:
    def __init__(self, config):
        self.config = config
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

    def get_state_colour(self, state):
        if self.config.dark_mode:
            self.dark_mode_palette.get(state)
        else:
            self.light_mode_palette.get(state)

class InlineEditManager:
    def __init__(self, mutate_callback):
        self.cell_editors = {
            GenericComment: text_editor,
            GenericString:  text_editor,
            GenericToken:   text_editor,
            GenericInt:     int_editor,
            GenericFloat:   float_editor,
            GenericBool:    bool_dropdown
        }
        self.mutate_callback = mutate_callback
        # self.main_controller = main_controller
        self.parent:QTreeWidget = None
        self.source:QTreeWidgetItem = None
        self.node:GenericNode = None
        self.editor:QWidget = None

    @property
    def active(self): return self.editor is not None

    def open_request(self,
                parent:QTreeWidget, 
                source:QTreeWidgetItem, 
                node:GenericNode|GenericKeyValue):
        if self.active:
            print("open_request when already open")
            pass #manage destruction pipeline
        self.parent = parent
        self.source = source
        self.node = node.value if isinstance(node, GenericKeyValue) else node
        self.editor = self._get_widget()
        print(f"{self.editor} created")
        self._create()

    def complete_request(self, new_value):
        print(f"{self.node}, {self.node.value} to {new_value}")
        if self.node.value != new_value:
            self.mutate_callback(self.node, new_value)
            # self.main_controller._mutate_node(self.node, new_value)
        self._destroy()
        self._clear()

    def cancel_request(self, reason):
        if self.active:
            print(f"{self.editor} cancelled due to {reason}, value: {self.node.value}")
            self._destroy()
        self._clear()

    def _get_widget(self):
        def emit(value):
            self.complete_request(value)
        try:
            editor_fn = self.cell_editors.get(type(self.node))
        except Exception as e:
            print(e)
            return None
        return editor_fn(self.node, emit)

    def _create(self):
        self.parent.setItemWidget(self.source, 1, self.editor)
        self.editor.setFocus()

    def _destroy(self):
        self.parent.removeItemWidget(self.source, 1)
        self.editor.deleteLater()

    def _clear(self):
        self.parent = None
        self.source = None
        self.node = None
        self.editor = None

class ChangeTracker:
    def __init__(self):
        self._changes = {}

    def dirty(self, node):
        return self.get_state(node) is not ChangeState.CLEAN

    def set_state(self, node, state):
        self._changes[node] = state

    def get_state(self, node):
        return self._changes.get(node, ChangeState.CLEAN)

    def clear(self, node):
        self._changes.pop(node, None)

class FilesystemMananger:
    def __init__(self):
        self.mod = None

    def load_mod(self, path):
        self.mod = ParadoxMod(path)
