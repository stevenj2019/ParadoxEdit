from App.Enums import ChangeState
from App.Contracts import BlockMutationRequest
from App.GUI.Menus import Action
from App.Contexts.FileActions import ParadoxFileActions
from App.PDXFactory.Blocks.Generic import comment_node
from App.PDXFactory.Blocks import Generic, Events
#dumb temporary bullshit
class CurrentContext:
    def __init__():
        pass
def dummy():
    return 

###       ###
#  GENERIC  #
###       ###
class GenericNodeActions:
    @staticmethod
    def node_actions(app_controller, selected):
        return [
            *ParadoxFileActions.node_actions(app_controller, selected),
            # Action("Add Comment", 
            #        lambda:app_controller.request_block_mutation.emit(BlockMutationRequest(  file=None,
            #                                                                                 target=selected,
            #                                                                                 value=Generic.comment_node,
            #                                                                                 state=ChangeState.ADDED)),
            #         False
            # )
        ]
    
###          ###
#  PRE-BUILTS  #
###          ###
class EffectsContext:
    @staticmethod
    def node_actions(app_controller, selected):
        return [
            *ParadoxFileActions.node_actions(app_controller, selected),
           Action("EffectsContext", dummy(), False)
        ]
    
class TriggersContext:
    @staticmethod
    def node_actions(app_controller, selected):
        return [
            *ParadoxFileActions.node_actions(app_controller, selected),
            Action("TriggersContext", dummy(), False)
        ]
    
###      ###
#  EVENTS  #
###      ###
class EventBlockActions:
    @staticmethod
    def node_actions(app_controller, selected):
        return [
            *ParadoxFileActions.node_actions(app_controller, selected),
            Action("Add Immediate Block", dummy, False)
        ]
    
class EventOptionContext:
    @staticmethod
    def node_actions(app_controller, selected):
        return [
            *ParadoxFileActions.node_actions(app_controller, selected),
            # *TriggersContext.node_actions(ctx), 
            # *EffectsContext.node_actions(ctx),
        ]
