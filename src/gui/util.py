from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeWidgetItem, QLabel, QWidgetAction
from PyQt5.QtCore import Qt
import qdarktheme

from Configuration import ConfigurationFile
def clear_children(parent_item: QTreeWidgetItem):
    """
    Removes all child items of a given parent item in place.
    """
    for i in reversed(range(parent_item.childCount())):
        parent_item.removeChild(parent_item.child(i))

def build_category_list(key,val)->QTreeWidgetItem:
    widget = QTreeWidgetItem([key])
    widget.setText(0, key)
    widget.setData(0, Qt.UserRole, val)
    return widget

def get_safe_mode_opposed_text(parent:QMainWindow):
    return "Disable" if parent.safe_mode else "Enable"

def toggle_dark_mode(config:ConfigurationFile):
    config.change_setting(dark_mode = not(config.dark_mode))
    app = QApplication.instance()
    app.setStyleSheet(qdarktheme.load_stylesheet("dark" if config.dark_mode else "light"))

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

def get_app_instance():
    return QApplication.instance()

def get_main_window():
    app = QApplication.instance()
    for widget in app.topLevelWidgets():
        if isinstance(widget, QMainWindow):
            return widget