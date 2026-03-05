from PyQt5.QtWidgets import QMainWindow, QTreeWidgetItem
from PyQt5.QtCore import Qt
from ParadoxParser import ParadoxScriptParser as PDXFile
from ModClasses.ParadoxCategory import GenericCategory
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

def apply_to_all_files(category: GenericCategory, func, *args, **kwargs):
    """
    Applies func to every file in the category.
    func should accept a file as its first argument, additional args/kwargs optional.
    """
    for file in category.files:
        func(file, *args, **kwargs)

def save_file(parent:QMainWindow, file:PDXFile):
    file.file_saved = True
    if parent.safe_mode:
        file._backup_file()
    file._to_pdx_script_file() #change to ._to_pdx_file() when i fix ParadoxParser token:var issue