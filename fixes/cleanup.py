from ParadoxParser import ParadoxScriptParser as PDXFile
from ParadoxParser.ParadoxNodes import GenericBlock, GenericComment
from PyQt5.QtWidgets import QMainWindow

def clear_comments(parent:QMainWindow, file:PDXFile):
    file.file_saved = False
    parent.been_modified = True
    def remove_comments(node):
        if isinstance(node, GenericBlock):
            node.children = [c for c in node.children if not isinstance(c, GenericComment)]

    file.nodes = [node for node in file.nodes if not isinstance(node, GenericComment)]
    for root in file.nodes:
        if isinstance(root, GenericBlock):
            root.traverse(remove_comments)
            