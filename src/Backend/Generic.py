from PyQt5.QtWidgets import QApplication
from ParadoxParser import ParadoxScriptParser as PDXFile
from ParadoxParser.ParadoxNodes import GenericBlock, GenericComment
from gui.util import get_main_winow

# def clear_comments(file:GenericCategoryItem):
def clear_comments(file):
    def remove_comments(node):
        if isinstance(node, GenericBlock):
            node.children = [c for c in node.children if not isinstance(c, GenericComment)]
    script = file.obj
    script.nodes = [node for node in script.nodes if not isinstance(node, GenericComment)]
    for root in script.nodes:
        if isinstance(root, GenericBlock):
            root.traverse(remove_comments)
            
def clear_whitespace(file:PDXFile):
    pass

# def save_all_files_in_category(category:GenericCategory):
def save_all_files_in_category(category):
    for file in category:
        if file.has_been_modified:
            save_file(file)

# def save_file(file:GenericCategoryItem):
def save_file(file):
    file.has_been_modified = False
    parent = get_main_winow()
    if parent.safe_mode:
        file.obj._backup_file()
    file.obj._to_pdx_file()
