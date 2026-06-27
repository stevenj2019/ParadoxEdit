from pathlib import Path
import qdarktheme

from PyQt5.QtWidgets import QApplication, QDialog, QFormLayout, QHBoxLayout, QLabel, QCheckBox, QLineEdit, QPushButton, QDialogButtonBox

from App.GUI.Dialogues.FileDialogues import select_hoi4_install_directory, select_mod_directory
from App.GUI.Dialogues.PopupModels import settings_error_critical

class SettingsWindow(QDialog):
    def __init__(self, title:str, parent):
        super().__init__()
        self.config = parent.app_controller.config
        self.setWindowTitle(title)
        self.resize(550,150)
        self.setLayout(QFormLayout())
        self.form = self.layout()

        self.config_file_label = QLabel(f"Configuration will be stored at: {self.config.file_path.absolute()}")
        self.form.addRow(self.config_file_label)

        self.game_install_path_label = QLabel("Paradox Game Path:")
        self.game_install_path_element = QHBoxLayout()
        self.game_install_path_element_text = QLineEdit()
        self.game_install_path_element_text.setText(str(self.config.game_install_path))
        self.game_install_path_element_button = QPushButton("...")
        self.game_install_path_element.addWidget(self.game_install_path_element_text)
        self.game_install_path_element.addWidget(self.game_install_path_element_button)
        self.game_install_path_element_button.clicked.connect(self.browse_game_install_path)
        self.form.addRow(self.game_install_path_label, self.game_install_path_element)

        self.mod_install_path_label = QLabel("Paradox Mods Path:")
        self.mod_install_path_element = QHBoxLayout()
        self.mod_install_path_element_text = QLineEdit()
        self.mod_install_path_element_text.setText(str(self.config.mod_file_path))
        self.mod_install_path_element_button = QPushButton("...")
        self.mod_install_path_element.addWidget(self.mod_install_path_element_text)
        self.mod_install_path_element.addWidget(self.mod_install_path_element_button)
        self.mod_install_path_element_button.clicked.connect(self.browse_mod_install_path)
        self.form.addRow(self.mod_install_path_label, self.mod_install_path_element)

        self.safe_mode_label = QLabel("Safe Mode:")
        self.safe_mode_check = QCheckBox()
        self.safe_mode_check.setChecked(self.config.safe_mode)
        self.safe_mode_label.setBuddy(self.safe_mode_check)
        self.form.addRow(self.safe_mode_label, self.safe_mode_check)

        self.dark_mode_label = QLabel("Use Dark Mode?:")
        self.dark_mode_check = QCheckBox()
        self.dark_mode_check.setChecked(self.config.dark_mode)
        self.dark_mode_label.setBuddy(self.dark_mode_check)
        self.form.addRow(self.dark_mode_label, self.dark_mode_check)
        self.dark_mode_check.toggled.connect(self.toggle_dark_mode)

        self.button = QDialogButtonBox(QDialogButtonBox.Save)
        self.form.addRow(self.button)
        self.button.accepted.connect(self.submit_form)

    def browse_game_install_path(self):
        path = select_hoi4_install_directory()
        if path:
            self.game_install_path_element_text.setText(path)

    def browse_mod_install_path(self):
        path = select_mod_directory()
        if path:
            self.mod_install_path_element_text.setText(path)
    
    def toggle_dark_mode(self):
        self.config.change_setting(dark_mode = not(self.config.dark_mode))
        app = QApplication.instance()
        app.setStyleSheet(qdarktheme.load_stylesheet("dark" if self.config.dark_mode else "light"))

    def submit_form(self):
        game_dir_error = False
        mod_dir_error = False
        
        game_folder = Path(self.game_install_path_element_text.text().strip())
        if not (game_folder.is_dir() and (game_folder / "pdx_launcher")):
           game_dir_error = True
        mod_folder = Path(self.mod_install_path_element_text.text().strip())
        if not (mod_folder.is_dir() and any(mod_folder.glob("*.mod"))):
            mod_dir_error = True
        
        if not (game_dir_error or mod_dir_error):
            self.config.change_setting(safe_mode = self.safe_mode_check.isChecked() )
            self.config.change_setting(dark_mode = self.dark_mode_check.isChecked() )
            self.config.change_setting(game_install_path = game_folder)
            self.config.change_setting(mod_file_path = mod_folder)
            self.config.write_file()
            self.accept()
        else:
            settings_error_critical(game_dir_error, mod_dir_error)