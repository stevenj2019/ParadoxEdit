from PyQt5.QtWidgets import QMenu
from PyQt5.QtCore import Qt
from gui.interactions.utility import is_leaf
from ModClasses.ParadoxCategory import EventCategory, GenericCategory
from ParadoxParser import ParadoxScriptParser
from gui.interactions.context_menus import event_file_context
from gui import util
def connect_mod_panel_events(main_window):
    tree = main_window.left_panel.tree

    def on_tree_click(item, column):
        if is_leaf(item):
            obj = item.data(0, Qt.UserRole)
            if obj:
                if not isinstance(obj, ParadoxScriptParser):
                    obj._organise()
                main_window.right_panel.load_block(obj)

    def on_tree_right_click(position):
        item = tree.itemAt(position)
        if not item:
            return 

        obj = item.data(0, Qt.UserRole)
        if not obj:
            return 
        event_file_context(main_window, item, obj)

    #left click event
    tree.itemClicked.connect(on_tree_click)

    #right click event
    tree.setContextMenuPolicy(Qt.CustomContextMenu)
    tree.customContextMenuRequested.connect(on_tree_right_click)