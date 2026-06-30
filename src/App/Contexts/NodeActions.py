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
    def node_actions(app_controller, selected):
        return [
            *ParadoxFileActions.node_actions(app_controller, selected),
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
