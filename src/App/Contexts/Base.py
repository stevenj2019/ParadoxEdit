from __future__ import annotations


from App.Enums import PDXMetadata
from App.Services import AppLogger
from App.Contracts import BulkMutationRequest, BlockMutationRequest
# from App.Loading.ParadoxSource import ParadoxVanilla
from App.GUI.Actions import Action
from App.GUI.Forms.LocaliseKey import LocaliseNodeForm
from App.PDXFactory.Blocks.Generic import comment_node
from App.Scripts.Generic import clear_comments, clear_whitespace

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

class NotImplementedContext(ParadoxContext):
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
                #    not isinstance(file, ParadoxVanilla)
            ),
            Action("Remove Whitespace", 
                   lambda:app_controller.request_bulk_mutation.emit(
                       BulkMutationRequest(target=file, action=clear_whitespace)
                   ),
                   True
                #    not isinstance(file, ParadoxVanilla)
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