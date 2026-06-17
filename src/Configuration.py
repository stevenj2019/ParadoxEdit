import json
from pathlib import Path
from platformdirs import user_config_dir

class ConfigurationFile:
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

