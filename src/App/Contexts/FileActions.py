from App.Enums import ChangeState
from App.Contracts import BlockMutationRequest
from App.GUI.Menus import Action
from App.PDXFactory.Blocks import Generic, Sprites, Events
#dumb temporary bullshit

def dummy():
    return 
class ParadoxFileActions:
    @staticmethod
    def file_actions(app_controller, selected):
        return [
            Action("Remove Comments", dummy(), False)
        ]
    @staticmethod
    def node_actions(app_controller, selected):
        return [
            Action("Add Comment", 
                   lambda:app_controller.request_block_mutation.emit(
                       BlockMutationRequest.add(selected, Generic.comment_node)
                   ), 
                   True
            )
        ]

class EventFileActions(ParadoxFileActions):
    @staticmethod
    def file_actions(app_controller, selected):
        return [
            *ParadoxFileActions.node_actions(app_controller, selected),
            # Action("Inject Event Logs", dummy(), False)
        ]
    @staticmethod
    def node_actions(app_controller, selected):
        return [
            *ParadoxFileActions.node_actions(app_controller, selected),
            Action("Add Namespace", 
                   lambda:app_controller.request_block_mutation.emit(
                       BlockMutationRequest.add(selected, Events.add_namespace_keyval)
                   ), 
                   True
            ),
            Action("Add Country Event",
                   lambda:app_controller.request_block_mutation.emit(
                       BlockMutationRequest.add(selected, Events.country_event_block)
                   ),
                   True
            ),
            Action("Add News Event",
                   lambda:app_controller.request_block_mutation.emit(
                       BlockMutationRequest.add(selected, Events.news_event_block)
                   ),
                   True
            )
        ]
    
class GFXFileActions(ParadoxFileActions):
    @staticmethod
    def file_actions(app_controller, selected):
        return [
            *ParadoxFileActions.node_actions(app_controller, selected),
            #Action()
        ]
    @staticmethod
    def node_actions(app_controller, selected):
        return [
            *ParadoxFileActions.node_actions(app_controller, selected),
            Action("Add Static Sprite",
                   lambda:app_controller.request_block_mutation.emit(
                       BlockMutationRequest.add(selected, Sprites.GFX_icon)
                   ), True
            ),
            Action("Add Focus _shine Sprite",
                   lambda:app_controller.request_block_mutation.emit(
                       BlockMutationRequest.add(selected, Sprites.GFX_shine_icon)
                   ), True
            )
       ]
    