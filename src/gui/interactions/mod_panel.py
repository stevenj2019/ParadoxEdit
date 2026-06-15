from PyQt5.QtWidgets import QMenu
from PyQt5.QtCore import Qt
from ModClasses.ParadoxCategory import EventCategory, GenericCategory
from ParadoxParser import ParadoxScriptParser
from .context_menu import build_context_menu
from gui import util
def connect_mod_panel_events(main_window):
    tree = main_window.left_panel.tree

    def on_tree_click(item, column):
        if item.childCount()==0:
            obj = item.data(0, Qt.UserRole)
            if obj:
                # if not isinstance(obj, ParadoxScriptParser):
                    # obj._organise()
                main_window.right_panel.load_block(obj)

    def on_tree_right_click(position):
        item = tree.itemAt(position)
        if not item:
            return 

        obj = item.data(0, Qt.UserRole)
        if not obj:
            return 
        build_context_menu(main_window, obj)

    #left click event
    tree.itemClicked.connect(on_tree_click)

    #right click event
    tree.setContextMenuPolicy(Qt.CustomContextMenu)
    tree.customContextMenuRequested.connect(on_tree_right_click)