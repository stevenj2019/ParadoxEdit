#debug import ParadoxParser
# from pathlib import Path
# import sys
# sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "ParadoxParser"))

#all imports for mod loading here
from sys import exit
from PyQt5.QtWidgets import QApplication, QDialog
from gui import MainWindow
from gui.menus.top_bar.sub_windows.settings import SettingsWindow
from gui.dialogues.file_dialogue import select_mod_file
from gui.dialogues.warning_messages import could_not_load_mod_critical
from Configuration import ConfigurationFile
import qdarktheme

app = QApplication([])
config = ConfigurationFile()
app.setStyleSheet(qdarktheme.load_stylesheet("dark" if config.dark_mode else "light"))
if not config.initalised:
    settings = SettingsWindow("PDXEdit Setup", config)
    if not settings.exec_() == QDialog.Accepted:
        exit()

window = MainWindow(config)
window.show()
app.exec_()
