import os

from ParadoxParser import ParadoxLocParser as PDXLocFile
from ParadoxParser.ParadoxNodes import GenericComment
from App.Modules.Base import (GenericCategory, ParadoxContext, 
                              ParadoxFileContext, ParadoxNodeContext)
from App.Contracts import BulkMutationRequest
from App.GUI.Actions import Action
from App.Scripts.Localisation import convert_legacy
###        ###
#  CATEGORY  #
###        ###
class LocalisationCategory(GenericCategory):
    def __init__(self, mod_path:os.PathLike):
        super().__init__(base=mod_path, 
                         paths=["localisation"], 
                         context=LocalisationContext,
                         parser=PDXLocFile)

    def _build_metadata(self):
        self.metadata = dict()
        for file in self.files.values():
            for node in file.nodes:
                if not isinstance(node, GenericComment):
                    self.metadata[node.key] = {"file":file, "node":node}

###        ###
#  CONTEXTS  #
###        ###
class LocalisationContext(ParadoxContext):
    @staticmethod
    def get_file_context():
        return LocalisationFileContext
    
    #this has no blocks, this should provide compatibility despite it
    @staticmethod
    def get_block_context(node):
        return ParadoxNodeContext
    
    #and due to inlineedit limits, also has no node actions
    @staticmethod
    def get_node_context(node):
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
