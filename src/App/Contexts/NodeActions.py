from App.Enums import ChangeState
from App.Contracts import BlockMutationRequest
from App.GUI.Menus import Action
from App.Contexts.FileActions import ParadoxFileActions
from App.PDXFactory.Blocks.Generic import comment_node
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
            Action("Add Comment", 
                   lambda:app_controller.request_block_mutation.emit(BlockMutationRequest(  file=None,
                                                                                            target=selected,
                                                                                            value=comment_node,
                                                                                            state=ChangeState.ADDED)),
                    False
            )
        ]
    
###          ###
#  PRE-BUILTS  #
###          ###
class EffectsContext:
    @staticmethod
    def node_actions(ctx:CurrentContext):
        return [
           Action("EffectsContext", dummy(), False)
        ]
    
class TriggersContext:
    @staticmethod
    def node_actions(ctx:CurrentContext):
        return [
            Action("TriggersContext", dummy(), False)
        ]
    
###      ###
#  EVENTS  #
###      ###
class EventBlockActions:
    @staticmethod
    def node_actions(ctx:CurrentContext):
        return [
            # *ParadoxFileActions.node_actions(ctx), 
            Action("EventBlockActions", dummy, False)
            # Action("Add Immediate Block", dummy(), False),
            # Action("Add Option Block", dummy(), False)
        ]
    
class EventOptionContext:
    @staticmethod
    def node_actions(ctx:CurrentContext):
        return [
            *ParadoxFileActions.node_actions(ctx),
            *TriggersContext.node_actions(ctx), 
            *EffectsContext.node_actions(ctx),
        ]
