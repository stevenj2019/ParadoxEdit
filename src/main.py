#all imports for mod loading here
from sys import exit
from PyQt5.QtWidgets import QApplication
from gui.main import MainWindow
from gui.file_dialogue import select_hoi4_install_directory, select_mod_file  # still optional
from Configuration import ConfigurationFile
from pathlib import Path

config = ConfigurationFile()
app = QApplication([])
if not config.initalised:
    install_location = select_hoi4_install_directory()
    if install_location:
        config.create_file()
        config.change_setting(game_install_path=Path(install_location))
    else:
        exit()
mod, path = select_mod_file(None, config)
if not mod:
    exit()
config.change_setting(mod_file_path=Path(path).parent)
config.write_file()
window = MainWindow(mod, config)
window.show()
app.exec_()