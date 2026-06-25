from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeWidgetItem, QLabel, QWidgetAction
from PyQt5.QtCore import Qt
import qdarktheme

from Configuration import ConfigurationFile

#These will go into ContextMenus Class
def build_category_list(key,val)->QTreeWidgetItem:
    widget = QTreeWidgetItem([key])
    widget.setText(0, key)
    widget.setData(0, Qt.UserRole, val)
    return widget

def add_menu_heading(menu, text):
    label = QLabel(text)
    label.setStyleSheet("""
        font-weight:bold;
        padding: 4px 12px;
    """)
    action = QWidgetAction(menu)
    action.setDefaultWidget(label)
    menu.addAction(action)
    menu.addSeparator()

#IDK where the fuck to put this??? constants maybe?
def get_main_window():
    app = QApplication.instance()
    for widget in app.topLevelWidgets():
        if isinstance(widget, QMainWindow):
            return widget
