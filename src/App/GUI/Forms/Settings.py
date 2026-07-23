from pathlib import Path
import qdarktheme

from PyQt5.QtWidgets import QDialog, QFormLayout, QHBoxLayout, QLabel, QCheckBox, QLineEdit, QPushButton, QDialogButtonBox

from App.GUI.Widgets.FileDialogues import select_hoi4_install_directory, select_mod_directory
from App.GUI.Widgets.PopupModels import settings_error_critical

#TODO: this should not allow an exit, or if it does, it should bring the app down on first run
class SettingsForm(QDialog):
    def __init__(self, title:str, app_controller):
        super().__init__()
        self.app_controller = app_controller
        self.setWindowTitle(title)
        self.resize(550,150)
        self.setLayout(QFormLayout())
        self.form = self.layout()

        safe_mode_checked = self.app_controller.configuration.safe_mode if self.app_controller.configuration.initialised else True
        dark_mode_checked = self.app_controller.configuration.dark_mode if self.app_controller.configuration.initialised else False

        self.config_file_label = QLabel(f"Configuration will be stored at: {self.app_controller.configuration.file_path.absolute()}")
        self.form.addRow(self.config_file_label)

        self.game_install_path_label = QLabel("Paradox Game Path:")
        self.game_install_path_element = QHBoxLayout()
        self.game_install_path_element_text = QLineEdit()
        self.game_install_path_element_text.setText(str(self.app_controller.configuration.game_install_path))
        self.game_install_path_element_button = QPushButton("...")
        self.game_install_path_element.addWidget(self.game_install_path_element_text)
        self.game_install_path_element.addWidget(self.game_install_path_element_button)
        self.game_install_path_element_button.clicked.connect(self.browse_game_install_path)
        self.form.addRow(self.game_install_path_label, self.game_install_path_element)

        self.mod_install_path_label = QLabel("Paradox Mods Path:")
        self.mod_install_path_element = QHBoxLayout()
        self.mod_install_path_element_text = QLineEdit()
        self.mod_install_path_element_text.setText(str(self.app_controller.configuration.mod_file_path))
        self.mod_install_path_element_button = QPushButton("...")
        self.mod_install_path_element.addWidget(self.mod_install_path_element_text)
        self.mod_install_path_element.addWidget(self.mod_install_path_element_button)
        self.mod_install_path_element_button.clicked.connect(self.browse_mod_install_path)
        self.form.addRow(self.mod_install_path_label, self.mod_install_path_element)

        self.safe_mode_label = QLabel("Safe Mode:")
        self.safe_mode_check = QCheckBox()
        self.safe_mode_check.setChecked(safe_mode_checked)
        self.safe_mode_label.setBuddy(self.safe_mode_check)
        self.form.addRow(self.safe_mode_label, self.safe_mode_check)

        self.dark_mode_label = QLabel("Use Dark Mode?:")
        self.dark_mode_check = QCheckBox()
        self.dark_mode_check.setChecked(dark_mode_checked)
        self.dark_mode_label.setBuddy(self.dark_mode_check)
        self.form.addRow(self.dark_mode_label, self.dark_mode_check)
        self.dark_mode_check.toggled.connect(self.toggle_dark_mode)

        self.button = QDialogButtonBox(QDialogButtonBox.Save)
        self.form.addRow(self.button)
        self.button.accepted.connect(self.submit_form)

    def browse_game_install_path(self):
        path = select_hoi4_install_directory(self.app_controller.main)
        if path:
            self.game_install_path_element_text.setText(path)

    def browse_mod_install_path(self):
        path = select_mod_directory(self.app_controller.main)
        if path:
            self.mod_install_path_element_text.setText(path)
    
    def toggle_dark_mode(self):
        self.app_controller.configuration.change_setting(dark_mode = not(self.app_controller.configuration.dark_mode))
        self.app_controller.app.setStyleSheet(qdarktheme.load_stylesheet("dark" if self.app_controller.configuration.dark_mode else "light"))

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
            self.app_controller.configuration.create_file()
            self.app_controller.configuration.change_setting(safe_mode = self.safe_mode_check.isChecked() )
            self.app_controller.configuration.change_setting(dark_mode = self.dark_mode_check.isChecked() )
            self.app_controller.configuration.change_setting(game_install_path = game_folder)
            self.app_controller.configuration.change_setting(mod_file_path = mod_folder)
            self.app_controller.configuration.write_file()
            self.accept()
        else:
            settings_error_critical(game_dir_error, mod_dir_error)