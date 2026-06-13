from PyQt5.Qt import QMainWindow, QMenu, QTreeWidget
from PyQt5.QtGui import QCursor
from ModClasses.ParadoxCategory import EventCategory, GenericCategory
from gui.util import (clear_children, build_category_list, get_safe_mode_opposed_text, 
                      apply_to_all_files, save_file)
from ParadoxParser import ParadoxScriptParser as PDXFile
from fixes.cleanup import clear_comments
from gui.widgets import edit_warning_if_clean, toggle_safe_mode_warning

def global_options(parent:QMainWindow, menu:QMenu):
    menu.addAction(f"{get_safe_mode_opposed_text(parent)} safe mode", lambda: toggle_safe_mode_warning(parent))

def category_generic_fixes(parent:QMainWindow, menu:QMenu, category:GenericCategory):
    menu.addAction("Clean/Save Categories", edit_warning_if_clean(parent, lambda: apply_to_all_files(category, save_file, parent)))
    menu.addAction("Clear Comments", edit_warning_if_clean(parent, lambda: apply_to_all_files(category, clear_comments)))

def file_generic_fixes(parent:QMainWindow, menu:QMenu, file:PDXFile):
    menu.addAction("Clean/Save File", edit_warning_if_clean(parent, lambda: save_file(parent, file)))
    menu.addAction("Clear Comments From Section", edit_warning_if_clean(parent, lambda: clear_comments(file)))

def event_category_fixes(menu:QMenu, category:GenericCategory):
    menu.addAction("Inject Log Lines into effect blocks")

def event_file_fixes(menu:QMenu, file:PDXFile):
    return

def event_file_context(parent:QMainWindow, tree_item:QTreeWidget, obj:EventCategory|PDXFile):
    menu = QMenu(parent)
    menu.addSection("Global Options")
    global_options(parent, menu)
    # menu.addSeperator()
    menu.addSection(f"{obj.__class__.__name__} Options")
    #category/file arbitration
    if isinstance(obj, GenericCategory):
        category_generic_fixes(parent, menu, obj)
        # menu.addAction("Inject logs into all events", )
    elif isinstance(obj, PDXFile):
        file_generic_fixes(parent, menu, obj)
    # menu.addSeperator()
    menu.addSection("Event Options")
    # menu.addAction("Logger Injection")
    # menu.exec_(parent.mapToGlobal(parent.cursor().pos()))
    menu.exec_(QCursor.pos())