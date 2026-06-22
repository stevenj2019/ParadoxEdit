#debug import ParadoxParser
# from pathlib import Path
# import sys
# sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "ParadoxParser"))

#all imports for mod loading here
from sys import exit
from PyQt5.QtWidgets import QApplication, QDialog
from gui import MainWindow
from gui.settings import SettingsWindow
from gui.file_dialogue import select_mod_file
from gui.warning_messages import could_not_load_mod_critical
from Configuration import ConfigurationFile
import qdarktheme

app = QApplication([])
config = ConfigurationFile()
app.setStyleSheet(qdarktheme.load_stylesheet("dark" if config.dark_mode else "light"))
if not config.initalised:
    settings = SettingsWindow("PDXEdit Setup", config)
    if settings.exec_() == QDialog.Accepted:    
        mod_path = select_mod_file(config=config)
        try:
            from ModClasses.ParadoxMod import ParadoxMod
            mod = ParadoxMod(mod_path)
        except Exception as e:
            error = could_not_load_mod_critical(e)
            error.exec_()
            exit()
else:
    mod_path = select_mod_file(config=config)
    try:
        from ModClasses.ParadoxMod import ParadoxMod
        mod = ParadoxMod(mod_path)
    except Exception as e:
        error = could_not_load_mod_critical(e)
        exit()
window = MainWindow(mod, config)
window.show()
app.exec_()
