
from App.Enums import ChangeState
from App.Contracts import BlockMutationRequest
from App.GUI.Menus import Action
from App.Contexts.FileActions import ParadoxFileActions
from App.PDXFactory.Blocks.Generic import comment_node
from App.PDXFactory.Blocks import Generic, Events
#dumb temporary bullshit
def dummy():
    return 

###       ###
#  GENERIC  #
###       ###
class GenericNodeActions:
    @staticmethod
    def node_actions(app_controller, node, node_index):
        return [
            *ParadoxFileActions.node_actions(app_controller, node, node_index),
        ]
    
###          ###
#  PRE-BUILTS  #
###          ###
class EffectsContext:
    @staticmethod
    def node_actions(app_controller, node, node_index):
        return [
            *ParadoxFileActions.node_actions(app_controller, node, node_index),
           Action("EffectsContext", dummy(), False)
        ]

class TriggersContext:
    @staticmethod
    def node_actions(app_controller, node, node_index):
        return [
            *ParadoxFileActions.node_actions(app_controller, node, node_index),
            Action("TriggersContext", dummy(), False)
        ]
    
###      ###
#  EVENTS  #
###      ###
class EventBlockActions:
    @staticmethod
    def node_actions(app_controller, node, node_index):
        return [
            *ParadoxFileActions.node_actions(app_controller, node, node_index),
            Action("Add Immediate Block", dummy, False)
        ]
    
class EventOptionContext:
    @staticmethod
    def node_actions(app_controller, node, node_index):
        return [
            *ParadoxFileActions.node_actions(app_controller, node, node_index),
            # *TriggersContext.node_actions(ctx), 
            # *EffectsContext.node_actions(ctx),
        ]
