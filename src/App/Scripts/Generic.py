from ParadoxParser import ParadoxScriptParser as PDXScriptFile
from ParadoxParser.ParadoxNodes import GenericBlock, GenericComment

from App.Enums import ChangeState
#OLD AND BAD
# def clear_comments(file, app_controller):
#     def remove_comments(node):
#         if isinstance(node, GenericBlock):
#             node.children = [c for c in node.children if not isinstance(c, GenericComment)]
#     script = file.obj
#     script.nodes = [node for node in script.nodes if not isinstance(node, GenericComment)]
#     for root in script.nodes:
#         if isinstance(root, GenericBlock):
#             root.traverse(remove_comments)

def clear_comments(file, app_controller):
    def tombstone_comments(node):
        if isinstance(node, GenericBlock):
            for child in node.nodes:
                tombstone_comments(child)
        if isinstance(node, GenericComment):
            app_controller.file_system.changed_file(file, node, ChangeState.DELETED)
    for node in file.nodes:
        tombstone_comments(node)

def clear_whitespace(file, app_controller):
    app_controller.file_system.change_tracker.set_file_state(file, ChangeState.MODIFIED)


