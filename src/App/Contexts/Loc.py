from App.Contexts.Base import (ParadoxContext, 
                              ParadoxFileContext, ParadoxNodeContext)
from App.Contracts import BulkMutationRequest
from App.GUI.Actions import Action
from App.Scripts.Localisation import convert_legacy

class LocalisationContext(ParadoxContext):
    @staticmethod
    def get_file_context():
        return LocalisationFileContext
    
    @staticmethod
    def get_block_context(node):
        return ParadoxNodeContext
    
    @staticmethod
    def get_node_context(parent_node, node):
        return ParadoxNodeContext
            
class LocalisationFileContext(ParadoxFileContext):
    @staticmethod
    def get_actions(app_controller, file):
        return [
            *ParadoxFileContext.get_actions(app_controller, file),
            Action("Convert to new format",
                   lambda:app_controller.request_bulk_mutation.emit(
                       BulkMutationRequest(target=file, action=convert_legacy)
                   ),
                   True
            )
        ]
