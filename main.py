#all imports for mod loading here
from sys import exit
from PyQt5.QtWidgets import QApplication
from gui.main import MainWindow
from gui.file_dialogue import select_and_load_mod  # still optional

app = QApplication([])
mod = select_and_load_mod()
if not mod:
    exit()
window = MainWindow(mod)
window.show()
app.exec_()