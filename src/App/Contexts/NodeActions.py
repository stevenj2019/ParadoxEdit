
from App.Enums import ChangeState
from App.Contracts import BlockMutationRequest
from App.GUI.Menus import Action
from App.Contexts.FileActions import ParadoxFileActions
from App.PDXFactory.Blocks.Generic import comment_node
from App.PDXFactory.Blocks.Events import immediate_block, option_block
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

class EffectBlockActions:
    @staticmethod
    def node_actions(app_controller, node, node_index):
        return [
            *ParadoxFileActions.node_actions(app_controller, node, node_index),
           Action("EffectBlockActions", dummy, False)
        ]

class TriggerBlockActions:
    @staticmethod
    def node_actions(app_controller, node, node_index):
        return [
            *ParadoxFileActions.node_actions(app_controller, node, node_index),
            Action("TriggerBlockActions", dummy, False)
        ]
    
###      ###
#  EVENTS  #
###      ###

class EventBlockActions:
    @staticmethod
    def node_actions(app_controller, node, node_index):
        return [
            *ParadoxFileActions.node_actions(app_controller, node, node_index),
            # Action("Add Immediate Block", immediate_block, False)
            Action("Add Immediate Block",
                   lambda:app_controller.request_block_mutation.emit(
                       BlockMutationRequest.add(node, node_index, immediate_block)
                   ),
                   True
            ),
            Action("Add Option Block",
                   lambda:app_controller.request_block_mutation.emit(
                       BlockMutationRequest.add(node, node_index, option_block)
                   ),
                   True
            )
        ]
    
class EventOptionContext:
    @staticmethod
    def node_actions(app_controller, node, node_index):
        return [
            *ParadoxFileActions.node_actions(app_controller, node, node_index),
            # *TriggerBlockActions.node_actions(ctx), 
            # *EventBlockActions.node_actions(ctx),
        ]
