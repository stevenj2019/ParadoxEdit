from PyQt5.QtWidgets import QMenu
from PyQt5.QtCore import Qt
from gui.interactions.utility import is_leaf
def connect_mod_panel_events(main_window):
    tree = main_window.left_panel.tree

    #this is so rigid, that it crahes on descriptor
    #also when i load a dict in, it just posts the filenames rather than the actual objects, annoyingly (i think im loading it in the wrong place....)
    def on_tree_click(item, column):
        if is_leaf(item):
            # obj = main_window.mod.categories[key] if key in main_window.mod_categories.keys() else None
            print("KEY:", item.text(0))
            obj = main_window.mod.categories[item.text(0)]
            if obj:
                # assign it to right panel
                obj._organise()
                main_window.right_panel.load_block(obj.category_data)

    tree.itemClicked.connect(on_tree_click)

    # treeSetContextMenuPolicy(Qt.CustomContextMenu)