from ParadoxParser import ParadoxScriptParser as PDXFile
from ParadoxParser.ParadoxNodes import GenericBlock, GenericComment
from PyQt5.QtWidgets import QMainWindow

def clear_comments(file:PDXFile):
    def remove_comments(node):
        if isinstance(node, GenericBlock):
            node.children = [c for c in node.children if not isinstance(c, GenericComment)]

    file.nodes = [node for node in file.nodes if not isinstance(node, GenericComment)]
    for root in file.nodes:
        if isinstance(root, GenericBlock):
            root.traverse(remove_comments)
            
def clear_whitespace(file:PDXFile):
    pass

def save_file(parent, file:PDXFile):
    file.file_saved = True
    if parent.safe_mode:
        file._backup_file()
    file._to_pdx_script_file() #change to ._to_pdx_file() when i fix ParadoxParser token:var issue