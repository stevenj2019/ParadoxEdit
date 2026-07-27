from App.Enums import PDXMetadata
from App.Contracts import BulkMutationRequest, BlockMutationRequest
from App.GUI.Actions import Action
from App.GUI.Forms.LocaliseKey import LocaliseNodeForm
from App.PDXFactory.Blocks.Generic import comment_node
from App.Scripts.Generic import clear_comments, clear_whitespace

#TODO need to make sure Vanilla files cannot be modified by ANY contexts.
def dummy(): return

class ParadoxContext:
    @staticmethod
    def get_file_context():
        return ParadoxFileContext
    
    @staticmethod
    def get_block_context(node):
        return ParadoxBlockContext

    @staticmethod
    def get_node_context(node):
        return ParadoxNodeContext

class ParadoxFileContext:
    @staticmethod
    def get_actions(app_controller, file):
        return [
            Action("Remove Comments", 
                   lambda:app_controller.request_bulk_mutation.emit(
                       BulkMutationRequest(target=file, action=clear_comments)
                   ),
                   True
            ),
            Action("Reformat File", 
                   lambda:app_controller.request_bulk_mutation.emit(
                       BulkMutationRequest(target=file, action=clear_whitespace)
                   ),
                   True
            )
        ]

class ParadoxBlockContext:
    @staticmethod
    def get_actions(app_controller, block_context):
        return
    
    def errors(app_controller, node_context):
        return
    
class ParadoxNodeContext:
    @staticmethod
    def get_actions(app_controller, block_context):
        return [
            Action("Add Comment", 
                   lambda:app_controller.request_block_mutation.emit(
                       BlockMutationRequest.add(block_context.parent, block_context.parent_index, comment_node)
                   ), 
                   True
            )
        ]
    
    def errors(app_controller, node_context):
        return

class ReadOnlyContext(ParadoxContext):
    @staticmethod
    def get_file_context():
        return NullContext
    
    @staticmethod
    def get_block_context(node):
        return NullContext

    @staticmethod
    def get_node_context(node):
        return NullContext
    
class NullContext:
    @staticmethod
    def get_actions(app_controller, block_context):
        return [
            Action("No Actions Available", dummy, False)
        ]
    
    def errors(app_controller, node_context):
        return
    
class LocalisationFieldContext:
    @staticmethod
    def get_actions(app_controller, node_context):
        return [
            Action("Localise", 
                   lambda:LocaliseNodeForm(app_controller, node_context.node.value.value), 
                   True)
        ]
    
    def errors(app_controller, node):
        if not node.value in app_controller.registry.get_metadata(PDXMetadata.LocKey).keys():
            return "Localisation does not exist"
    
class GFXFieldContext:
    @staticmethod
    def get_actions(app_controller, node_context):
        return [
            Action("Preview Icon", 
                   lambda:app_controller.main.request_icon_preview.emit(node_context.node.value),
                   True)
        ]
    
    def errors(app_controller, node):
        if not node.value in app_controller.registry.get_metadata(PDXMetadata.GFXIcon).keys():
            return "Icon does not exist"
        else:
            return