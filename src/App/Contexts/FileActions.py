from App.Enums import ChangeState
from App.Contracts import BlockMutationRequest, BulkMutationRequest
from App.GUI.Menus import Action

from ParadoxParser import ParadoxScriptParser as PDXFile
from App.GUI.Forms.AddGFX import AddNewGFXForm
from App.PDXFactory.Blocks.Generic import comment_node
from App.PDXFactory.Blocks.Events import add_namespace_keyval, country_event_block, news_event_block
from App.PDXFactory.Blocks.Sprites import GFX_icon, GFX_shine_icon
from App.Scripts.Generic import clear_comments, clear_whitespace

class ParadoxFileActions:
    @staticmethod
    def file_actions(app_controller, file):
        return [
            Action("Remove Comments", 
                   lambda:app_controller.request_bulk_mutation.emit(
                       BulkMutationRequest(target=file, action=clear_comments)
                   ),
                   True
            ),
            Action("Remove Whitespace", 
                   lambda:app_controller.request_bulk_mutation.emit(
                       BulkMutationRequest(target=file, action=clear_whitespace)
                   ),
                   True
            )
        ]
    @staticmethod
    def node_actions(app_controller, node, node_index):
        return [
            Action("Add Comment", 
                   lambda:app_controller.request_block_mutation.emit(
                       BlockMutationRequest.add(node, node_index, comment_node)
                   ), 
                   True
            )
        ]

class EventFileActions(ParadoxFileActions):
    @staticmethod
    def file_actions(app_controller, file):
        return [
            *ParadoxFileActions.file_actions(app_controller, file),
            # Action("Inject Event Logs", dummy(), False)
        ]
    @staticmethod
    def node_actions(app_controller, node, node_index):
        return [
            *ParadoxFileActions.node_actions(app_controller, node, node_index),
            Action("Add Namespace", 
                   lambda:app_controller.request_block_mutation.emit(
                       BlockMutationRequest.add(node, node_index, add_namespace_keyval)
                   ), 
                   True
            ),
            Action("Add Country Event",
                   lambda:app_controller.request_block_mutation.emit(
                       BlockMutationRequest.add(node, node_index, country_event_block)
                   ),
                   True
            ),
            Action("Add News Event",
                   lambda:app_controller.request_block_mutation.emit(
                       BlockMutationRequest.add(node, node_index, news_event_block)
                   ),
                   True
            )
        ]
    
class GFXFileActions(ParadoxFileActions):
    @staticmethod
    def file_actions(app_controller, file):
        return [
            *ParadoxFileActions.file_actions(app_controller, file),
            Action("Bulk-Upload Sprites",
                   lambda:AddNewGFXForm(app_controller, file),
                   isinstance(file, PDXFile))
        ]
    @staticmethod
    def node_actions(app_controller, node, node_index):
        return [
            *ParadoxFileActions.node_actions(app_controller, node, node_index),
            Action("Add Static Sprite",
                   lambda:app_controller.request_block_mutation.emit(
                       BlockMutationRequest.add(node, node_index, GFX_icon)
                   ), True
            ),
            Action("Add Focus _shine Sprite",
                   lambda:app_controller.request_block_mutation.emit(
                       BlockMutationRequest.add(node, node_index, GFX_shine_icon)
                   ), True
            )
       ]
    