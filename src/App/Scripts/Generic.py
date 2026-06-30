from ParadoxParser import ParadoxScriptParser as PDXScriptFile
from ParadoxParser.ParadoxNodes import GenericBlock, GenericComment

from App.Enums import ChangeState

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


