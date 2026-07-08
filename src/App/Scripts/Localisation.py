from ParadoxParser.ParadoxNodes import GenericLegacyLocKey, GenericLocKey

from App.Enums import ChangeState

def convert_legacy(file, app_controller):
    node_changes = dict()
    for index, node in enumerate(file.nodes):
        if isinstance(node, GenericLegacyLocKey):
            node_changes[index] = GenericLocKey(node.key, node.value)
        
    for index, new_node in node_changes.items():
        file.nodes[index] = new_node
        app_controller.file_system.changed_file(file, new_node, ChangeState.MODIFIED)