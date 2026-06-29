from ParadoxParser import ParadoxScriptParser as PDXScriptFile
from ParadoxParser.ParadoxNodes import GenericBlock, GenericComment

def clear_comments(file):
    def remove_comments(node):
        if isinstance(node, GenericBlock):
            node.children = [c for c in node.children if not isinstance(c, GenericComment)]
    script = file.obj
    script.nodes = [node for node in script.nodes if not isinstance(node, GenericComment)]
    for root in script.nodes:
        if isinstance(root, GenericBlock):
            root.traverse(remove_comments)
            
def clear_whitespace(file:PDXScriptFile):
    pass

